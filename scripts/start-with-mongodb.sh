#!/bin/bash
# Start Movie Booking System with MongoDB
# This script rebuilds and starts all services with MongoDB

echo "=================================================="
echo "🎬 Movie Booking System - MongoDB Edition"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Which setup are you using?${NC}"
echo "1) Web UI (docker-compose.combined.yml)"
echo "2) Desktop GUI (docker-compose.yml)"
echo ""
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo -e "${YELLOW}→ Using Web UI setup...${NC}"
    COMPOSE_FILE="docker-compose.combined.yml"
    SERVICE="movie-booking-app"
    ACCESS_URL="http://localhost:3000"
elif [ "$choice" = "2" ]; then
    echo ""
    echo -e "${YELLOW}→ Using Desktop GUI setup...${NC}"
    COMPOSE_FILE="docker-compose.yml"
    SERVICE="app-server"
    ACCESS_URL="python app.py (after this script completes)"
else
    echo -e "${RED}Invalid choice. Exiting.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 1: Stopping existing containers...${NC}"
docker-compose -f "$COMPOSE_FILE" down

echo ""
echo -e "${YELLOW}Step 2: Pulling MongoDB image...${NC}"
docker pull mongo:7.0

echo ""
echo -e "${YELLOW}Step 3: Building services (this may take 2-3 minutes)...${NC}"
docker-compose -f "$COMPOSE_FILE" build --no-cache "$SERVICE"

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ Build failed! Check the error messages above.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 4: Starting all services...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d

echo ""
echo -e "${YELLOW}Step 5: Waiting for services to be ready...${NC}"
echo "Waiting for MongoDB..."
sleep 10

echo "Waiting for Application Server..."
sleep 10

echo ""
echo -e "${YELLOW}Step 6: Checking service status...${NC}"
docker-compose -f "$COMPOSE_FILE" ps

echo ""
echo -e "${YELLOW}Step 7: Verifying MongoDB...${NC}"
docker exec movie-booking-mongodb mongosh --eval "db.adminCommand('ping')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ MongoDB is running${NC}"
else
    echo -e "${RED}✗ MongoDB health check failed${NC}"
fi

echo ""
echo -e "${YELLOW}Step 8: Verifying Application Server...${NC}"
curl -s http://localhost:9000/health | grep -q "mongodb"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Application Server is running with MongoDB${NC}"
else
    echo -e "${RED}✗ Application Server health check failed${NC}"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✅ System Started Successfully!${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}Access Information:${NC}"
echo ""
if [ "$choice" = "1" ]; then
    echo "  Web UI:     http://localhost:3000"
    echo "  Backend:    http://localhost:9000"
    echo "  MongoDB:    mongodb://localhost:27017"
    echo ""
    echo -e "${GREEN}Open your browser and go to: http://localhost:3000${NC}"
else
    echo "  Backend:    http://localhost:9000"
    echo "  MongoDB:    mongodb://localhost:27017"
    echo ""
    echo -e "${GREEN}Now run: python app.py${NC}"
fi
echo ""
echo -e "${YELLOW}Default Login Credentials:${NC}"
echo "  Username: admin"
echo "  Password: 123"
echo ""
echo -e "${YELLOW}IMPORTANT - Clear Your Browser Cache:${NC}"
echo "  Windows/Linux: Ctrl + Shift + R"
echo "  Mac:           Cmd + Shift + R"
echo ""
echo -e "${BLUE}View logs:${NC} docker-compose -f $COMPOSE_FILE logs -f"
echo -e "${BLUE}Stop services:${NC} docker-compose -f $COMPOSE_FILE down"
echo ""
echo "📖 Read MONGODB_MIGRATION_GUIDE.md for more details"
echo ""
