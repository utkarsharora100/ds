import threading
import random
import time

# ✅ NEW
from fastapi import FastAPI
import uvicorn


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
        self._register_routes()

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

    # ✅ NEW — serve FastAPI
    def serve(self, port: int):
        uvicorn.run(self.app, host="0.0.0.0", port=port)
