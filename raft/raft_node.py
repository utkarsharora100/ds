import threading
import random
import time

# ✅ NEW
from fastapi import FastAPI
import uvicorn
import sys
import os
from llm import storage
import threading
import requests
import grpc
from concurrent import futures
from proto import raft_pb2, raft_pb2_grpc


class RaftNode:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers  # dict of node_id -> address
        self.state = "follower"
        self.term = 0
        self.voted_for = None
        self.leader_id = None
        self.running = True

        self.election_timeout = self._reset_timeout()
        self.lock = threading.Lock()

        # Start background thread for Raft timing
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

        # ✅ NEW — attach FastAPI app
        self.app = FastAPI()
        # initialize DB on this raft node
        # ensure parent path is importable
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        self.db = storage.create_in_memory_db()
        print(f"[{self.node_id}] ✅ Database initialized on RAFT node (FastAPI)")
        self._register_routes()

        # Start gRPC server for RaftService (DB + raft RPCs)
        self.grpc_port = int(os.environ.get(f"RAFT_PORT_{self.node_id}", 50051))
        threading.Thread(target=self._start_grpc_server, daemon=True).start()

    def _reset_timeout(self):
        # Random election timeout between 5–8 seconds
        return time.time() + random.uniform(5, 8)

    def _run(self):
        """Background thread: handles elections and leadership."""
        while self.running:
            time.sleep(0.5)
            now = time.time()

            # If election timeout reached and not leader, start election
            if now > self.election_timeout and self.state != "leader":
                self._start_election()

    def _start_election(self):
        with self.lock:
            self.term += 1
            self.state = "candidate"
            self.voted_for = self.node_id

            # Simulate vote count
            votes = 1  # self vote
            total_nodes = len(self.peers) + 1
            majority = total_nodes // 2 + 1

            # Simulate random support
            votes += random.randint(0, len(self.peers))

            if votes >= majority:
                self.state = "leader"
                self.leader_id = self.node_id
                print(f"[{self.node_id}] 🏆 is the LEADER now (term {self.term})")
            else:
                self.state = "follower"

            # Reset election timeout for next term
            self.election_timeout = self._reset_timeout()

    # ✅ NEW — FastAPI routes (status + simple manual endpoints)
    def _register_routes(self):

        @self.app.get("/status")
        def status():
            return {
                "node_id": self.node_id,
                "state": self.state,
                "term": self.term,
                "leader_id": self.leader_id,
                "peers": list(self.peers.keys())
            }

        @self.app.post("/trigger-election")
        def manual_election():
            self._start_election()
            return {"message": "Election manually triggered."}

        # ---------------- DB endpoints ----------------
        @self.app.get("/movies")
        def get_movies():
            try:
                movies = storage.get_all_movies(self.db)
                return {"status": "success", "movies": movies}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.post("/add_movie")
        def add_movie(payload: dict):
            try:
                movie = payload.get("movie")
                city = payload.get("city")
                seats = int(payload.get("seats", 50))
                ok = storage.add_movie_to_db(self.db, movie, city, seats)
                return {"status": "success"} if ok else {"status": "failure", "message": "exists"}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.post("/update_seats")
        def update_seats(payload: dict):
            try:
                movie = payload.get("movie")
                city = payload.get("city")
                seats = int(payload.get("seats", 1))
                ok = storage.update_movie_seats(self.db, movie, city, seats)
                return {"status": "success"} if ok else {"status": "failure", "message": "insufficient_or_missing"}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.post("/create_user")
        def create_user(payload: dict):
            try:
                username = payload.get("username")
                password = payload.get("password")
                ok = storage.create_user(self.db, username, password)
                return {"status": "success"} if ok else {"status": "failure", "message": "exists"}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.post("/authenticate")
        def authenticate(payload: dict):
            try:
                username = payload.get("username")
                password = payload.get("password")
                user_id = storage.authenticate_user(self.db, username, password)
                if user_id:
                    return {"status": "success", "user_id": user_id}
                return {"status": "failure", "message": "invalid_credentials"}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.post("/create_session")
        def create_session(payload: dict):
            try:
                user_id = int(payload.get("user_id"))
                token = storage.create_session(self.db, user_id)
                return {"status": "success", "token": token}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.get("/get_user_by_token")
        def get_user_by_token(token: str):
            try:
                res = storage.get_user_by_token(self.db, token)
                if res:
                    return {"status": "success", "user_id": res[0], "username": res[1]}
                return {"status": "failure", "message": "not_found"}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.post("/logout")
        def logout(payload: dict):
            try:
                token = payload.get("token")
                ok = storage.logout(self.db, token)
                return {"status": "success"} if ok else {"status": "failure"}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

        @self.app.get("/raft_logs")
        def raft_logs():
            try:
                logs = storage.get_all_logs(self.db)
                return {"status": "success", "logs": logs}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

    # ---------------- gRPC server & servicer ----------------
    class _RaftServicer(raft_pb2_grpc.RaftServiceServicer):
        def __init__(self, node):
            self.node = node

        # Basic Raft RPCs (simplified / passthrough)
        def RequestVote(self, request, context):
            # Simplified vote response (not full Raft implementation here)
            return raft_pb2.RequestVoteResponse(term=self.node.term, vote_granted=True)

        def AppendEntries(self, request, context):
            # Accept heartbeats
            return raft_pb2.AppendEntriesResponse(term=self.node.term, success=True, match_index=0)

        # ---------------- Database RPCs ----------------
        def AddMovie(self, request, context):
            ok = storage.add_movie_to_db(self.node.db, request.movie, request.city, request.seats)
            return raft_pb2.AddMovieResponse(success=ok, message="" if ok else "exists")

        def GetMovies(self, request, context):
            movies = storage.get_all_movies(self.node.db)
            resp = raft_pb2.GetMoviesResponse()
            for m in movies:
                mv = raft_pb2.Movie(title=m.get("movie"), city=m.get("city"), seats=int(m.get("seats") or 0))
                resp.movies.append(mv)
            return resp

        def UpdateSeats(self, request, context):
            ok = storage.update_movie_seats(self.node.db, request.movie, request.city, request.seats)
            return raft_pb2.UpdateSeatsResponse(success=ok, message="" if ok else "insufficient_or_missing")

        def CreateUser(self, request, context):
            ok = storage.create_user(self.node.db, request.username, request.password)
            return raft_pb2.CreateUserResponse(success=ok, message="" if ok else "exists")

        def AuthenticateUser(self, request, context):
            user_id = storage.authenticate_user(self.node.db, request.username, request.password)
            return raft_pb2.AuthenticateUserResponse(user_id=user_id or 0, success=bool(user_id))

        def CreateSession(self, request, context):
            token = storage.create_session(self.node.db, request.user_id)
            return raft_pb2.CreateSessionResponse(token=token)

        def GetUserByToken(self, request, context):
            res = storage.get_user_by_token(self.node.db, request.token)
            if res:
                return raft_pb2.GetUserByTokenResponse(user_id=res[0], username=res[1], success=True)
            return raft_pb2.GetUserByTokenResponse(success=False)

        def Logout(self, request, context):
            ok = storage.logout(self.node.db, request.token)
            return raft_pb2.LogoutResponse(success=ok)

    def _start_grpc_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        raft_pb2_grpc.add_RaftServiceServicer_to_server(self._RaftServicer(self), server)
        grpc_port = int(os.environ.get(f"RAFT_PORT_{self.node_id}", 50051))
        server.add_insecure_port(f"0.0.0.0:{grpc_port}")
        print(f"[{self.node_id}] ▶️ Starting gRPC RaftService on port {grpc_port}")
        server.start()
        server.wait_for_termination()

    # ✅ NEW — serve FastAPI
    def serve(self, port: int):
        uvicorn.run(self.app, host="0.0.0.0", port=port)
