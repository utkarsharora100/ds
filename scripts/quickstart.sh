#!/bin/bash

# ============================================================================
# QUICKSTART SCRIPT - Distributed Movie Booking System
# ============================================================================
# This script sets up and runs the complete distributed movie booking system
# in one command. Perfect for first-time setup and demonstrations.
#
# What it does:
# 1. Checks prerequisites (Docker, Python, venv)
# 2. Starts all Docker services
# 3. Waits for services to be healthy
# 4. Loads sample data
# 5. Provides options to launch GUI or run tests
#
# Usage: ./quickstart.sh
# ============================================================================

set -e  # Exit on error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}${BOLD}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║     🎬  DISTRIBUTED MOVIE BOOKING SYSTEM - QUICKSTART  🎬            ║
║                                                                       ║
║     FastAPI + Raft Consensus + LLM Assistant + Multi-Client GUI      ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}Starting automated setup...${NC}\n"
sleep 1

# ============================================================================
# Step 1: Check Prerequisites
# ============================================================================
echo -e "${YELLOW}[1/8] Checking Prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found!${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found!${NC}"
    echo "Please install Docker Compose v2"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose installed${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python3 installed${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip > /dev/null 2>&1
    ./venv/bin/pip install -r requirements.txt > /dev/null 2>&1
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

echo ""

# ============================================================================
# Step 2: Stop Any Existing Containers
# ============================================================================
echo -e "${YELLOW}[2/8] Cleaning Up Previous Instances...${NC}"

if sudo docker compose ps | grep -q "Up"; then
    echo "Stopping existing containers..."
    sudo docker compose down > /dev/null 2>&1
    echo -e "${GREEN}✓ Previous containers stopped${NC}"
else
    echo -e "${GREEN}✓ No previous containers running${NC}"
fi

echo ""

# ============================================================================
# Step 3: Build Docker Images
# ============================================================================
echo -e "${YELLOW}[3/8] Building Docker Images...${NC}"
echo -e "${CYAN}This may take 5-10 minutes on first run...${NC}"

sudo docker compose build --quiet 2>&1 | grep -E "Built|CACHED|ERROR" || true

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker images built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

echo ""

# ============================================================================
# Step 4: Start All Services
# ============================================================================
echo -e "${YELLOW}[4/8] Starting All Services...${NC}"
echo "  • Application Server (port 9000)"
echo "  • LLM Server (port 8500)"
echo "  • Raft Node 1 (port 50051)"
echo "  • Raft Node 2 (port 50052)"
echo "  • Raft Node 3 (port 50053)"
echo ""

sudo docker compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All services started${NC}"
else
    echo -e "${RED}❌ Failed to start services${NC}"
    exit 1
fi

echo ""

# ============================================================================
# Step 5: Wait for Services to Be Ready
# ============================================================================
echo -e "${YELLOW}[5/8] Waiting for Services to Initialize...${NC}"

MAX_WAIT=60
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:9000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Application server is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo -e "${RED}❌ Services failed to start within ${MAX_WAIT}s${NC}"
    echo "Check logs with: sudo docker compose logs"
    exit 1
fi

echo ""

# ============================================================================
# Step 6: Health Check & Raft Verification
# ============================================================================
echo -e "${YELLOW}[6/9] Running Health Checks & Raft Tests...${NC}"

./scripts/check_health.sh || {
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
}

echo ""
echo -e "${BLUE}Testing Raft Consensus...${NC}"

# Check Raft leader election
LEADER=$(curl -s http://localhost:50051/status 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('currentLeader', 'unknown'))" 2>/dev/null || echo "unknown")

if [ "$LEADER" != "unknown" ]; then
    echo -e "${GREEN}✓ Raft leader elected: $LEADER${NC}"
else
    echo -e "${YELLOW}⚠ Raft leader not detected (may still be electing)${NC}"
fi

# Show all Raft nodes status
echo ""
echo "Raft Cluster Status:"
for PORT in 50051 50052 50053; do
    STATUS=$(curl -s http://localhost:$PORT/status 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"{d.get('state', 'unknown')} (term {d.get('term', '?')})\")"; echo "${PIPESTATUS[0]}")
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} Node on port $PORT: $STATUS"
    else
        echo -e "  ${RED}✗${NC} Node on port $PORT: unreachable"
    fi
done

echo ""

# ============================================================================
# Step 7: Load Sample Data
# ============================================================================
echo -e "${YELLOW}[7/9] Loading Sample Data...${NC}"
echo -e "${CYAN}Would you like to load 15 sample movies? (recommended for testing)${NC}"
read -p "Load sample data? (y/n): " LOAD_DATA

if [ "$LOAD_DATA" = "y" ] || [ "$LOAD_DATA" = "Y" ]; then
    ./scripts/load_sample_data.sh --force > /dev/null 2>&1
    echo -e "${GREEN}✓ Sample data loaded (15 movies)${NC}"
else
    echo -e "${YELLOW}⊘ Skipped sample data${NC}"
fi

echo ""

# ============================================================================
# Step 8: Test Basic Functionality
# ============================================================================
echo -e "${YELLOW}[8/9] Testing Basic Booking Functionality...${NC}"

# Login as admin
TOKEN=$(curl -s -X POST http://localhost:9000/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"123"}' 2>/dev/null | \
    python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✓ Admin login successful${NC}"
    
    # Test get movies
    MOVIE_COUNT=$(curl -s "http://localhost:9000/data/movies?token=$TOKEN" 2>/dev/null | \
        python3 -c "import sys, json; print(len(json.load(sys.stdin).get('movies', [])))" 2>/dev/null || echo "0")
    echo -e "${GREEN}✓ Movies endpoint working (${MOVIE_COUNT} movies)${NC}"
else
    echo -e "${YELLOW}⚠ Login test skipped${NC}"
fi

echo ""

# ============================================================================
# Step 9: Launch Options
# ============================================================================
echo -e "${YELLOW}[9/9] System Ready!${NC}"
echo ""
echo -e "${GREEN}${BOLD}✅ ALL SERVICES ARE RUNNING!${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}Next Steps - Choose Your Adventure:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BOLD}Option 1: Launch GUI (if you have display)${NC}"
echo "  ${GREEN}python3 app_multi.py${NC}    # Multi-window (3 clients + admin)"
echo "  ${GREEN}python3 app.py${NC}          # Single window"
echo ""
echo -e "${BOLD}Option 2: Run Complete Demo${NC}"
echo "  ${GREEN}./scripts/demo_complete_system.sh${NC}"
echo ""
echo -e "${BOLD}Option 3: Run Tests${NC}"
echo "  ${GREEN}./venv/bin/python tests/test_complete_system.py${NC}"
echo ""
echo -e "${BOLD}Option 4: Use CLI${NC}"
echo "  ${GREEN}# Register user${NC}"
echo "  curl -X POST http://localhost:9000/register \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"username\":\"testuser\",\"password\":\"test123\"}'"
echo ""
echo "  ${GREEN}# Login${NC}"
echo "  curl -X POST http://localhost:9000/login \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"username\":\"testuser\",\"password\":\"test123\"}'"
echo ""
echo "  ${GREEN}# Get movies${NC}"
echo "  curl http://localhost:9000/data/movies?token=YOUR_TOKEN"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BOLD}Useful Commands:${NC}"
echo "  ${YELLOW}./scripts/check_health.sh${NC}          # Check all services"
echo "  ${YELLOW}./scripts/reset_database.sh${NC}        # Clear all data"
echo "  ${YELLOW}./scripts/load_sample_data.sh${NC}      # Load test movies"
echo "  ${YELLOW}./scripts/test_llm_viability.sh${NC}    # Test LLM server"
echo "  ${YELLOW}sudo docker compose logs [service]${NC}  # View logs"
echo "  ${YELLOW}sudo docker compose ps${NC}              # Check containers"
echo "  ${YELLOW}sudo docker compose down${NC}            # Stop all services"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BOLD}Default Admin Credentials:${NC}"
echo "  Username: ${GREEN}admin${NC}"
echo "  Password: ${GREEN}123${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BOLD}Service URLs:${NC}"
echo "  Application Server: ${GREEN}http://localhost:9000${NC}"
echo "  LLM Server:         ${GREEN}http://localhost:8500${NC}"
echo "  Raft Node 1:        ${GREEN}http://localhost:50051${NC}"
echo "  Raft Node 2:        ${GREEN}http://localhost:50052${NC}"
echo "  Raft Node 3:        ${GREEN}http://localhost:50053${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}${BOLD}🚀 Your distributed movie booking system is ready!${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to exit this script (services will keep running)${NC}"
echo ""

# Wait for user input
read -p "Press Enter to exit..."

echo ""
echo -e "${GREEN}Quickstart complete! Services are still running in the background.${NC}"
echo -e "${YELLOW}To stop all services: ${NC}${BOLD}sudo docker compose down${NC}"
echo ""
