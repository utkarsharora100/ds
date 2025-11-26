import threading
import random
import time
import httpx

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

    
        self.HEARTBEAT_INTERVAL = 0.05      # 50ms (20 heartbeats/sec)
        self.ELECTION_TIMEOUT_MIN = 0.5     # 500ms
        self.ELECTION_TIMEOUT_MAX = 1.0     # 1000ms

        # Initialize timing state
        self.last_heartbeat_time = time.time()
        self._stop_heartbeat = False
        self._heartbeat_thread = None
        self.log = []  # Log for future log replication
        self.commit_index = 0

        self.election_timeout = self._reset_timeout()
        self.lock = threading.Lock()

        print(f"[{self.node_id}] Timing: heartbeat={self.HEARTBEAT_INTERVAL*1000}ms, election={self.ELECTION_TIMEOUT_MIN*1000}-{self.ELECTION_TIMEOUT_MAX*1000}ms")

        # Start background thread for Raft timing
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

        #  NEW — attach FastAPI app
        self.app = FastAPI()
        self._register_routes()

    def _reset_timeout(self):
        # Random election timeout using configured constants
        return time.time() + random.uniform(self.ELECTION_TIMEOUT_MIN, self.ELECTION_TIMEOUT_MAX)

    def _run(self):
        """
        Background thread: monitors for leader heartbeats and starts election if timeout.
        Only starts election if NO heartbeat received during timeout period.
        """
        while self.running:
            if self.state == "leader":
                # Leaders don't run election timer
                time.sleep(0.1)
                continue

            # Check periodically (every 100ms)
            time.sleep(0.1)

            # Check if heartbeat was received recently
            with self.lock:
                time_since_heartbeat = time.time() - self.last_heartbeat_time
                timeout = random.uniform(self.ELECTION_TIMEOUT_MIN, self.ELECTION_TIMEOUT_MAX)

            if time_since_heartbeat >= timeout:
                # No heartbeat received - leader might be dead
                print(f"[{self.node_id}] Election timeout: no heartbeat for {time_since_heartbeat:.2f}s")
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
                print(f"[{self.node_id}] is the LEADER now (term {self.term}, votes {votes}/{total_nodes})")

                # CRITICAL: Start heartbeat loop immediately
                if hasattr(self, '_heartbeat_thread') and self._heartbeat_thread:
                    # Cancel any existing heartbeat thread
                    self._stop_heartbeat = True
                    self._heartbeat_thread.join(timeout=1.0)

                self._stop_heartbeat = False
                self._heartbeat_thread = threading.Thread(target=self._send_heartbeats_loop, daemon=True)
                self._heartbeat_thread.start()
                print(f"[{self.node_id}] Started heartbeat loop")
            else:
                self.state = "follower"
                print(f"[{self.node_id}] Election failed (term {self.term}, votes {votes}/{total_nodes})")

            # Reset election timeout for next term
            self.election_timeout = self._reset_timeout()

    def _step_down(self, new_term):
        """
        Step down from leader/candidate to follower due to higher term.
        Stops heartbeat loop if running.
        """
        with self.lock:
            old_state = self.state
            self.state = "follower"
            self.term = new_term
            self.voted_for = None
            self.leader_id = None
            self.last_heartbeat_time = time.time()

        # Stop heartbeat loop if we were leader
        if old_state == "leader":
            self._stop_heartbeat = True
            if self._heartbeat_thread:
                self._heartbeat_thread.join(timeout=1.0)
            print(f"[{self.node_id}] Stepped down from leader to follower (term {new_term})")

        elif old_state == "candidate":
            print(f"[{self.node_id}] Stepped down from candidate to follower (term {new_term})")

    def _send_heartbeats_loop(self):
        """
        Leader continuously sends heartbeats to all followers.
        Sends empty AppendEntries every 50ms.
        """
        while self.state == "leader" and not self._stop_heartbeat:
            try:
                # Send heartbeat to each peer
                for peer_id, peer_address in self.peers.items():
                    try:
                        # Convert service name format to HTTP URL if needed
                        if not peer_address.startswith('http'):
                            peer_url = f"http://{peer_address}"
                        else:
                            peer_url = peer_address

                        response = httpx.post(
                            f"{peer_url}/append-entries",
                            json={
                                "term": self.term,
                                "leader_id": self.node_id,
                                "entries": [],  # Empty = heartbeat
                                "prev_log_index": len(self.log) - 1 if self.log else -1,
                                "prev_log_term": self.log[-1].get("term", 0) if self.log else 0,
                                "leader_commit": self.commit_index
                            },
                            timeout=0.1  # 100ms timeout
                        )

                        if response.status_code == 200:
                            data = response.json()
                            # Check if peer has higher term
                            if data.get("term", 0) > self.term:
                                print(f"[{self.node_id}] Peer {peer_id} has higher term {data['term']}, stepping down")
                                self._step_down(data["term"])
                                return

                    except Exception:
                        # Peer might be down, continue with others
                        pass

                # Sleep before next heartbeat
                time.sleep(self.HEARTBEAT_INTERVAL)

            except Exception as e:
                print(f"[{self.node_id}] Heartbeat loop error: {e}")
                break

        print(f"[{self.node_id}] Stopped heartbeat loop")

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

        @self.app.post("/append-entries")
        async def append_entries(request: Request):
            """Handle heartbeats and log replication from leader"""
            data = await request.json()
            leader_term = data.get("term", 0)
            leader_id = data.get("leader_id", "")
            entries = data.get("entries", [])

            with self.lock:
                # Update term if higher
                if leader_term > self.term:
                    self.term = leader_term
                    self.voted_for = None
                    self.state = "follower"
                    self.leader_id = leader_id

                # Reject if term is outdated
                if leader_term < self.term:
                    return {"success": False, "term": self.term}

                
                self.last_heartbeat_time = time.time()
                self.leader_id = leader_id

                # If we were candidate, step down to follower
                if self.state == "candidate":
                    self.state = "follower"
                    print(f"[{self.node_id}] Stepped down from candidate to follower (received heartbeat from {leader_id})")

            # Only log non-empty heartbeats to reduce spam
            if entries:
                print(f"[{self.node_id}] Received AppendEntries from {leader_id} (term {leader_term}, {len(entries)} entries)")

            return {"success": True, "term": self.term}

        @self.app.post("/request-vote")
        async def request_vote(request: Request):
            """Handle vote requests from other nodes during elections"""
            data = await request.json()
            candidate_term = data.get("term", 0)
            candidate_id = data.get("candidate_id", "")

            with self.lock:
                # Update term if candidate has higher term
                if candidate_term > self.term:
                    self.term = candidate_term
                    self.voted_for = None
                    
                    if self.state in ["leader", "candidate"]:
                        old_state = self.state
                        self.state = "follower"
                        if old_state == "leader":
                            self._stop_heartbeat = True
                            print(f"[{self.node_id}] Stepping down from leader due to higher term {candidate_term}")

                # Reject if term is outdated
                if candidate_term < self.term:
                    print(f"[{self.node_id}] Rejected vote for {candidate_id} (stale term {candidate_term} < {self.term})")
                    return {"vote_granted": False, "term": self.term}

                # Grant vote if haven't voted yet OR already voted for this candidate
                if self.voted_for is None or self.voted_for == candidate_id:
                    self.voted_for = candidate_id
                    self.last_heartbeat_time = time.time()  # Reset timer (activity detected)
                    print(f"[{self.node_id}] ✓ Granted vote to {candidate_id} for term {candidate_term}")
                    return {"vote_granted": True, "term": self.term}
                else:
                    print(f"[{self.node_id}] ✗ Denied vote to {candidate_id} (already voted for {self.voted_for})")
                    return {"vote_granted": False, "term": self.term}

        @self.app.post("/trigger-election")
        def manual_election():
            self._start_election()
            return {"message": "Election manually triggered."}

    def serve(self, port: int):
        uvicorn.run(self.app, host="0.0.0.0", port=port)
