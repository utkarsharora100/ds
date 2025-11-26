"""
gRPC-based Raft Node Implementation
Implements leader election, heartbeats, and log replication using gRPC protocol.
"""

import threading
import random
import time
import grpc
from concurrent import futures
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from proto import raft_pb2, raft_pb2_grpc
from raft.raft_storage import get_raft_storage


class RaftNode(raft_pb2_grpc.RaftServiceServicer):
    """
    Raft consensus node using gRPC for inter-node communication.
    Implements: Leader Election, Heartbeats, Log Replication
    """

    def __init__(self, node_id: str, peers: dict, mongodb_url: str = None):
        """
        Initialize Raft node with MongoDB persistence.

        Args:
            node_id: Unique identifier for this node (e.g., "node1")
            peers: Dict of peer_id -> address (e.g., {"node2": "localhost:50052"})
            mongodb_url: MongoDB connection URL (optional, from env if not provided)
        """
        self.node_id = node_id
        self.peers = peers  # {node_id: "host:port"}
        self.running = True

        # Timing configuration (optimized for Docker)
        self.HEARTBEAT_INTERVAL = 0.05      # 50ms
        self.ELECTION_TIMEOUT_MIN = 0.5     # 500ms
        self.ELECTION_TIMEOUT_MAX = 1.0     # 1000ms
        self.RPC_TIMEOUT = 1.0              # 1 second for gRPC calls

        # Initialize timing state
        self.last_heartbeat_time = time.time()
        self._stop_heartbeat = False
        self._heartbeat_thread = None

        # Leader-only state (reinitialized after election)
        self.next_index = {}   # {peer_id: int}
        self.match_index = {}  # {peer_id: int}

        # DEADLOCK PREVENTION: Single lock pattern
        self.lock = threading.Lock()

        # gRPC stubs for peer communication (lazy initialization)
        self._stubs = {}

        # Initialize MongoDB storage (singleton pattern)
        self.storage = get_raft_storage(mongodb_url, node_id)

        # Crash recovery: restore state from MongoDB
        self._recover_from_storage()

        print(f"[{self.node_id}] Timing: heartbeat={self.HEARTBEAT_INTERVAL*1000}ms, "
              f"election={self.ELECTION_TIMEOUT_MIN*1000}-{self.ELECTION_TIMEOUT_MAX*1000}ms", flush=True)

        # Start background election timer thread
        self._election_thread = threading.Thread(target=self._run_election_timer, daemon=True)
        self._election_thread.start()

    def _recover_from_storage(self):
        """
        CRASH RECOVERY: Restore state from MongoDB on startup.
        Implements Raft's persistent state requirements.
        """
        print(f"[{self.node_id}] Starting crash recovery from MongoDB...", flush=True)

        # 1. Recover metadata (term, votedFor, commitIndex, lastApplied)
        metadata = self.storage.load_metadata()
        self.term = metadata["currentTerm"]
        self.voted_for = metadata["votedFor"]
        self.commit_index = metadata["commitIndex"]
        self.last_applied = metadata["lastApplied"]

        # Always start as follower after crash
        self.state = "follower"
        self.leader_id = None

        print(f"[{self.node_id}] Recovered metadata: term={self.term}, "
              f"votedFor={self.voted_for}, commitIndex={self.commit_index}, "
              f"lastApplied={self.last_applied}", flush=True)

        # 2. Recover log entries
        self.log = self.storage.get_all_log_entries()
        print(f"[{self.node_id}] Recovered {len(self.log)} log entries", flush=True)

        # 3. Recover state machine
        self.state_machine = self.storage.get_all_state_machine()
        print(f"[{self.node_id}] Recovered state machine with {len(self.state_machine)} keys", flush=True)

        # 4. Re-apply any entries between last_applied and commit_index
        # (Handles case where node crashed between commit and apply)
        if self.last_applied < self.commit_index:
            print(f"[{self.node_id}] Re-applying entries {self.last_applied+1} to {self.commit_index}", flush=True)
            while self.last_applied < self.commit_index:
                self.last_applied += 1
                if self.last_applied <= len(self.log):
                    entry = self.log[self.last_applied - 1]
                    key = entry.get("key", "")
                    value = entry.get("value", {})
                    self.state_machine[key] = value
                    self.storage.set_state_machine_value(key, value)
            self.storage.update_commit_applied(self.commit_index, self.last_applied)

        print(f"[{self.node_id}] Crash recovery complete", flush=True)

    def _get_stub(self, peer_id: str) -> raft_pb2_grpc.RaftServiceStub:
        """
        Get or create gRPC stub for a peer.
        Uses lazy initialization to avoid connecting to peers that are down.
        """
        if peer_id not in self._stubs:
            address = self.peers[peer_id]
            channel = grpc.insecure_channel(address)
            self._stubs[peer_id] = raft_pb2_grpc.RaftServiceStub(channel)
        return self._stubs[peer_id]

    def _get_last_log_index(self) -> int:
        """Get index of last log entry (0 if empty)."""
        return len(self.log)

    def _get_last_log_term(self) -> int:
        """Get term of last log entry (0 if empty)."""
        if self.log:
            return self.log[-1]["term"]
        return 0

    def _get_log_term(self, index: int) -> int:
        """Get term of log entry at given index (1-indexed). Returns 0 if not found."""
        if index <= 0 or index > len(self.log):
            return 0
        return self.log[index - 1]["term"]

    def _initialize_leader_state(self):
        """Initialize nextIndex and matchIndex after becoming leader."""
        last_log_index = self._get_last_log_index()
        for peer_id in self.peers:
            # Initialize nextIndex to leader's last log index + 1
            self.next_index[peer_id] = last_log_index + 1
            # Initialize matchIndex to 0
            self.match_index[peer_id] = 0
        print(f"[{self.node_id}] Initialized leader state: nextIndex={self.next_index}", flush=True)

    def _run_election_timer(self):
        """
        Background thread: monitors for leader heartbeats and starts election if timeout.
        FAULT TOLERANCE: Detects leader failure and triggers new election.
        """
        while self.running:
            if self.state == "leader":
                # Leaders don't run election timer
                time.sleep(0.1)
                continue

            time.sleep(0.1)  # Check every 100ms

            # CRITICAL SECTION: Check heartbeat timeout
            with self.lock:
                time_since_heartbeat = time.time() - self.last_heartbeat_time
                timeout = random.uniform(self.ELECTION_TIMEOUT_MIN, self.ELECTION_TIMEOUT_MAX)

            if time_since_heartbeat >= timeout:
                print(f"[{self.node_id}] Election timeout: no heartbeat for {time_since_heartbeat:.2f}s", flush=True)
                self._start_election()

    def _send_heartbeats_loop(self):
        """
        Leader continuously sends heartbeats to all followers via gRPC.
        LOG REPLICATION: Piggybacks log entries on heartbeats.
        FAULT TOLERANCE: Maintains leader authority and detects stale terms.
        """
        while self.state == "leader" and not self._stop_heartbeat:
            try:
                for peer_id in self.peers:
                    self._send_append_entries(peer_id)

                # Update commit index based on matchIndex
                self._update_commit_index()

                # Apply committed entries to state machine
                self._apply_committed_entries()

                time.sleep(self.HEARTBEAT_INTERVAL)

            except Exception as e:
                print(f"[{self.node_id}] Heartbeat loop error: {e}", flush=True)
                break

        print(f"[{self.node_id}] Stopped heartbeat loop", flush=True)

    def _send_append_entries(self, peer_id: str):
        """
        Send AppendEntries RPC to a single peer.
        Includes log entries starting from nextIndex[peer_id].
        """
        try:
            stub = self._get_stub(peer_id)

            with self.lock:
                # Get entries to send (from nextIndex to end of log)
                next_idx = self.next_index.get(peer_id, 1)
                prev_log_index = next_idx - 1
                prev_log_term = self._get_log_term(prev_log_index)

                # Build entries to send (convert to protobuf LogEntry)
                entries_to_send = []
                for i in range(next_idx - 1, len(self.log)):
                    entry = self.log[i]
                    entries_to_send.append(raft_pb2.LogEntry(
                        index=entry["index"],
                        term=entry["term"],
                        key=entry.get("key", ""),
                        json_value=json.dumps(entry.get("value", {}))
                    ))

                current_term = self.term
                current_commit = self.commit_index

            # Build AppendEntries request
            request = raft_pb2.AppendEntriesRequest(
                term=current_term,
                leader_id=self.node_id,
                prev_log_index=prev_log_index,
                prev_log_term=prev_log_term,
                entries=entries_to_send,  # PIGGYBACKED LOG ENTRIES
                leader_commit=current_commit
            )

            # gRPC call with timeout (DEADLOCK PREVENTION)
            response = stub.AppendEntries(request, timeout=self.RPC_TIMEOUT)

            # Handle response
            with self.lock:
                if response.term > self.term:
                    # Step down if peer has higher term
                    print(f"[{self.node_id}] Peer {peer_id} has higher term {response.term}, stepping down", flush=True)
                    self._step_down(response.term)
                    return

                if response.success:
                    # Update nextIndex and matchIndex for this peer
                    if entries_to_send:
                        self.next_index[peer_id] = next_idx + len(entries_to_send)
                        self.match_index[peer_id] = response.match_index
                        print(f"[{self.node_id}] Replicated {len(entries_to_send)} entries to {peer_id}, "
                              f"matchIndex={response.match_index}", flush=True)
                else:
                    # Decrement nextIndex and retry (log inconsistency)
                    self.next_index[peer_id] = max(1, self.next_index.get(peer_id, 1) - 1)
                    print(f"[{self.node_id}] AppendEntries rejected by {peer_id}, "
                          f"decremented nextIndex to {self.next_index[peer_id]}", flush=True)

        except grpc.RpcError:
            # Peer might be down, continue with others (FAULT TOLERANCE)
            pass

    def _update_commit_index(self):
        """
        Update commit_index based on matchIndex values.
        A log entry is committed if it's replicated on a majority of servers.
        """
        with self.lock:
            if self.state != "leader":
                return

            # For each index from commit_index+1 to last log index
            for n in range(self.commit_index + 1, len(self.log) + 1):
                # Count how many servers have this entry
                replicated_count = 1  # Leader has it

                for peer_id in self.peers:
                    if self.match_index.get(peer_id, 0) >= n:
                        replicated_count += 1

                # Check if majority and entry is from current term
                majority = (len(self.peers) + 1) // 2 + 1
                if replicated_count >= majority:
                    # Only commit entries from current term (Raft safety property)
                    if self._get_log_term(n) == self.term:
                        self.commit_index = n
                        print(f"[{self.node_id}] Committed entry {n} (replicated on {replicated_count} nodes)", flush=True)

    def _apply_committed_entries(self):
        """
        Apply committed log entries to the state machine with persistence.
        """
        with self.lock:
            while self.last_applied < self.commit_index:
                self.last_applied += 1
                entry = self.log[self.last_applied - 1]

                # Apply to state machine (simple key-value store)
                key = entry.get("key", "")
                value = entry.get("value", {})
                self.state_machine[key] = value

                # PERSIST: Write to MongoDB state machine
                self.storage.set_state_machine_value(key, value)

                print(f"[{self.node_id}] Applied and persisted entry {self.last_applied}: {key}={value}", flush=True)

            # PERSIST: Update commit_index and last_applied
            self.storage.update_commit_applied(self.commit_index, self.last_applied)

    def _start_election(self):
        """
        Start leader election process with persistence.
        FAULT TOLERANCE: Term-based voting prevents split-brain.
        DEADLOCK PREVENTION: Lock held only during state changes, not during RPC.
        """
        # CRITICAL SECTION: Update state atomically
        with self.lock:
            self.term += 1
            self.state = "candidate"
            self.voted_for = self.node_id
            current_term = self.term

            # PERSIST: Save term and vote before sending RPCs
            self.storage.update_term_and_vote(self.term, self.voted_for)

        print(f"[{self.node_id}] Starting election for term {current_term}", flush=True)

        # Vote for self
        votes = 1
        total_nodes = len(self.peers) + 1
        majority = total_nodes // 2 + 1

        # Request votes from peers via gRPC (OUTSIDE LOCK - prevents deadlock)
        for peer_id in self.peers:
            try:
                stub = self._get_stub(peer_id)

                request = raft_pb2.RequestVoteRequest(
                    term=current_term,
                    candidate_id=self.node_id,
                    last_log_index=self._get_last_log_index(),
                    last_log_term=self._get_last_log_term()
                )

                # gRPC call with timeout (DEADLOCK PREVENTION)
                response = stub.RequestVote(request, timeout=self.RPC_TIMEOUT)

                if response.vote_granted:
                    votes += 1
                    print(f"[{self.node_id}] Got vote from {peer_id}", flush=True)
                else:
                    print(f"[{self.node_id}] Vote denied by {peer_id} (term {response.term})", flush=True)

                    # Step down if peer has higher term
                    if response.term > current_term:
                        self._step_down(response.term)
                        return

            except grpc.RpcError as e:
                print(f"[{self.node_id}] Could not reach {peer_id}: {e.code()}", flush=True)

        # Check election result
        with self.lock:
            # Verify we're still candidate and term hasn't changed
            if self.state != "candidate" or self.term != current_term:
                print(f"[{self.node_id}] Election interrupted (state={self.state}, term={self.term})", flush=True)
                return

            if votes >= majority:
                self.state = "leader"
                self.leader_id = self.node_id
                print(f"[{self.node_id}] Became LEADER (term {self.term}, votes {votes}/{total_nodes})", flush=True)

                # Initialize leader state for log replication
                self._initialize_leader_state()

                # Start heartbeat loop
                self._stop_heartbeat = False
                self._heartbeat_thread = threading.Thread(target=self._send_heartbeats_loop, daemon=True)
                self._heartbeat_thread.start()
            else:
                self.state = "follower"
                print(f"[{self.node_id}] Election failed (term {self.term}, votes {votes}/{total_nodes})", flush=True)

    def _step_down(self, new_term: int):
        """
        Step down from leader/candidate to follower with persistence.
        FAULT TOLERANCE: Handles network partitions gracefully.
        """
        with self.lock:
            old_state = self.state
            self.state = "follower"
            self.term = new_term
            self.voted_for = None
            self.leader_id = None
            self.last_heartbeat_time = time.time()

            # PERSIST: Save new term and cleared vote
            self.storage.update_term_and_vote(new_term, None)

        # Stop heartbeat loop if we were leader
        if old_state == "leader":
            self._stop_heartbeat = True
            if self._heartbeat_thread:
                self._heartbeat_thread.join(timeout=1.0)  # DEADLOCK PREVENTION: timeout
            print(f"[{self.node_id}] Stepped down from leader to follower (term {new_term})", flush=True)
        elif old_state == "candidate":
            print(f"[{self.node_id}] Stepped down from candidate to follower (term {new_term})", flush=True)

    def RequestVote(self, request, context):
        """
        Handle vote request from candidate with persistence.
        gRPC endpoint: /raft.RaftService/RequestVote
        """
        candidate_term = request.term
        candidate_id = request.candidate_id

        with self.lock:
            # Update term if candidate has higher term
            if candidate_term > self.term:
                self.term = candidate_term
                self.voted_for = None
                # PERSIST: Update term
                self.storage.update_term_and_vote(candidate_term, None)
                if self.state in ["leader", "candidate"]:
                    old_state = self.state
                    self.state = "follower"
                    if old_state == "leader":
                        self._stop_heartbeat = True
                        print(f"[{self.node_id}] Stepping down from leader due to higher term {candidate_term}", flush=True)

            # Reject if term is outdated
            if candidate_term < self.term:
                print(f"[{self.node_id}] Rejected vote for {candidate_id} (stale term {candidate_term} < {self.term})", flush=True)
                return raft_pb2.RequestVoteResponse(vote_granted=False, term=self.term)

            # Check log is at least as up-to-date as candidate's
            # (Raft safety: only vote for candidates with up-to-date logs)
            my_last_term = self._get_last_log_term()
            my_last_index = self._get_last_log_index()

            log_ok = (request.last_log_term > my_last_term or
                      (request.last_log_term == my_last_term and request.last_log_index >= my_last_index))

            # Grant vote if haven't voted yet OR already voted for this candidate, AND log is ok
            if (self.voted_for is None or self.voted_for == candidate_id) and log_ok:
                self.voted_for = candidate_id
                self.last_heartbeat_time = time.time()  # Reset election timer
                # PERSIST: Save vote
                self.storage.update_term_and_vote(self.term, candidate_id)
                print(f"[{self.node_id}] Granted vote to {candidate_id} for term {candidate_term}", flush=True)
                return raft_pb2.RequestVoteResponse(vote_granted=True, term=self.term)
            else:
                reason = "already voted" if self.voted_for and self.voted_for != candidate_id else "log not up-to-date"
                print(f"[{self.node_id}] Denied vote to {candidate_id} ({reason})", flush=True)
                return raft_pb2.RequestVoteResponse(vote_granted=False, term=self.term)

    def AppendEntries(self, request, context):
        """
        Handle heartbeat/log replication from leader with persistence.
        gRPC endpoint: /raft.RaftService/AppendEntries
        LOG REPLICATION: Appends entries to local log.
        """
        leader_term = request.term
        leader_id = request.leader_id

        with self.lock:
            # Update term if higher
            if leader_term > self.term:
                self.term = leader_term
                self.voted_for = None
                self.state = "follower"
                self.leader_id = leader_id
                # PERSIST: Update term
                self.storage.update_term_and_vote(leader_term, None)

            # Reject if term is outdated
            if leader_term < self.term:
                return raft_pb2.AppendEntriesResponse(success=False, term=self.term, match_index=0)

            # Valid heartbeat received - reset election timer
            self.last_heartbeat_time = time.time()
            self.leader_id = leader_id

            # Step down if we were candidate
            if self.state == "candidate":
                self.state = "follower"
                print(f"[{self.node_id}] Stepped down from candidate (received heartbeat from {leader_id})", flush=True)

            # Log consistency check
            prev_log_index = request.prev_log_index
            prev_log_term = request.prev_log_term

            # Check if we have the entry at prev_log_index with matching term
            if prev_log_index > 0:
                if prev_log_index > len(self.log):
                    # We don't have entry at prev_log_index
                    print(f"[{self.node_id}] Log inconsistency: missing entry at index {prev_log_index}", flush=True)
                    return raft_pb2.AppendEntriesResponse(
                        success=False, term=self.term, match_index=len(self.log)
                    )

                if self._get_log_term(prev_log_index) != prev_log_term:
                    # Term mismatch - delete this entry and all following
                    print(f"[{self.node_id}] Log inconsistency: term mismatch at index {prev_log_index}", flush=True)
                    # PERSIST: Truncate from MongoDB first
                    self.storage.truncate_log_from(prev_log_index)
                    self.log = self.log[:prev_log_index - 1]
                    return raft_pb2.AppendEntriesResponse(
                        success=False, term=self.term, match_index=len(self.log)
                    )

            # Append new entries
            if request.entries:
                for entry in request.entries:
                    entry_index = entry.index

                    # If we already have this entry, check for conflict
                    if entry_index <= len(self.log):
                        if self._get_log_term(entry_index) != entry.term:
                            # Conflict: delete existing entry and all following
                            # PERSIST: Truncate from MongoDB first
                            self.storage.truncate_log_from(entry_index)
                            self.log = self.log[:entry_index - 1]
                        else:
                            # Already have this entry with same term, skip
                            continue

                    # Append new entry
                    new_entry = {
                        "index": entry.index,
                        "term": entry.term,
                        "key": entry.key,
                        "value": json.loads(entry.json_value) if entry.json_value else {}
                    }
                    self.log.append(new_entry)
                    # PERSIST: Write to MongoDB
                    self.storage.append_log_entry(new_entry)
                    print(f"[{self.node_id}] Appended and persisted log entry {entry.index}: {entry.key}", flush=True)

            # Update commit index
            if request.leader_commit > self.commit_index:
                self.commit_index = min(request.leader_commit, len(self.log))
                print(f"[{self.node_id}] Updated commit_index to {self.commit_index}", flush=True)

            # Apply committed entries with persistence
            while self.last_applied < self.commit_index:
                self.last_applied += 1
                entry = self.log[self.last_applied - 1]
                key = entry.get("key", "")
                value = entry.get("value", {})
                self.state_machine[key] = value
                # PERSIST: Write to MongoDB state machine
                self.storage.set_state_machine_value(key, value)
                print(f"[{self.node_id}] Applied and persisted entry {self.last_applied}: {key}={value}", flush=True)

            # PERSIST: Update commit_index and last_applied
            self.storage.update_commit_applied(self.commit_index, self.last_applied)

            return raft_pb2.AppendEntriesResponse(
                success=True,
                term=self.term,
                match_index=len(self.log)
            )

    def append_entry(self, key: str, value: dict) -> dict:
        """
        Client API: Append a new entry to the log (leader only) with persistence.

        Args:
            key: Entry key (e.g., "booking")
            value: Entry value as dict

        Returns:
            dict with status and info
        """
        with self.lock:
            if self.state != "leader":
                return {
                    "success": False,
                    "error": "Not leader",
                    "leader_id": self.leader_id
                }

            # Create new log entry
            new_index = len(self.log) + 1
            entry = {
                "index": new_index,
                "term": self.term,
                "key": key,
                "value": value
            }

            # PERSIST: Write to MongoDB first (write-ahead logging)
            if not self.storage.append_log_entry(entry):
                return {
                    "success": False,
                    "error": "Failed to persist log entry"
                }

            # Append to leader's log
            self.log.append(entry)
            print(f"[{self.node_id}] Leader appended and persisted entry {new_index}: {key}={value}", flush=True)

            return {
                "success": True,
                "index": new_index,
                "term": self.term
            }

    def get_status(self) -> dict:
        """Get current node status."""
        with self.lock:
            return {
                "node_id": self.node_id,
                "state": self.state,
                "term": self.term,
                "leader_id": self.leader_id,
                "peers": list(self.peers.keys()),
                "log_length": len(self.log),
                "commit_index": self.commit_index,
                "last_applied": self.last_applied,
                "next_index": dict(self.next_index) if self.state == "leader" else {},
                "match_index": dict(self.match_index) if self.state == "leader" else {}
            }

    def get_log(self) -> list:
        """Get current log entries."""
        with self.lock:
            return list(self.log)

    def get_state_machine(self) -> dict:
        """Get current state machine state."""
        with self.lock:
            return dict(self.state_machine)

    def _create_http_handler(self):
        """Create HTTP request handler with access to Raft node."""
        raft_node = self

        class RaftStatusHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Suppress HTTP logs

            def do_GET(self):
                if self.path == '/status':
                    status = raft_node.get_status()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(status).encode())
                elif self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "healthy", "node_id": raft_node.node_id}).encode())
                elif self.path == '/log':
                    log_entries = raft_node.get_log()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(log_entries).encode())
                elif self.path == '/state':
                    state_machine = raft_node.get_state_machine()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(state_machine).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

        return RaftStatusHandler

    def _start_http_server(self, http_port: int):
        """Start HTTP status server in background thread."""
        handler = self._create_http_handler()
        http_server = HTTPServer(('0.0.0.0', http_port), handler)
        print(f"[{self.node_id}] HTTP status server started on port {http_port}", flush=True)
        http_server.serve_forever()

    def serve(self, port: int, http_port: int = None):
        """
        Start gRPC server and HTTP status server.

        Args:
            port: gRPC port (50051, 50052, 50053)
            http_port: HTTP status port (defaults to gRPC port + 1000, e.g., 51051)
        """
        # Calculate HTTP port if not provided
        if http_port is None:
            http_port = port + 1000  # e.g., 50051 -> 51051

        # Start HTTP status server in background thread
        http_thread = threading.Thread(target=self._start_http_server, args=(http_port,), daemon=True)
        http_thread.start()

        # Start gRPC server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        raft_pb2_grpc.add_RaftServiceServicer_to_server(self, server)

        server.add_insecure_port(f'0.0.0.0:{port}')
        server.start()

        print(f"[{self.node_id}] gRPC Raft server started on port {port}", flush=True)

        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            self.running = False
            server.stop(0)
            print(f"[{self.node_id}] Server stopped", flush=True)

    def stop(self):
        """Stop the Raft node gracefully."""
        self.running = False
        self._stop_heartbeat = True
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=1.0)
