import grpc
import threading
import time, json, os
import random
from concurrent import futures
from typing import Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

# Import Raft state and gRPC components
from .raft_state import RaftState
from proto import raft_pb2, raft_pb2_grpc

def get_sample_movies():
    """Returns a list of sample movies for populating the state machine."""
    return [
        ("Inception", "New York", 120),
        ("Inception", "Los Angeles", 100),
        ("The Dark Knight", "New York", 150),
        ("The Dark Knight", "Chicago", 80),
        ("Interstellar", "San Francisco", 90),
        ("Interstellar", "Boston", 110),
        ("Avengers Endgame", "New York", 200),
        ("Avengers Endgame", "Los Angeles", 180),
        ("Spider-Man", "Chicago", 100),
        ("Spider-Man", "Miami", 75),
        ("Joker", "New York", 85),
        ("Joker", "Seattle", 95),
        ("Parasite", "San Francisco", 70),
        ("Dune", "Los Angeles", 130),
        ("Oppenheimer", "New York", 160)
    ]

# ---------------------- Raft Node Server ----------------------
class RaftNode(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, node_id: str, peers: Dict[str, str]):
        self.node_id = node_id
        self.peers = peers
        self.state = RaftState(node_id, peers)
        
        # Start election timer
        self.state.start_election_timer()
        print(f"[{self.node_id}] Initialized as follower in term {self.state.current_term}")

        # --- STATE MACHINE ---
        self.state_machine: Dict[str, Any] = {
            "users": {"admin": "123", "utkarsh": "password123"},
            "movies": [],
            "bookings": []
        }
        self.commit_index = 0
        self.last_applied = 0

        # --- PERSISTENCE ---
        self.state_file = f"raft_state_{self.node_id}.json"
        self.load_state_from_disk()


    # ---------------------- gRPC Methods ----------------------
    def RequestVote(self, request, context):
        return self.state.handle_request_vote(request)

    def AppendEntries(self, request, context):
        response = self.state.handle_append_entries(request)
        if response.success:
            # Apply committed entries to the state machine
            if self.state.leader_commit > self.commit_index:
                self.commit_index = min(self.state.leader_commit, len(self.state.log) -1)
                self.apply_committed_entries()

            # If we receive a valid heartbeat, we are not the leader
            if self.state.state != "follower":
                print(f"[{self.node_id}] Demoted to follower.")
                self.state.become_follower(self.state.current_term)
                self.state.start_election_timer()
        return response

    # ---------------------- State Machine Logic ----------------------
    def apply_committed_entries(self):
        """Apply log entries from last_applied up to commit_index."""
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            log_entry = self.state.log[self.last_applied]
            self.apply_log_entry(log_entry)

    def apply_log_entry(self, log_entry: raft_pb2.LogEntry):
        """Apply a single log entry to the state machine."""
        try:
            command = json.loads(log_entry.json_value)
            cmd_type = command.get("type")
            print(f"[{self.node_id}] Applying command: {cmd_type}")

            if cmd_type == "add_movie":
                movie_id = f"{command['movie']}-{command['city']}"
                if not any(m['id'] == movie_id for m in self.state_machine["movies"]):
                    self.state_machine["movies"].append({
                        "id": movie_id,
                        "movie": command["movie"],
                        "city": command["city"],
                        "seats": command["seats"]
                    })

            elif cmd_type == "register_user":
                username = command["username"]
                if username not in self.state_machine["users"]:
                    self.state_machine["users"][username] = command["password"]

            elif cmd_type == "book_seat":
                movie_id = f"{command['movie']}-{command['city']}"
                for movie in self.state_machine["movies"]:
                    if movie['id'] == movie_id and movie['seats'] >= command['seats']:
                        movie['seats'] -= command['seats']
                        self.state_machine["bookings"].append({
                            "requestId": command["booking_id"],
                            "data": {
                                "user": command["user"],
                                "movie": command["movie"],
                                "city": command["city"],
                                "seats": command["seats"],
                                "timestamp": command["timestamp"]
                            }
                        })
                        break
            
            elif cmd_type == "clear_database":
                self.state_machine["movies"] = []
                self.state_machine["bookings"] = []

            elif cmd_type == "load_sample_data":
                self.state_machine["movies"] = []
                self.state_machine["bookings"] = []
                sample_movies = get_sample_movies()
                for movie, city, seats in sample_movies:
                    self.state_machine["movies"].append({
                        "id": f"{movie}-{city}",
                        "movie": movie, "city": city, "seats": seats
                    })

        except json.JSONDecodeError:
            print(f"[{self.node_id}] ERROR: Could not decode log entry: {log_entry.json_value}")

    # ---------------------- Persistence ----------------------
    def save_state_to_disk(self):
        """Persist the current state machine and Raft state to disk."""
        with open(self.state_file, 'w') as f:
            state_to_save = {
                "state_machine": self.state_machine,
                "current_term": self.state.current_term,
                "voted_for": self.state.voted_for,
                "log": [
                    {"index": e.index, "term": e.term, "json_value": e.json_value}
                    for e in self.state.log
                ]
            }
            json.dump(state_to_save, f)
        print(f"[{self.node_id}] State saved to {self.state_file}")

    def load_state_from_disk(self):
        """Load state from disk on startup."""
        if not os.path.exists(self.state_file):
            return
        try:
            with open(self.state_file, 'r') as f:
                loaded_state = json.load(f)
                self.state_machine = loaded_state.get("state_machine", self.state_machine)
                self.state.current_term = loaded_state.get("current_term", 0)
                self.state.voted_for = loaded_state.get("voted_for", None)
                
                log_entries = loaded_state.get("log", [])
                self.state.log = [
                    raft_pb2.LogEntry(
                        index=e["index"], term=e["term"], json_value=e["json_value"]
                    ) for e in log_entries
                ]
                
                # Apply all loaded log entries to rebuild state machine
                self.commit_index = len(self.state.log) - 1
                self.apply_committed_entries()

            print(f"[{self.node_id}] State loaded from {self.state_file}")
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"[{self.node_id}] Could not load state from disk, starting fresh.")


    # ---------------------- Leader-Specific Methods ----------------------
    def send_heartbeats(self):
        """Leader sends AppendEntries RPCs to all peers."""
        while self.state.state == "leader":
            # If we are not the leader, stop sending heartbeats
            if self.state.state != "leader":
                break

            # Apply any newly committed entries on the leader itself
            if self.state.commit_index > self.commit_index:
                self.commit_index = self.state.commit_index
                self.apply_committed_entries()

            time.sleep(self.state.heartbeat_interval)

    def _send_append_entries_to_peer(self, peer_id: str):
        """Helper to send AppendEntries to a single peer."""
        # This logic is now inside RaftState
        self.state.replicate_log_to_peer(peer_id)

    # ---------------------- Server Lifecycle ----------------------
    def serve(self, port: int):
        """Start gRPC and FastAPI servers."""
        # gRPC server
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        raft_pb2_grpc.add_RaftServiceServicer_to_server(self, self.grpc_server)
        self.grpc_server.add_insecure_port(f'[::]:{port}')
        self.grpc_server.start()
        
        # FastAPI server (runs in the main thread)
        app = create_fastapi_app(self)
        uvicorn.run(app, host="0.0.0.0", port=port)

    def stop(self):
        print(f"[{self.node_id}] Stopping server...")
        self.state.stop_election_timer()
        
        # Persist state on graceful shutdown
        self.save_state_to_disk()

        self.grpc_server.stop(0)


# ---------------------- FastAPI App Factory ----------------------
def create_fastapi_app(node: RaftNode):
    """Creates a FastAPI app with routes for the given Raft node."""
    app = FastAPI()

    # --- API for Application Server ---
    @app.post("/propose")
    async def propose_entry(request: Request):
        if node.state.state != "leader":
            return JSONResponse({"status": "failure", "message": "Not the leader"}, status_code=400)
        
        command = await request.json()
        cmd_type = command.get("type")

        # --- Validation Logic ---
        if cmd_type == "register_user":
            if command["username"] in node.state_machine["users"]:
                return JSONResponse({"status": "failure", "message": "Username already exists"})
        
        elif cmd_type == "add_movie":
            movie_id = f"{command['movie']}-{command['city']}"
            if any(m['id'] == movie_id for m in node.state_machine["movies"]):
                 return JSONResponse({"status": "failure", "message": "Movie already exists in this city"})

        elif cmd_type == "book_seat":
            movie_id = f"{command['movie']}-{command['city']}"
            movie_found = False
            for movie in node.state_machine["movies"]:
                if movie['id'] == movie_id:
                    movie_found = True
                    if movie['seats'] < command['seats']:
                        return JSONResponse({"status": "failure", "message": "Insufficient seats"})
                    break
            if not movie_found:
                return JSONResponse({"status": "failure", "message": "Movie not found"})

        # --- Propose to Raft Log ---
        new_log_entry = raft_pb2.LogEntry(
            term=node.state.current_term,
            index=len(node.state.log),
            json_value=json.dumps(command)
        )
        node.state.log.append(new_log_entry)
        print(f"[{node.node_id}] Proposed new entry: {command['type']}")

        # The entry will be committed and applied via heartbeats.
        # For simplicity, we return success optimistically.
        # A more robust implementation would wait for commit.
        response_data = {"status": "success"}
        if cmd_type == "book_seat":
            response_data["booking_id"] = command["booking_id"]
        if cmd_type == "clear_database":
            response_data["cleared"] = {
                "movies": len(node.state_machine["movies"]),
                "bookings": len(node.state_machine["bookings"])
            }
        if cmd_type == "load_sample_data":
            response_data["loaded"] = {"movies": len(get_sample_movies())}

        return JSONResponse(response_data)

    @app.get("/query/{key}")
    async def query_state(key: str):
        if node.state.state != "leader":
            return JSONResponse({"status": "failure", "message": "Not the leader"}, status_code=400)
        
        if key == "movies":
            # Format to match the old API response structure for client compatibility
            formatted_movies = [
                {"id": idx + 1, "data": movie} 
                for idx, movie in enumerate(node.state_machine.get("movies", []))
            ]
            return JSONResponse({"status": "success", "data": formatted_movies})

        if key == "bookings":
            # Add context for client-side filtering
            bookings_with_context = []
            for booking in node.state_machine.get("bookings", []):
                booking_copy = booking.copy()
                booking_copy["context"] = {
                    "username": booking["data"].get("user", "unknown")
                }
                bookings_with_context.append(booking_copy)
            return JSONResponse({"status": "success", "data": bookings_with_context})

        data = node.state_machine.get(key)
        if data is not None:
            return JSONResponse({"status": "success", "data": data})
        else:
            return JSONResponse({"status": "failure", "message": "Key not found"}, status_code=404)


    # --- Internal Raft Admin/Status API ---
    @app.get("/status")
    async def get_status():
        return {
            "node_id": node.node_id,
            "state": node.state.state,
            "term": node.state.current_term,
            "leader_id": node.state.leader_id,
            "commit_index": node.state.commit_index,
            "log_length": len(node.state.log)
        }

    @app.post("/trigger-election")
    async def trigger_election():
        print(f"[{node.node_id}] Manual election triggered via API.")
        node.state.start_election()
        return {"message": "Election manually triggered."}

    return app
