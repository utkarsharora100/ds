import random
import time
import threading
from proto import raft_pb2, raft_pb2_grpc
import sys
import os
import json 
import sqlite3 # <--- IMPORT SQLITE3

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from llm import storage

class RaftNodeState:
    def __init__(self, node_id, peers, stub_dict):
        """
        Initializes the Raft Node's state machine.
        """
        self.node_id = node_id
        self.peers = peers              # list of peer addresses
        self.stub_dict = stub_dict      # mapping {address: stub}

        # --- Persistent State (should be saved to stable storage) ---
        self.current_term = 0
        self.voted_for = None
        self.log = []                   # List of log entries. Each entry is (term, command)

        # --- Volatile State (all nodes) ---
        self.commit_index = 0
        self.last_applied = 0

        self.state = "follower"
        self.leader_id = None

        # --- Volatile State (leaders only, re-initialized on election) ---
        self.next_index = {} 
        self.match_index = {}

        # --- Timers and Threads ---
        self.election_timeout_duration = random.uniform(3, 5) # 3-5 seconds
        self.heartbeat_interval = 1.0 # 1 second
        self.last_heartbeat = time.time()
        self.lock = threading.Lock()
        
        
        # --- !!! THIS IS THE FIX FOR DISAPPEARING BOOKINGS !!! ---
        # We are no longer using the in-memory DB.
        # We are creating a persistent, file-based database for each node.
        # This assumes a '/data' directory is mounted as a volume
        # in your docker-compose.yml file.
        db_dir = "/data"
        if not os.path.exists(db_dir):
            # Fallback for local testing (not in Docker)
            db_dir = os.path.join(os.path.dirname(__file__), '..', '.db_data')
            os.makedirs(db_dir, exist_ok=True)
        
        db_path = os.path.join(db_dir, f"raft_node_{self.node_id}.db")
        
        # Connect to the persistent database file
        # check_same_thread=False is crucial for multi-threaded access
        self.db = sqlite3.connect(db_path, check_same_thread=False) 
        print(f"[{node_id}] ✅ Database CONNECTED at: {db_path}")
        # --- END FIX ---
        
        # --- This line is no longer needed ---
        # self.db = storage.create_in_memory_db() 
        
        try:
            # You must add this function to your storage.py
            # It should run: CREATE TABLE IF NOT EXISTS bookings (...)
            storage.create_bookings_table(self.db) 
            print(f"[{node_id}] ✅ Bookings table verified.")
        except Exception as e:
            print(f"[{node_id}] ⚠️ Could not create bookings table: {e} (This is OK if it already exists)")
        
        try:
            # We also need to create the other tables
            storage.create_tables(self.db) # Assuming this function exists
            print(f"[{node_id}] ✅ All other tables verified.")
        except Exception as e:
             print(f"[{node_id}] ⚠️ Could not create other tables: {e} (This is OK if they already exist)")


        # Start background election timer thread
        threading.Thread(target=self.run_election_timer, daemon=True).start()

    def run_election_timer(self):
        """
        Runs in the background. If no heartbeat is received within the
        election timeout, it starts a new election.
        """
        while True:
            time.sleep(0.1) # Check every 100ms
            
            with self.lock:
                # Only run the timer if we are a follower or candidate
                if self.state in ("follower", "candidate"):
                    time_since_heartbeat = time.time() - self.last_heartbeat
                    
                    if time_since_heartbeat > self.election_timeout_duration:
                        print(f"[{self.node_id}] Election timeout! (No heartbeat for {time_since_heartbeat:.2f}s). Starting election.")
                        # Start election in a new thread to not block the timer
                        threading.Thread(target=self.start_election, daemon=True).start()
                        # Reset the timer for the *new* election
                        self.reset_election_timer() 

    def reset_election_timer(self):
        """Resets the election timeout to a new random value."""
        self.last_heartbeat = time.time()
        self.election_timeout_duration = random.uniform(3, 5)

    def start_election(self):
        """Transitions to candidate and requests votes from peers."""
        with self.lock:
            # Can't start an election if already leader
            if self.state == "leader":
                return

            # --- Become Candidate ---
            self.state = "candidate"
            self.current_term += 1
            self.voted_for = self.node_id
            self.reset_election_timer()
            
            print(f"[{self.node_id}] Starting election for term {self.current_term}")
            
            # --- Tally Votes ---
            votes_received = 1  # Vote for self
            
            last_log_index = len(self.log) - 1
            last_log_term = self.log[last_log_index][0] if last_log_index >= 0 else 0
            
            # This is the request we are sending
            vote_req_payload = raft_pb2.RequestVoteRequest(
                term=self.current_term, 
                candidate_id=self.node_id,
                last_log_index=last_log_index,
                last_log_term=last_log_term
            )

        # --- Send RequestVote RPCs to all peers (in parallel) ---
        # This is done outside the lock to avoid deadlocks
        
        for peer_addr, stub in self.stub_dict.items():
            try:
                # Use a timeout for the gRPC call
                resp = stub.RequestVote(vote_req_payload, timeout=0.5) 
                
                with self.lock:
                    if resp.term > self.current_term:
                        # Their term is higher, we are no longer candidate
                        self.become_follower(resp.term)
                        return # Stop election
                    
                    if resp.vote_granted:
                        votes_received += 1
                        
            except Exception as e:
                # This is expected if a node is down
                print(f"[{self.node_id}] Could not get vote from {peer_addr}: {e}")
                pass

        # --- Check for Majority ---
        with self.lock:
            # Check if we are still a candidate in the same term
            # (we might have become a follower if we received an AppendEntries)
            if self.state != "candidate" or self.current_term != vote_req_payload.term:
                return # Election is no longer valid

            majority = (len(self.peers) + 1) // 2 + 1
            if votes_received >= majority:
                self.become_leader()
            else:
                # Failed to win, revert to follower
                self.state = "follower"
                print(f"[{self.node_id}] Election failed, received {votes_received}/{majority} votes.")

    def become_follower(self, term):
        """Transitions to follower state."""
        print(f"[{self.node_id}] Stepping down. Becoming follower for term {term}.")
        self.state = "follower"
        self.current_term = term
        self.voted_for = None
        self.leader_id = None
        self.reset_election_timer()

    def become_leader(self):
        """Transitions to leader state and initializes progress trackers."""
        print(f"[{self.node_id}] 🏆 BECOMES LEADER (term {self.current_term})")
        self.state = "leader"
        self.leader_id = self.node_id
        
        # --- Initialize leader's volatile state ---
        last_log_idx = len(self.log)
        self.next_index = {peer: last_log_idx + 1 for peer in self.peers}
        self.match_index = {peer: 0 for peer in self.peers}

        # Start sending heartbeats
        threading.Thread(target=self.heartbeat_loop, daemon=True).start()

    def heartbeat_loop(self):
        """
        As leader, periodically sends heartbeats (empty AppendEntries)
        to all peers to maintain authority.
        """
        while True:
            with self.lock:
                if self.state != "leader":
                    return # Stop sending heartbeats if not leader
                
                current_term = self.current_term
                leader_commit = self.commit_index

            # --- Send heartbeats (AppendEntries) to all peers ---
            # This is done outside the lock
            for peer_addr, stub in self.stub_dict.items():
                try:
                    # TODO: This needs to be a full AppendEntries, not just a heartbeat.
                    # It should send log entries based on self.next_index[peer_addr]
                    
                    req = raft_pb2.AppendEntriesRequest(
                        term=current_term,
                        leader_id=self.node_id,
                        leader_commit=leader_commit,
                        # prev_log_index=...
                        # prev_log_term=...
                        # entries=...
                    )
                    
                    # Use a timeout
                    resp = stub.AppendEntries(req, timeout=0.5)

                    with self.lock:
                        if resp.term > self.current_term:
                            # Peer has a higher term, we must step down
                            self.become_follower(resp.term)
                            return # Stop heartbeat loop
                        
                        # TODO: Handle resp.success (log replication logic)
                        # if resp.success:
                        #   self.match_index[peer_addr] = ...
                        #   self.next_index[peer_addr] = ...
                        # else:
                        #   self.next_index[peer_addr] -= 1
                        
                except Exception:
                    # Peer is likely down, will retry on next heartbeat
                    pass
            
            # --- Check for commit advancement ---
            # TODO: After updating match_index, check if a new
            # commit_index can be set based on majority match.
            # self.update_commit_index()
            
            time.sleep(self.heartbeat_interval)

    # ------------------------------------------------------------------
    # gRPC Servicer Handlers (called by RaftNode's servicer)
    # ------------------------------------------------------------------

    def handle_append_entries(self, request: raft_pb2.AppendEntriesRequest):
        """Handler for AppendEntries RPC (heartbeats or log entries)."""
        with self.lock:
            # 1. Reply false if term < currentTerm
            if request.term < self.current_term:
                return raft_pb2.AppendEntriesResponse(term=self.current_term, success=False)
            
            # We have a valid leader or a new leader
            self.reset_election_timer()
            
            if request.term > self.current_term:
                self.become_follower(request.term)
            
            if self.state == "candidate":
                self.state = "follower" # Step down if we were a candidate
                
            self.leader_id = request.leader_id

            # TODO: Implement full log matching logic
            # 2. Reply false if log doesn’t contain an entry at prevLogIndex
            #    whose term matches prevLogTerm
            
            # TODO:
            # 3. If an existing entry conflicts with a new one (same index
            #    but different terms), delete the existing entry and all that
            #    follow it
            
            # TODO:
            # 4. Append any new entries not already in the log

            # 5. If leaderCommit > commitIndex, set commitIndex =
            #    min(leaderCommit, index of last new entry)
            if request.leader_commit > self.commit_index:
                self.commit_index = min(request.leader_commit, len(self.log) - 1)
                # TODO: Apply logs to state machine (self.apply_logs())

            return raft_pb2.AppendEntriesResponse(term=self.current_term, success=True)

    def handle_vote_request(self, request: raft_pb2.RequestVoteRequest):
        """Handler for RequestVote RPC."""
        with self.lock:
            # 1. Reply false if term < currentTerm
            if request.term < self.current_term:
                return raft_pb2.RequestVoteResponse(term=self.current_term, vote_granted=False)
            
            # If we see a higher term, step down and update term
            if request.term > self.current_term:
                self.become_follower(request.term)

            # 2. If votedFor is null or candidateId, and candidate's log is at
            #    least as up-to-date as receiver's log, grant vote
            voted_for_ok = self.voted_for is None or self.voted_for == request.candidate_id
            
            # TODO: Implement log up-to-dateness check
            log_ok = True
            
            if voted_for_ok and log_ok:
                self.voted_for = request.candidate_id
                self.reset_election_timer() # Granting vote resets our timer
                return raft_pb2.RequestVoteResponse(term=self.current_term, vote_granted=True)
            else:
                return raft_pb2.RequestVoteResponse(term=self.current_term, vote_granted=False)

    def handle_client_command(self, command_type, command_data):
        """
        Handles a client command (e.g., "add_movie", "book_seat").
        This should only be run on the LEADER.
        """
        with self.lock:
            if self.state != "leader":
                return {"status": "failure", "message": "Not leader", "leader_id": self.leader_id}

            term = self.current_term
            # Store command_data as a JSON string for the log
            log_entry = (term, command_type, json.dumps(command_data))
            
            # Append to our local log
            self.log.append(log_entry) 
            
            # Persist to our local DB log
            storage.append_log(self.db, term, command_type, json.dumps(command_data)) 

            print(f"[{self.node_id}] Log appended: {log_entry}")
            
            # TODO: This command now needs to be replicated to peers via
            # the heartbeat_loop. The client should wait for the command
            # to be *committed* (not just logged) before getting a response.
            
            # For this simple demo, we apply it immediately.
            # THIS IS INCORRECT FOR A REAL RAFT.
            try:
                result = self.apply_command(command_type, command_data)
                return {"status": "success", "result": result}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

    def apply_command(self, command_type, command_data):
        """
        (INCORRECTLY PLACED)
        Applies a command to the state machine (the database).
        
        In a REAL Raft, this would run when self.last_applied < self.commit_index,
        and it would apply self.log[self.last_applied].
        """
        if command_type == "add_movie":
            return self.add_movie(
                command_data['movie'], 
                command_data['city'], 
                command_data['seats']
            )
        elif command_type == "update_seats":
            return self.update_movie_seats(
                command_data['movie'],
                command_data['city'],
                command_data['seats_to_book'] # This is a negative number
            )
        # --- NEW BOOKING COMMANDS ---
        elif command_type == "add_booking":
            # command_data is the full booking entry
            return self.add_booking(command_data)
        elif command_type == "clear_bookings":
            return self.clear_all_bookings()
        # --- END NEW ---
        elif command_type == "create_user":
            return self.create_user(
                command_data['username'],
                command_data['password']
            )
        
        raise ValueError(f"Unknown command type: {command_type}")


    # ------------------------------------------------------------------
    # Database Methods (called by handlers)
    # ------------------------------------------------------------------
    
    def add_movie(self, movie: str, city: str, seats: int = 50):
        """Add a movie to the RAFT-hosted database."""
        return storage.add_movie_to_db(self.db, movie, city, seats)
    
    def get_all_movies(self):
        """Get all movies from the RAFT-hosted database."""
        return storage.get_all_movies(self.db)
    
    def update_movie_seats(self, movie: str, city: str, seats_to_book: int):
        """Update movie seats in the RAFT-hosted database."""
        # Note: update_movie_seats expects a *negative* number to book
        return storage.update_movie_seats(self.db, movie, city, seats_to_book)
    
    # --- NEW BOOKING DB METHODS ---
    def add_booking(self, booking_entry: dict):
        """Adds a booking to the RAFT-hosted database."""
        # Assuming a storage function that takes the full entry
        return storage.add_booking_to_db(self.db, booking_entry)
        
    def get_all_bookings(self):
        """Gets all bookings from the RAFT-hosted database."""
        return storage.get_all_bookings_from_db(self.db)
        
    def clear_all_bookings(self):
        """Clears all bookings from the RAFT-hosted database."""
        return storage.clear_all_bookings(self.db)
    # --- END NEW ---

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