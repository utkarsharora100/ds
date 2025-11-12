#!/bin/bash
# Quick Fix Script - Rebuild after syntax error fix
# This script rebuilds the frontend container after the app.js fix

echo "=================================================="
echo "🔧 Quick Fix - Rebuilding Frontend"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
elif [ "$choice" = "2" ]; then
    echo ""
    echo -e "${YELLOW}→ Using Desktop GUI setup...${NC}"
    COMPOSE_FILE="docker-compose.yml"
    SERVICE="app-server"
else
    echo -e "${RED}Invalid choice. Exiting.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 1: Stopping containers...${NC}"
docker-compose -f "$COMPOSE_FILE" stop "$SERVICE"

echo ""
echo -e "${YELLOW}Step 2: Rebuilding $SERVICE (no cache)...${NC}"
echo "This may take 1-2 minutes..."
docker-compose -f "$COMPOSE_FILE" build "$SERVICE" --no-cache

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ Build failed! Check the error messages above.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 3: Starting $SERVICE...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d "$SERVICE"

echo ""
echo -e "${YELLOW}Step 4: Waiting for service to be ready...${NC}"
sleep 10

echo ""
echo -e "${YELLOW}Step 5: Checking status...${NC}"
docker-compose -f "$COMPOSE_FILE" ps "$SERVICE"

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Rebuild Complete!${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}IMPORTANT - Clear Your Browser Cache:${NC}"
echo ""
echo "  Windows/Linux: Press Ctrl + Shift + R"
echo "  Mac:           Press Cmd + Shift + R"
echo ""
echo "Or use Incognito/Private window:"
echo "  1. Open new Incognito window (Ctrl+Shift+N or Cmd+Shift+N)"
echo "  2. Go to http://localhost:3000"
echo "  3. Test login"
echo ""
echo -e "${GREEN}Then test your login!${NC}"
echo ""
echo "Test credentials:"
echo "  Admin:  username: admin,  password: 123"
echo "  User:   Create new account via Register button"
echo ""
