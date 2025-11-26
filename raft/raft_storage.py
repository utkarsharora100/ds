"""
MongoDB Storage Module for Raft Consensus Layer
Provides persistence for log entries, state machine, and node metadata.
Implements singleton pattern for single connection per node.
"""

import os
import threading
from typing import Dict, List, Optional, Any
from pymongo import MongoClient, ASCENDING, WriteConcern
from pymongo.errors import ConnectionFailure
import json


class RaftStorage:
    """
    Singleton MongoDB storage for a Raft node.
    Ensures exactly one connection per node.

    Collections:
    - raft_log: Log entries (index, term, key, json_value)
    - raft_state_machine: Key-value state machine
    - raft_metadata: Node metadata (currentTerm, votedFor, commitIndex, lastApplied)
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, connection_string: str = None, node_id: str = None):
        """Singleton pattern - ensures single connection per node."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, connection_string: str = None, node_id: str = None):
        """
        Initialize MongoDB connection for Raft persistence.

        Args:
            connection_string: MongoDB connection URL
            node_id: Unique node identifier (e.g., "node1")
        """
        if self._initialized:
            return

        if connection_string is None:
            connection_string = os.environ.get(
                "RAFT_MONGODB_URL",
                "mongodb://localhost:27017/"
            )

        self.node_id = node_id or os.environ.get("RAFT_NODE_ID", "unknown")
        self.connection_string = connection_string

        # Initialize MongoDB client with connection pooling
        # Using async writes (w=0) for better performance
        self.client = MongoClient(
            connection_string,
            maxPoolSize=10,
            minPoolSize=1,
            serverSelectionTimeoutMS=5000
        )

        # Database named after node for isolation
        self.db = self.client[f'raft_{self.node_id}']

        # Collections with async write concern (w=0 = fire-and-forget)
        async_write = WriteConcern(w=0)
        self.log_collection = self.db.get_collection('raft_log', write_concern=async_write)
        self.state_machine_collection = self.db.get_collection('raft_state_machine', write_concern=async_write)
        self.metadata_collection = self.db.get_collection('raft_metadata', write_concern=async_write)

        # Create indexes
        self._create_indexes()

        self._initialized = True
        print(f"[{self.node_id}] [RAFT_STORAGE] Connected to MongoDB: {connection_string}", flush=True)

    def _create_indexes(self):
        """Create indexes for efficient queries."""
        try:
            # Unique index on log entry index
            self.log_collection.create_index([("index", ASCENDING)], unique=True)

            # Unique index on state machine keys
            self.state_machine_collection.create_index([("key", ASCENDING)], unique=True)

            print(f"[{self.node_id}] [RAFT_STORAGE] Indexes created", flush=True)
        except Exception as e:
            print(f"[{self.node_id}] [RAFT_STORAGE] Index creation warning: {e}", flush=True)

    # ==================== LOG PERSISTENCE ====================

    def append_log_entry(self, entry: Dict) -> bool:
        """
        Persist a new log entry.

        Args:
            entry: Dict with keys: index, term, key, value

        Returns:
            True if successful
        """
        try:
            doc = {
                "index": entry["index"],
                "term": entry["term"],
                "key": entry.get("key", ""),
                "json_value": json.dumps(entry.get("value", {}))
            }
            self.log_collection.insert_one(doc)
            return True
        except Exception as e:
            print(f"[{self.node_id}] [RAFT_STORAGE] Error appending log: {e}", flush=True)
            return False

    def get_log_entry(self, index: int) -> Optional[Dict]:
        """Get a specific log entry by index."""
        doc = self.log_collection.find_one({"index": index}, {"_id": 0})
        if doc:
            return {
                "index": doc["index"],
                "term": doc["term"],
                "key": doc.get("key", ""),
                "value": json.loads(doc.get("json_value", "{}"))
            }
        return None

    def get_all_log_entries(self) -> List[Dict]:
        """Retrieve all log entries sorted by index."""
        docs = self.log_collection.find({}, {"_id": 0}).sort("index", ASCENDING)
        entries = []
        for doc in docs:
            entries.append({
                "index": doc["index"],
                "term": doc["term"],
                "key": doc.get("key", ""),
                "value": json.loads(doc.get("json_value", "{}"))
            })
        return entries

    def get_last_log_entry(self) -> Optional[Dict]:
        """Get the most recent log entry."""
        doc = self.log_collection.find_one(
            {}, {"_id": 0}, sort=[("index", -1)]
        )
        if doc:
            return {
                "index": doc["index"],
                "term": doc["term"],
                "key": doc.get("key", ""),
                "value": json.loads(doc.get("json_value", "{}"))
            }
        return None

    def truncate_log_from(self, from_index: int) -> int:
        """
        Delete all log entries starting from the given index.
        Used during log inconsistency resolution.

        Returns:
            Number of entries deleted
        """
        result = self.log_collection.delete_many({"index": {"$gte": from_index}})
        print(f"[{self.node_id}] [RAFT_STORAGE] Truncated {result.deleted_count} entries from index {from_index}", flush=True)
        return result.deleted_count

    def get_log_count(self) -> int:
        """Get total number of log entries."""
        return self.log_collection.count_documents({})

    # ==================== STATE MACHINE PERSISTENCE ====================

    def set_state_machine_value(self, key: str, value: Any) -> bool:
        """
        Set or update a key-value pair in the state machine.
        Uses upsert for idempotent updates.
        """
        try:
            self.state_machine_collection.update_one(
                {"key": key},
                {"$set": {"key": key, "value": json.dumps(value)}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[{self.node_id}] [RAFT_STORAGE] Error setting state machine: {e}", flush=True)
            return False

    def get_state_machine_value(self, key: str) -> Optional[Any]:
        """Get a value from the state machine."""
        doc = self.state_machine_collection.find_one({"key": key})
        if doc:
            return json.loads(doc.get("value", "null"))
        return None

    def get_all_state_machine(self) -> Dict[str, Any]:
        """Retrieve entire state machine as a dictionary."""
        docs = self.state_machine_collection.find({}, {"_id": 0})
        return {doc["key"]: json.loads(doc.get("value", "null")) for doc in docs}

    def clear_state_machine(self) -> int:
        """Clear all state machine entries (for testing)."""
        result = self.state_machine_collection.delete_many({})
        return result.deleted_count

    # ==================== METADATA PERSISTENCE ====================

    def save_metadata(self, term: int, voted_for: Optional[str],
                      commit_index: int, last_applied: int) -> bool:
        """
        Persist node metadata atomically.
        Uses upsert to ensure exactly one metadata document.
        """
        try:
            self.metadata_collection.update_one(
                {"_id": "node_metadata"},
                {"$set": {
                    "currentTerm": term,
                    "votedFor": voted_for,
                    "commitIndex": commit_index,
                    "lastApplied": last_applied
                }},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[{self.node_id}] [RAFT_STORAGE] Error saving metadata: {e}", flush=True)
            return False

    def load_metadata(self) -> Dict:
        """
        Load persisted metadata.
        Returns default values if no metadata exists.
        """
        doc = self.metadata_collection.find_one({"_id": "node_metadata"})
        if doc:
            return {
                "currentTerm": doc.get("currentTerm", 0),
                "votedFor": doc.get("votedFor"),
                "commitIndex": doc.get("commitIndex", 0),
                "lastApplied": doc.get("lastApplied", 0)
            }
        return {
            "currentTerm": 0,
            "votedFor": None,
            "commitIndex": 0,
            "lastApplied": 0
        }

    def update_term_and_vote(self, term: int, voted_for: Optional[str]) -> bool:
        """
        Update term and votedFor atomically.
        Called during elections and when receiving higher terms.
        """
        try:
            self.metadata_collection.update_one(
                {"_id": "node_metadata"},
                {"$set": {"currentTerm": term, "votedFor": voted_for}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[{self.node_id}] [RAFT_STORAGE] Error updating term/vote: {e}", flush=True)
            return False

    def update_commit_applied(self, commit_index: int, last_applied: int) -> bool:
        """Update commit_index and last_applied."""
        try:
            self.metadata_collection.update_one(
                {"_id": "node_metadata"},
                {"$set": {"commitIndex": commit_index, "lastApplied": last_applied}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[{self.node_id}] [RAFT_STORAGE] Error updating commit/applied: {e}", flush=True)
            return False

    # ==================== UTILITY METHODS ====================

    def is_connected(self) -> bool:
        """Check if MongoDB connection is healthy."""
        try:
            self.client.admin.command('ping')
            return True
        except ConnectionFailure:
            return False

    def clear_all(self) -> Dict[str, int]:
        """Clear all collections (for testing/reset)."""
        log_count = self.log_collection.delete_many({}).deleted_count
        sm_count = self.state_machine_collection.delete_many({}).deleted_count
        meta_count = self.metadata_collection.delete_many({}).deleted_count
        return {"log": log_count, "state_machine": sm_count, "metadata": meta_count}

    def close(self):
        """Close MongoDB connection."""
        if hasattr(self, 'client'):
            self.client.close()
            print(f"[{self.node_id}] [RAFT_STORAGE] Connection closed", flush=True)


def get_raft_storage(connection_string: str = None, node_id: str = None) -> RaftStorage:
    """Factory function to get singleton RaftStorage instance."""
    return RaftStorage(connection_string, node_id)
