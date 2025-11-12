import threading
import random
import time
import uvicorn
import sys
import os
import grpc
from fastapi import FastAPI
from concurrent import futures
from proto import raft_pb2, raft_pb2_grpc

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from llm import storage

# --- IMPORT THE RAFT LOGIC CORE ---
from raft_state import RaftNodeState


class RaftNode:
    def __init__(self, node_id, peers_map):
        """
        Initializes the Raft Node server.
        
        Args:
            node_id (str): The ID of this node (e.g., "N1").
            peers_map (dict): A map of all node IDs to their gRPC addresses.
                              e.g., {"N1": "localhost:50051", "N2": ...}
        """
        self.node_id = node_id
        self.peers_map = peers_map
        self.my_grpc_addr = self.peers_map[self.node_id]
        
        # --- 1. Create gRPC stubs for all OTHER nodes ---
        self.other_peer_addrs = []
        self.stub_dict = {} # {address: stub}
        for peer_id, peer_addr in self.peers_map.items():
            if peer_id != self.node_id:
                self.other_peer_addrs.append(peer_addr)
                try:
                    # Create a gRPC channel to the peer
                    channel = grpc.insecure_channel(peer_addr)
                    # Create a stub (client) for the RaftService
                    self.stub_dict[peer_addr] = raft_pb2_grpc.RaftServiceStub(channel)
                    print(f"[{self.node_id}] Created gRPC stub for {peer_id} at {peer_addr}")
                except Exception as e:
                    print(f"[{self.node_id}] FAILED to create gRPC stub for {peer_id}: {e}")

        # --- 2. Instantiate the Raft Logic Core ---
        # This starts the election timers and state management
        self.state = RaftNodeState(
            node_id=self.node_id,
            peers=self.other_peer_addrs,
            stub_dict=self.stub_dict
        )
        
        # --- 3. Set up FastAPI ---
        # This is the HTTP server for the Application_server to talk to
        self.app = FastAPI()
        self._register_routes()

        # --- 4. Start gRPC Server in a background thread ---
        # This is the server for internal Raft-to-Raft communication
        self.grpc_port = int(self.my_grpc_addr.split(':')[-1])
        threading.Thread(target=self._start_grpc_server, daemon=True).start()

    # ------------------------------------------------------------------
    # FastAPI HTTP Routes (for app server)
    # ------------------------------------------------------------------
    def _register_routes(self):
        """
        Register all FastAPI routes. These routes delegate
        logic to the RaftNodeState instance (self.state).
        """
        
        @self.app.get("/status")
        def status():
            # Read state directly from the RaftNodeState instance
            # This endpoint is "smart": includes progress if leader
            with self.state.lock:
                is_leader = self.state.state == "leader"
                resp = {
                    "node_id": self.state.node_id,
                    "state": self.state.state,
                    "term": self.state.current_term,
                    "leader_id": self.state.leader_id,
                    "peers": self.state.peers,
                    "is_leader": is_leader
                }
                # Include progress variables if this node is the leader
                if is_leader:
                    resp["next_index"] = self.state.next_index
                    resp["match_index"] = self.state.match_index
            return resp

        @self.app.post("/trigger-election")
        def manual_election():
            # Call the method on the RaftNodeState instance
            threading.Thread(target=self.state.start_election, daemon=True).start()
            return {"message": "Election manually triggered."}

        # ---------------- DB endpoints ----------------

        @self.app.get("/movies")
        def get_movies():
            """Get all movies (read-only, no replication needed)"""
            try:
                # Delegate to the state's method
                movies = self.state.get_all_movies()
                return {"status": "success", "movies": movies}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.post("/add_movie")
        def add_movie(payload: dict):
            """Add a movie (replicated write operation)"""
            try:
                # This is a replicated command
                movie = payload.get("movie")
                city = payload.get("city")
                seats = int(payload.get("seats", 50))
                
                # Use the replicated command handler
                result = self.state.handle_client_command("add_movie", 
                     {"movie": movie, "city": city, "seats": seats})
                
                return result # Will be {"status": "success"} or {"status": "failure", ...}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.post("/update_seats")
        def update_seats(payload: dict):
            """Update seats (replicated write operation)"""
            try:
                # This is a replicated command
                movie = payload.get("movie")
                city = payload.get("city")
                seats = int(payload.get("seats", 1)) # This is seats_to_book (e.g., 5)
                
                # Use the replicated command handler
                # We store the *negative* number to decrement seats
                result = self.state.handle_client_command("update_seats", 
                     {"movie": movie, "city": city, "seats_to_book": -seats})

                return result
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        # --- NEW BOOKING ENDPOINTS (FOR PERSISTENT BOOKINGS) ---
        @self.app.post("/add_booking")
        def add_booking(payload: dict):
            """Adds a booking to the replicated log (write operation)"""
            try:
                # The payload is the entire booking entry
                result = self.state.handle_client_command("add_booking", payload)
                return result
            except Exception as e:
                return {"status": "failure", "message": str(e)}
        
        @self.app.get("/get_bookings")
        def get_bookings():
            """Gets all bookings from the local DB (read-only)"""
            try:
                bookings = self.state.get_all_bookings()
                return {"status": "success", "bookings": bookings}
            except Exception as e:
                return {"status": "failure", "message": str(e)}
        
        @self.app.post("/clear_bookings")
        def clear_bookings(payload: dict):
            """Clears all bookings (replicated write operation)"""
            try:
                # TODO: Add token check logic here if needed
                result = self.state.handle_client_command("clear_bookings", {})
                return result
            except Exception as e:
                return {"status": "failure", "message": str(e)}
        # --- END NEW ---

        @self.app.post("/create_user")
        def create_user(payload: dict):
            """Create a new user (replicated write operation)"""
            try:
                username = payload.get("username")
                password = payload.get("password")
                # Use the replicated command handler
                result = self.state.handle_client_command("create_user",
                    {"username": username, "password": password})
                return result
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.post("/authenticate")
        def authenticate(payload: dict):
            """Authenticate a user (read-only)"""
            try:
                username = payload.get("username")
                password = payload.get("password")
                # Auth is a read-only operation, no need to replicate
                user_id = self.state.authenticate_user(username, password)
                if user_id:
                    return {"status": "success", "user_id": user_id}
                return {"status": "failure", "message": "invalid_credentials"}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.post("/create_session")
        def create_session(payload: dict):
            """Create a session (read-only, local to node)"""
            try:
                user_id = int(payload.get("user_id"))
                # Sessions are read-only, no need to replicate
                token = self.state.create_session(user_id)
                return {"status": "success", "token": token}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.get("/get_user_by_token")
        def get_user_by_token(token: str):
            """Get user from token (read-only, local to node)"""
            try:
                # Read-only, no replication
                res = self.state.get_user_by_token(token)
                if res:
                    return {"status": "success", "user_id": res[0], "username": res[1]}
                return {"status": "failure", "message": "not_found"}
            except Exception as e:
                return {"status":"failure", "message": str(e)}

        @self.app.post("/logout")
        def logout(payload: dict):
            """Log out user (read-only, local to node)"""
            try:
                token = payload.get("token")
                # Read-only, no replication
                ok = self.state.logout(token)
                return {"status": "success"} if ok else {"status": "failure"}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.get("/raft_logs")
        def raft_logs():
            """Get all logs (read-only)"""
            try:
                logs = self.state.get_all_logs()
                return {"status": "success", "logs": logs}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

    # ------------------------------------------------------------------
    # gRPC Server (for internal Raft communication)
    # ------------------------------------------------------------------
    class _RaftServicer(raft_pb2_grpc.RaftServiceServicer):
        def __init__(self, node_state: RaftNodeState):
            # Store a reference to the RaftNodeState instance
            self.state = node_state

        # --- Raft RPCs ---
        # These are called by *other* nodes
        
        def RequestVote(self, request, context):
            # Delegate to the state's handler
            return self.state.handle_vote_request(request)

        def AppendEntries(self, request, context):
            # Delegate to the state's handler
            return self.state.handle_append_entries(request)

        # --- Database RPCs ---
        # These are (currently) unused as we proxy via HTTP
        
        def AddMovie(self, request, context):
            ok = self.state.add_movie(request.movie, request.city, request.seats)
            return raft_pb2.AddMovieResponse(success=ok, message="" if ok else "exists")

        def GetMovies(self, request, context):
            movies = self.state.get_all_movies()
            resp = raft_pb2.GetMoviesResponse()
            for m in movies:
                mv = raft_pb2.Movie(title=m.get("movie"), city=m.get("city"), seats=int(m.get("seats") or 0))
                resp.movies.append(mv)
            return resp

        def UpdateSeats(self, request, context):
            # Note: This expects a *negative* number for booking
            ok = self.state.update_movie_seats(request.movie, request.city, request.seats)
            return raft_pb2.UpdateSeatsResponse(success=ok, message="" if ok else "insufficient_or_missing")

        def CreateUser(self, request, context):
            ok = self.state.create_user(request.username, request.password)
            return raft_pb2.CreateUserResponse(success=ok, message="" if ok else "exists")

        def AuthenticateUser(self, request, context):
            user_id = self.state.authenticate_user(request.username, request.password)
            return raft_pb2.AuthenticateUserResponse(user_id=user_id or 0, success=bool(user_id))
        
        def CreateSession(self, request, context):
            token = self.state.create_session(request.user_id)
            return raft_pb2.CreateSessionResponse(token=token)

        def GetUserByToken(self, request, context):
            res = self.state.get_user_by_token(request.token)
            if res:
                return raft_pb2.GetUserByTokenResponse(user_id=res[0], username=res[1], success=True)
            return raft_pb2.GetUserByTokenResponse(success=False)

        def Logout(self, request, context):
            ok = self.state.logout(request.token)
            return raft_pb2.LogoutResponse(success=ok)
        

    def _start_grpc_server(self):
        """Starts the gRPC server in the background."""
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        # Pass the RaftNodeState instance to the servicer
        raft_pb2_grpc.add_RaftServiceServicer_to_server(self._RaftServicer(self.state), server)
        
        server.add_insecure_port(f"0.0.0.0:{self.grpc_port}")
        print(f"[{self.node_id}] ▶️ Starting gRPC RaftService on port {self.grpc_port}")
        server.start()
        server.wait_for_termination()

    # ------------------------------------------------------------------
    # Main serve method (to be called by launcher)
    # ------------------------------------------------------------------
    def serve(self, port: int):
        """Starts the FastAPI (Uvicorn) server."""
        print(f"[{self.node_id}] ▶️ Starting FastAPI app server on http://0.0.0.0:{port}")
        uvicorn.run(self.app, host="0.0.0.0", port=port)