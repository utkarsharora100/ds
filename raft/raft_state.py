import random
import time
import threading
from proto import raft_pb2, raft_pb2_grpc
from llm.storage import append_log, get_all_logs, create_in_memory_db
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from llm import storage

class RaftNodeState:
    def __init__(self, node_id, peers, stub_dict):
        self.node_id = node_id
        self.peers = peers                # list of peer addresses
        self.stub_dict = stub_dict        # mapping {address: stub}

        self.current_term = 0
        self.voted_for = None
        self.log = []                     # in-memory log entries

        self.commit_index = 0
        self.last_applied = 0

        self.state = "follower"
        self.leader_id = None

        self.election_timeout = random.uniform(3, 5)
        self.last_heartbeat = time.time()
        
        # ✅ NEW: Initialize database on each RAFT node
        self.db = create_in_memory_db()
        print(f"[{node_id}] ✅ Database initialized on RAFT node")

        # Start background election thread
        threading.Thread(target=self.run_election_timer, daemon=True).start()

    def run_election_timer(self):
        """Election timer to trigger a new election if no heartbeat is received."""
        while True:
            time.sleep(0.1)
            if time.time() - self.last_heartbeat > self.election_timeout and self.state != "leader":
                print(f"[{self.node_id}] Election timeout — starting election.")
                self.start_election()

    def start_election(self):
        """Start election process."""
        self.current_term += 1
        self.voted_for = self.node_id
        self.state = "candidate"
        votes = 1  # voted for self

        for peer, stub in self.stub_dict.items():
            try:
                req = raft_pb2.VoteRequest(term=self.current_term, candidate_id=self.node_id)
                resp = stub.RequestVote(req)
                if resp.vote_granted:
                    votes += 1
            except Exception:
                pass

        if votes > len(self.peers) // 2:
            print(f"[{self.node_id}] Becomes LEADER (term {self.current_term})")
            self.state = "leader"
            self.leader_id = self.node_id
            threading.Thread(target=self.heartbeat_loop, daemon=True).start()
        else:
            self.state = "follower"

    def heartbeat_loop(self):
        """Leader sends periodic heartbeats."""
        while self.state == "leader":
            for peer, stub in self.stub_dict.items():
                try:
                    req = raft_pb2.AppendRequest(
                        term=self.current_term,
                        leader_id=self.node_id,
                        leader_commit=self.commit_index,
                    )
                    stub.AppendEntries(req)
                except Exception:
                    pass
            time.sleep(1)

    def handle_append_entries(self, request):
        """Follower receives heartbeats or log append requests."""
        self.last_heartbeat = time.time()
        if request.term >= self.current_term:
            self.current_term = request.term
            self.state = "follower"
            return raft_pb2.AppendResponse(term=self.current_term, success=True)
        return raft_pb2.AppendResponse(term=self.current_term, success=False)

    def handle_vote_request(self, request):
        """Follower decides whether to grant vote."""
        if request.term < self.current_term:
            return raft_pb2.VoteResponse(term=self.current_term, vote_granted=False)

        if self.voted_for is None or self.voted_for == request.candidate_id:
            self.voted_for = request.candidate_id
            self.current_term = request.term
            self.last_heartbeat = time.time()
            return raft_pb2.VoteResponse(term=self.current_term, vote_granted=True)

        return raft_pb2.VoteResponse(term=self.current_term, vote_granted=False)

    def handle_client_command(self, command):
        """Handle a client command (leader only)."""
        if self.state != "leader":
            return f"Not leader, redirect to {self.leader_id}"

        term = self.current_term
        self.log.append((term, command))
        append_log(term, command)  # save to SQLite

        print(f"[{self.node_id}] Log appended: {command}")
        return f"Command '{command}' committed (term {term})"
    
    # ✅ NEW: Database operation methods (forwarded to database on each node)
    def add_movie(self, movie: str, city: str, seats: int = 50):
        """Add a movie to the RAFT-hosted database."""
        return storage.add_movie_to_db(self.db, movie, city, seats)
    
    def get_all_movies(self):
        """Get all movies from the RAFT-hosted database."""
        return storage.get_all_movies(self.db)
    
    def update_movie_seats(self, movie: str, city: str, seats: int):
        """Update movie seats in the RAFT-hosted database."""
        return storage.update_movie_seats(self.db, movie, city, seats)
    
    def create_user(self, username: str, password: str):
        """Create a user in the RAFT-hosted database."""
        return storage.create_user(self.db, username, password)
    
    def authenticate_user(self, username: str, password: str):
        """Authenticate a user against the RAFT-hosted database."""
        return storage.authenticate_user(self.db, username, password)
    
    def create_session(self, user_id: int):
        """Create a session in the RAFT-hosted database."""
        return storage.create_session(self.db, user_id)
    
    def get_user_by_token(self, token: str):
        """Get user info by session token from the RAFT-hosted database."""
        return storage.get_user_by_token(self.db, token)
    
    def logout(self, token: str):
        """Logout a user from the RAFT-hosted database."""
        return storage.logout(self.db, token)
    
    def get_all_logs(self):
        """Get all RAFT logs from the database."""
        return storage.get_all_logs(self.db)