#!/usr/bin/env python3
"""
Main entry point for Raft nodes
Usage: python main.py node1|node2|node3
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from raft.raft_node import RaftNode

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py node1|node2|node3")
        sys.exit(1)
    
    node_id = sys.argv[1]  # node1, node2, or node3
    
    if node_id not in ["node1", "node2", "node3"]:
        print(f"Error: Invalid node ID '{node_id}'. Must be node1, node2, or node3")
        sys.exit(1)
    
    # Port mapping
    port_map = {
        "node1": 50051,
        "node2": 50052,
        "node3": 50053
    }
    
    port = port_map[node_id]
    
    # Configure peers (other nodes)
    # In Docker, use service names; locally, use localhost
    docker_env = os.environ.get("DOCKER_ENV", "false").lower() == "true"
    
    if docker_env:
        # Docker environment - use service names
        peers = {
            "node1": "raft-node1:50051",
            "node2": "raft-node2:50052",
            "node3": "raft-node3:50053"
        }
    else:
        # Local environment - use localhost
        peers = {
            "node1": "localhost:50051",
            "node2": "localhost:50052",
            "node3": "localhost:50053"
        }
    
    # Remove self from peers
    peers.pop(node_id, None)
    
    print(f"[{node_id}] 🚀 Starting Raft node on port {port}")
    print(f"[{node_id}] Peers: {list(peers.keys())}")
    
    # Create and start Raft node
    node = RaftNode(node_id, peers)
    
    # Start FastAPI server
    print(f"[{node_id}] ✅ Raft node ready. Listening on port {port}")
    node.serve(port)

if __name__ == "__main__":
    main()

