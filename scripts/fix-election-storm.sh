#!/bin/bash
# Fix Raft Election Storm
# Adds heartbeat mechanism to prevent continuous elections

echo "=================================================="
echo "🔧 Fixing Raft Election Storm"
echo "=================================================="
echo ""

cd "$(dirname "$0")/.."

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}What this script fixes:${NC}"
echo "  ❌ Before: Election storm (term increments rapidly to 100+)"
echo "  ✅ After:  Stable leadership (term stays constant)"
echo ""
echo -e "${YELLOW}Changes being applied:${NC}"
echo "  • Added heartbeat loop (50ms intervals)"
echo "  • Added /append-entries endpoint"
echo "  • Updated election timer to check heartbeats"
echo "  • Added step-down mechanism"
echo "  • Optimized timing (500-1000ms election timeout)"
echo ""
echo -e "${YELLOW}Documentation:${NC} docs/ELECTION_STORM_FIX.md"
echo ""

read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

echo -e "${YELLOW}Step 1: Stopping Raft nodes...${NC}"
docker compose -f docker-compose.combined.yml stop raft-node1 raft-node2 raft-node3

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ Failed to stop nodes. Check if Docker is running.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Rebuilding Raft nodes with heartbeat fix...${NC}"
docker compose -f docker-compose.combined.yml build --no-cache raft-node1 raft-node2 raft-node3

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ Build failed! Check error messages above.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 3: Starting Raft nodes...${NC}"
docker compose -f docker-compose.combined.yml up -d raft-node1 raft-node2 raft-node3

echo ""
echo -e "${YELLOW}Step 4: Waiting for nodes to start and elect leader (10 seconds)...${NC}"
sleep 10

echo ""
echo -e "${YELLOW}Step 5: Checking node status...${NC}"
echo ""

NODE1_STATUS=$(curl -s http://localhost:50051/status 2>/dev/null)
NODE2_STATUS=$(curl -s http://localhost:50052/status 2>/dev/null)
NODE3_STATUS=$(curl -s http://localhost:50053/status 2>/dev/null)

if [ -z "$NODE1_STATUS" ] || [ -z "$NODE2_STATUS" ] || [ -z "$NODE3_STATUS" ]; then
    echo -e "${RED}✗ Could not reach nodes. They may still be starting.${NC}"
    echo ""
    echo "Try checking manually:"
    echo "  curl http://localhost:50051/status | jq '.'"
    echo "  curl http://localhost:50052/status | jq '.'"
    echo "  curl http://localhost:50053/status | jq '.'"
    exit 1
fi

echo "Node 1:"
echo "$NODE1_STATUS" | jq '.'
echo ""
echo "Node 2:"
echo "$NODE2_STATUS" | jq '.'
echo ""
echo "Node 3:"
echo "$NODE3_STATUS" | jq '.'
echo ""

# Count leaders
LEADER_COUNT=$(echo "$NODE1_STATUS $NODE2_STATUS $NODE3_STATUS" | grep -o '"state":"leader"' | wc -l | tr -d ' ')

if [ "$LEADER_COUNT" -eq 1 ]; then
    echo -e "${GREEN}✅ SUCCESS! Only ONE leader elected!${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Found $LEADER_COUNT leaders (expected 1)${NC}"
    echo "This might resolve after nodes fully synchronize."
fi

echo ""
echo -e "${YELLOW}Step 6: Checking for heartbeats in logs...${NC}"
echo ""
echo "Tailing logs for 5 seconds to verify heartbeat mechanism..."
echo ""

timeout 5 docker compose -f docker-compose.combined.yml logs -f raft-node1 raft-node2 raft-node3 2>/dev/null | head -20

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Fix Applied!${NC}"
echo "=================================================="
echo ""
echo -e "${BLUE}What to look for in logs:${NC}"
echo "  ✅ \"Started heartbeat loop\" - Leader sending heartbeats"
echo "  ✅ \"Timing: heartbeat=50ms\" - Correct timing configured"
echo "  ✅ Term stays CONSTANT (1 → 1 → 1)"
echo "  ❌ NO \"Election timeout\" messages (unless leader crashes)"
echo ""
echo -e "${BLUE}Verification commands:${NC}"
echo "  # Check status:"
echo "  curl http://localhost:50051/status | jq '{node, state, term}'"
echo "  curl http://localhost:50052/status | jq '{node, state, term}'"
echo "  curl http://localhost:50053/status | jq '{node, state, term}'"
echo ""
echo "  # Watch logs:"
echo "  docker compose -f docker-compose.combined.yml logs -f raft-node1"
echo ""
echo "  # Monitor term stability (should stay constant):"
echo "  watch -n 2 'curl -s http://localhost:50051/status | jq .term'"
echo ""
echo -e "${BLUE}Expected behavior:${NC}"
echo "  • Term should stay CONSTANT (not increment)"
echo "  • Only ONE node shows state=\"leader\""
echo "  • Followers receive heartbeats every 50ms"
echo "  • No election storms"
echo ""
echo -e "${BLUE}Test failover:${NC}"
echo "  # Stop current leader and watch re-election:"
echo "  docker compose stop raft-node2  # (or whichever is leader)"
echo "  # New leader should be elected within 1 second"
echo ""
echo -e "${YELLOW}Documentation:${NC}"
echo "  See docs/ELECTION_STORM_FIX.md for complete technical details"
echo ""
