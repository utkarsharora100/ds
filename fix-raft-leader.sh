#!/bin/bash
# Fix Raft Leader Election Bug
# This script rebuilds Raft nodes with proper leader election

echo "=================================================="
echo "🔧 Fixing Raft Leader Election"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Stopping Raft nodes...${NC}"
docker compose -f docker-compose.combined.yml stop raft-node1 raft-node2 raft-node3

echo ""
echo -e "${YELLOW}Step 2: Rebuilding Raft nodes with fixed election...${NC}"
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
echo -e "${YELLOW}Step 4: Waiting for nodes to start (10 seconds)...${NC}"
sleep 10

echo ""
echo -e "${YELLOW}Step 5: Checking node status...${NC}"
echo ""
echo "Node 1:"
curl -s http://localhost:50051/status | jq '.'
echo ""
echo "Node 2:"
curl -s http://localhost:50052/status | jq '.'
echo ""
echo "Node 3:"
curl -s http://localhost:50053/status | jq '.'

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Fix Applied!${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}Expected: Only ONE node should show state=leader${NC}"
echo ""
echo -e "${YELLOW}View logs:${NC} docker compose -f docker-compose.combined.yml logs -f raft-node1"
echo ""
