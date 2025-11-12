#!/bin/bash
# Fix LLM Service Timeout Issue
# Increases timeout for CPU inference and adds better error handling

echo "=================================================="
echo "🔧 Fixing LLM Service Timeout"
echo "=================================================="
echo ""

cd "$(dirname "$0")/.."

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Issue:${NC}"
echo "  ❌ LLM service timing out (10 second timeout)"
echo "  ❌ CPU inference takes 30-60 seconds"
echo ""
echo -e "${YELLOW}Solution:${NC}"
echo "  ✅ Increased timeout to 60 seconds"
echo "  ✅ Added better error handling and logging"
echo "  ✅ User-friendly timeout messages"
echo ""

read -p "Press Enter to apply fix or Ctrl+C to cancel..."
echo ""

echo -e "${YELLOW}Step 1: Stopping application server...${NC}"
docker compose -f docker-compose.combined.yml stop movie-booking-app

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ Failed to stop container. Check if Docker is running.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Rebuilding application server with increased timeout...${NC}"
docker compose -f docker-compose.combined.yml build --no-cache movie-booking-app

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ Build failed! Check error messages above.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 3: Starting application server...${NC}"
docker compose -f docker-compose.combined.yml up -d movie-booking-app

echo ""
echo -e "${YELLOW}Step 4: Waiting for services to start (10 seconds)...${NC}"
sleep 10

echo ""
echo -e "${YELLOW}Step 5: Checking LLM service status...${NC}"
echo ""

# Check backend health
BACKEND_HEALTH=$(curl -s http://localhost:9000/health 2>/dev/null)
if [ -n "$BACKEND_HEALTH" ]; then
    echo "Backend: ✅ Running"
    echo "$BACKEND_HEALTH" | jq '.'
else
    echo "Backend: ❌ Not responding"
fi

echo ""

# Check LLM health through proxy
LLM_HEALTH=$(curl -s http://localhost:9000/proxy/llm/health 2>/dev/null)
if [ -n "$LLM_HEALTH" ]; then
    echo "LLM Service (via proxy): ✅ Accessible"
    echo "$LLM_HEALTH" | jq '.'
else
    echo "LLM Service: ⚠️ Not accessible yet (may still be loading model)"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Fix Applied!${NC}"
echo "=================================================="
echo ""
echo -e "${BLUE}What was changed:${NC}"
echo "  • Timeout: 10 seconds → 60 seconds"
echo "  • Added logging for LLM proxy requests"
echo "  • Better error messages for users"
echo ""
echo -e "${BLUE}Testing the AI Assistant:${NC}"
echo "  1. Open http://localhost:3000"
echo "  2. Login (admin/123)"
echo "  3. Click AI Assistant (robot icon, bottom right)"
echo "  4. Ask a question: \"what can you do?\""
echo "  5. Wait 30-60 seconds for first response (CPU is slow!)"
echo ""
echo -e "${YELLOW}⚠️ Important Notes:${NC}"
echo "  • First request takes LONGEST (model warm-up)"
echo "  • CPU inference: 30-60 seconds per response"
echo "  • Subsequent requests: 15-30 seconds"
echo "  • For faster responses, use GPU (if available)"
echo ""
echo -e "${BLUE}Test via command line:${NC}"
echo "  # Quick test (should get response in 30-60 seconds):"
echo "  curl -X POST http://localhost:9000/proxy/llm/ask \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"question\": \"What can you help me with?\"}' \\"
echo "    --max-time 65"
echo ""
echo -e "${BLUE}View logs:${NC}"
echo "  # Backend logs (will show LLM proxy activity):"
echo "  docker compose -f docker-compose.combined.yml logs -f movie-booking-app"
echo ""
echo "  # LLM server logs:"
echo "  docker compose -f docker-compose.combined.yml logs -f llm-server"
echo ""
echo -e "${BLUE}If still not working:${NC}"
echo "  1. Check if LLM container is running:"
echo "     docker ps | grep llm"
echo ""
echo "  2. Check LLM logs for errors:"
echo "     docker compose -f docker-compose.combined.yml logs llm-server | tail -50"
echo ""
echo "  3. Restart LLM server:"
echo "     docker compose -f docker-compose.combined.yml restart llm-server"
echo ""
echo "  4. If model failed to load, rebuild LLM:"
echo "     docker compose -f docker-compose.combined.yml build --no-cache llm-server"
echo "     docker compose -f docker-compose.combined.yml up -d llm-server"
echo ""
