import random
import time
import threading
from proto import raft_pb2, raft_pb2_grpc
from llm.storage import append_log, get_all_logs

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
