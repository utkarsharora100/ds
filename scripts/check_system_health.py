#!/usr/bin/env python3
"""
Python-based health check script for the Distributed Movie Booking System.
This script is intended to be run inside the app-server container.
"""

import requests
import sys
import os

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    NC = '\033[0m' # No Color

def check_service(name, url, timeout=3):
    """Checks a single service endpoint."""
    print(f"Checking {name:<20} ... ", end="")
    sys.stdout.flush()
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ OK{Colors.NC}")
            return True, response.json()
        else:
            print(f"{Colors.RED}❌ FAILED (HTTP: {response.status_code}){Colors.NC}")
            return False, None
    except requests.RequestException as e:
        print(f"{Colors.RED}❌ FAILED (Unreachable){Colors.NC}")
        return False, None

def main():
    """Main health check routine."""
    print("========================================")
    print("    Distributed System Health Check")
    print("========================================")
    print()

    all_ok = True
    
    # --- Service Health Checks ---
    print("--- API Endpoints ---")
    
    # Use localhost by default, which works when this script is run from the host.
    # If RUN_CONTEXT is 'docker', use Docker service names. This makes the script flexible.
    run_context = os.environ.get("RUN_CONTEXT", "local")
    
    llm_host = "llm-server" if run_context == "docker" else "localhost"
    raft1_host = "raft-node1" if run_context == "docker" else "localhost"
    raft2_host = "raft-node2" if run_context == "docker" else "localhost"
    raft3_host = "raft-node3" if run_context == "docker" else "localhost"
    
    services_to_check = [
        ("Application Server", "http://localhost:9000/health"),
        ("LLM Server", f"http://{llm_host}:8500/health"),
        ("Raft Node 1", f"http://{raft1_host}:50051/status"),
        ("Raft Node 2", f"http://{raft2_host}:50052/status"),
        ("Raft Node 3", f"http://{raft3_host}:50053/status"),
    ]
    
    raft_nodes_status = []
    for name, url in services_to_check:
        ok, data = check_service(name, url)
        if not ok:
            all_ok = False
        if "Raft Node" in name and ok:
            raft_nodes_status.append(data)

    print()

    # --- Raft Leader Verification ---
    print("--- Raft Consensus ---")
    leader_id = None
    for status in raft_nodes_status:
        if status.get("state") == "leader":
            leader_id = status.get("node_id")
            break
            
    if leader_id:
        print(f"{Colors.GREEN}✅ Leader elected: {leader_id}{Colors.NC}")
    else:
        print(f"{Colors.RED}❌ No leader found in the Raft cluster.{Colors.NC}")
        all_ok = False
        
    print()
    print("========================================")
    if all_ok:
        print(f"          {Colors.GREEN}✅ System Healthy{Colors.NC}")
    else:
        print(f"          {Colors.RED}❌ System Unhealthy{Colors.NC}")
    print("========================================")

if __name__ == "__main__":
    main()