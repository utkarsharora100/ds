import threading
import random
import time
import httpx

# ✅ NEW
from fastapi import FastAPI, Request
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

            # Real vote count - start with self vote
            votes = 1
            total_nodes = len(self.peers) + 1
            majority = total_nodes // 2 + 1

            # Request votes from actual peers via HTTP
            for peer_id, peer_address in self.peers.items():
                try:
                    # Convert service name format to HTTP URL if needed
                    if not peer_address.startswith('http'):
                        peer_url = f"http://{peer_address}"
                    else:
                        peer_url = peer_address

                    # Request vote from peer
                    response = httpx.post(
                        f"{peer_url}/request-vote",
                        json={"term": self.term, "candidate_id": self.node_id},
                        timeout=1.0
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("vote_granted", False):
                            votes += 1
                            print(f"[{self.node_id}] ✓ Got vote from {peer_id}")
                        else:
                            print(f"[{self.node_id}] ✗ Vote denied by {peer_id} (term {data.get('term')})")
                except Exception as e:
                    print(f"[{self.node_id}] ✗ Could not reach {peer_id}: {e}")

            # Check if we have majority
            if votes >= majority:
                self.state = "leader"
                self.leader_id = self.node_id
                print(f"[{self.node_id}] 🏆 is the LEADER now (term {self.term}, votes {votes}/{total_nodes})")
            else:
                self.state = "follower"
                print(f"[{self.node_id}] ❌ Election failed (term {self.term}, votes {votes}/{total_nodes})")

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

        @self.app.post("/request-vote")
        async def request_vote(request: Request):
            """Handle vote requests from other nodes during elections"""
            data = await request.json()
            candidate_term = data.get("term", 0)
            candidate_id = data.get("candidate_id", "")

            with self.lock:
                # If candidate's term is higher, update our term and step down
                if candidate_term > self.term:
                    self.term = candidate_term
                    self.state = "follower"
                    self.voted_for = None
                    self.leader_id = None

                # Grant vote if we haven't voted in this term, or already voted for this candidate
                if candidate_term == self.term and (self.voted_for is None or self.voted_for == candidate_id):
                    self.voted_for = candidate_id
                    self.election_timeout = self._reset_timeout()  # Reset timeout when granting vote
                    print(f"[{self.node_id}] ✓ Granted vote to {candidate_id} for term {candidate_term}")
                    return {"term": self.term, "vote_granted": True}
                else:
                    print(f"[{self.node_id}] ✗ Denied vote to {candidate_id} (already voted for {self.voted_for})")
                    return {"term": self.term, "vote_granted": False}

        @self.app.post("/trigger-election")
        def manual_election():
            self._start_election()
            return {"message": "Election manually triggered."}

    # ✅ NEW — serve FastAPI
    def serve(self, port: int):
        uvicorn.run(self.app, host="0.0.0.0", port=port)
