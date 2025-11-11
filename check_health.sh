#!/bin/bash

# Health Check Script for Distributed Movie Booking System
# This script checks if all Docker services are running properly

echo "=================================="
echo "  System Health Check"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check service
check_service() {
    local name=$1
    local url=$2
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name OK${NC}"
        return 0
    else
        echo -e "${RED}❌ $name FAILED${NC}"
        return 1
    fi
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi

echo "Checking Docker services..."
echo ""

# Check containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}❌ No services running. Start with: docker-compose up -d${NC}"
    exit 1
fi

# Check each service
check_service "Application Server" "http://localhost:9000/health"
check_service "Raft Node 1" "http://localhost:50051/status"
check_service "Raft Node 2" "http://localhost:50052/status"
check_service "Raft Node 3" "http://localhost:50053/status"
check_service "LLM Server" "http://localhost:8500/health"

echo ""
echo "=================================="

# Check for Raft leader
echo ""
echo "Checking Raft leader election..."
leader_found=false

for port in 50051 50052 50053; do
    response=$(curl -s http://localhost:$port/status)
    if echo "$response" | grep -q '"state":"leader"'; then
        node=$(echo "$response" | grep -o '"node_id":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}✅ Leader elected: $node (port $port)${NC}"
        leader_found=true
        break
    fi
done

if [ "$leader_found" = false ]; then
    echo -e "${RED}❌ No Raft leader found. Wait a few seconds and try again.${NC}"
fi

echo ""
echo "=================================="
echo "  Health Check Complete"
echo "=================================="
