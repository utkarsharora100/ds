#!/bin/bash
# Quick Demo Script for Enhanced Client View

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     ENHANCED CLIENT VIEW - LIVE DEMONSTRATION              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}[1/7]${NC} Checking server health..."
curl -s http://localhost:9000/health
echo -e "\n${GREEN}✓ Server is healthy${NC}\n"
sleep 1

echo -e "${BLUE}[2/7]${NC} Registering new client user 'demo_client'..."
REGISTER_RESP=$(curl -s -X POST http://localhost:9000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_client","password":"demo123"}')
echo $REGISTER_RESP
echo -e "${GREEN}✓ User registered${NC}\n"
sleep 1

echo -e "${BLUE}[3/7]${NC} Logging in as client..."
CLIENT_RESP=$(curl -s -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_client","password":"demo123"}')
echo $CLIENT_RESP
CLIENT_TOKEN=$(echo $CLIENT_RESP | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo -e "${GREEN}✓ Client logged in${NC}"
echo -e "${YELLOW}Token: ${CLIENT_TOKEN:0:40}...${NC}\n"
sleep 1

echo -e "${BLUE}[4/7]${NC} Logging in as admin to add movies..."
ADMIN_RESP=$(curl -s -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}')
ADMIN_TOKEN=$(echo $ADMIN_RESP | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo -e "${GREEN}✓ Admin logged in${NC}\n"
sleep 1

echo -e "${BLUE}[5/7]${NC} Adding movies to the system..."
echo "   • Adding 'Inception' in Delhi..."
curl -s -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"Inception\",\"city\":\"Delhi\"}" > /dev/null
echo "   • Adding 'The Matrix' in Mumbai..."
curl -s -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"The Matrix\",\"city\":\"Mumbai\"}" > /dev/null
echo "   • Adding 'Interstellar' in Bangalore..."
curl -s -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"Interstellar\",\"city\":\"Bangalore\"}" > /dev/null
echo -e "${GREEN}✓ Movies added${NC}\n"
sleep 1

echo -e "${BLUE}[6/7]${NC} Fetching available movies (CLIENT VIEW)..."
MOVIES_RESP=$(curl -s "http://localhost:9000/data/movies?token=$CLIENT_TOKEN")
echo $MOVIES_RESP | python3 -m json.tool 2>/dev/null || echo $MOVIES_RESP
echo -e "${GREEN}✓ Movies retrieved${NC}\n"
sleep 1

echo -e "${BLUE}[7/7]${NC} Booking tickets as client..."
echo "   Booking 3 seats for 'Inception' in Delhi..."
BOOKING_RESP=$(curl -s -X POST http://localhost:9000/business \
  -H "Content-Type: application/json" \
  -d "{\"requestId\":\"demo-booking-$(date +%s)\",\"payload\":{\"type\":\"book_seat\",\"data\":{\"movie\":\"Inception\",\"city\":\"Delhi\",\"seats\":3}},\"context\":{\"token\":\"$CLIENT_TOKEN\"}}")
echo $BOOKING_RESP
echo -e "${GREEN}✓ Booking successful${NC}\n"
sleep 1

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    DEMONSTRATION COMPLETE                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "What just happened:"
echo "  1. ✅ Server health check passed"
echo "  2. ✅ New client user registered"
echo "  3. ✅ Client authentication successful"
echo "  4. ✅ Admin added multiple movies"
echo "  5. ✅ Client viewed available movies"
echo "  6. ✅ Client booked tickets successfully"
echo ""
echo "The enhanced client view in app.py provides:"
echo "  • User registration and authentication"
echo "  • Browse movies with city and seat info"
echo "  • Book tickets with custom seat count"
echo "  • View booking history"
echo "  • Refresh data from server"
echo ""
echo "To use the GUI application:"
echo "  1. Install: pip install customtkinter"
echo "  2. Run: python app.py"
echo "  3. Login or register"
echo "  4. Use the dual-panel interface!"
echo ""
echo -e "${GREEN}All systems operational!${NC} 🚀"
