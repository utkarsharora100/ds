#!/bin/bash
# Quick Fix for MongoDB Import Error
# This script rebuilds the container with the corrected import

echo "=================================================="
echo "🔧 Fixing MongoDB Import Error"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Stopping the container...${NC}"
docker-compose -f docker-compose.combined.yml stop movie-booking-app

echo ""
echo -e "${YELLOW}Step 2: Rebuilding with fixed import...${NC}"
docker-compose -f docker-compose.combined.yml build --no-cache movie-booking-app

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ Build failed! Check error messages above.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 3: Starting the container...${NC}"
docker-compose -f docker-compose.combined.yml up -d movie-booking-app

echo ""
echo -e "${YELLOW}Step 4: Waiting for startup (15 seconds)...${NC}"
sleep 15

echo ""
echo -e "${YELLOW}Step 5: Checking logs...${NC}"
docker logs movie-booking-combined --tail=20

echo ""
echo -e "${YELLOW}Step 6: Testing health endpoint...${NC}"
curl -s http://localhost:9000/health

echo ""
echo ""
echo "=================================================="
echo -e "${GREEN}✅ Fix Applied!${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}Now test login:${NC}"
echo "1. Open: http://localhost:3000"
echo "2. Clear browser cache: Ctrl+Shift+R (or Cmd+Shift+R on Mac)"
echo "3. Login: admin / 123"
echo ""
echo -e "${YELLOW}View logs:${NC} docker logs movie-booking-combined -f"
echo ""
