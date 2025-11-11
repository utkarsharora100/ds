#!/bin/bash

# Quick Start Script for Distributed Movie Booking System
# This script helps you start all components easily

echo "================================================"
echo "  Distributed Movie Booking System - Quick Start"
echo "================================================"
echo ""

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Function to start a component in a new terminal
start_component() {
    local name=$1
    local command=$2
    
    echo "Starting $name..."
    
    # For Linux with gnome-terminal
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "$command; exec bash"
    # For Linux with xterm
    elif command -v xterm &> /dev/null; then
        xterm -e "$command; bash" &
    # For macOS
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        osascript -e "tell app \"Terminal\" to do script \"cd $(pwd) && $command\""
    else
        echo "Could not detect terminal emulator. Please run manually: $command"
    fi
    
    sleep 2
}

echo "Choose an option:"
echo "1. Full System (GUI + Application Server + 3 Raft Nodes)"
echo "2. Application Server Only"
echo "3. Raft Nodes Only (3 nodes)"
echo "4. GUI Only"
echo "5. LLM Server Only"
echo "6. Stop All Components"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "Starting Full System..."
        echo ""
        
        # Start Application Server
        start_component "Application Server" "python Application_server/Application_server.py"
        
        # Start Raft Nodes
        start_component "Raft Node 1" "python main.py node1"
        start_component "Raft Node 2" "python main.py node2"
        start_component "Raft Node 3" "python main.py node3"
        
        echo "Waiting for services to initialize (5 seconds)..."
        sleep 5
        
        # Start GUI
        echo "Starting GUI Application..."
        python app.py
        ;;
        
    2)
        echo ""
        echo "Starting Application Server..."
        python Application_server/Application_server.py
        ;;
        
    3)
        echo ""
        echo "Starting Raft Nodes..."
        start_component "Raft Node 1" "python main.py node1"
        start_component "Raft Node 2" "python main.py node2"
        start_component "Raft Node 3" "python main.py node3"
        echo "All Raft nodes started. Leader election will occur automatically."
        ;;
        
    4)
        echo ""
        echo "Starting GUI..."
        python app.py
        ;;
        
    5)
        echo ""
        echo "Starting LLM Server..."
        python -m uvicorn llm.llm_server:app --host 0.0.0.0 --port 8500
        ;;
        
    6)
        echo ""
        echo "Stopping all components..."
        
        # Kill all related processes
        pkill -f "Application_server.py" 2>/dev/null
        pkill -f "main.py node" 2>/dev/null
        pkill -f "llm_server" 2>/dev/null
        
        # Kill by port
        lsof -ti:9000 | xargs kill -9 2>/dev/null
        lsof -ti:50051 | xargs kill -9 2>/dev/null
        lsof -ti:50052 | xargs kill -9 2>/dev/null
        lsof -ti:50053 | xargs kill -9 2>/dev/null
        lsof -ti:8500 | xargs kill -9 2>/dev/null
        
        echo "All components stopped."
        ;;
        
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
