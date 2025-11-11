from raft.raft_node import RaftNode
import sys
import os

if __name__ == "__main__":
    # Check if running in Docker (use container names) or locally (use localhost)
    use_docker = os.environ.get("DOCKER_ENV", "false").lower() == "true"
    
    if use_docker:
        # Use container names for Docker network
        nodes = {
            "node1": "raft-node1:50051",
            "node2": "raft-node2:50052",
            "node3": "raft-node3:50053"
        }
    else:
        # Use localhost for local development
        nodes = {
            "node1": "localhost:50051",
            "node2": "localhost:50052",
            "node3": "localhost:50053"
        }

    # Check command line argument
    if len(sys.argv) < 2:
        print("Usage: python main.py <node_id>")
        sys.exit(1)

    node_id = sys.argv[1]
    peers = {nid: addr for nid, addr in nodes.items() if nid != node_id}

    print(f"[{node_id}] Starting with peers: {peers}")
    
    # Start Raft node
    node = RaftNode(node_id, peers)
    port = int(nodes[node_id].split(":")[1])
    node.serve(port)
