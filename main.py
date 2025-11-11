from raft.raft_node import RaftNode
import sys

if __name__ == "__main__":
    # Define cluster nodes
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

    # Start Raft node
    node = RaftNode(node_id, peers)
    port = int(nodes[node_id].split(":")[1])
    node.serve(port)
