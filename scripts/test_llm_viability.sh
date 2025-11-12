#!/bin/bash
# Test LLM Server Viability
# Tests all LLM endpoints to ensure the AI assistant is working

set -e

echo "=========================================="
echo "  LLM Server Viability Test"
echo "=========================================="
echo ""

LLM_URL="http://localhost:8500"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
echo "GET $LLM_URL/health"
echo ""

HEALTH_RESPONSE=$(curl -s $LLM_URL/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ LLM Server is healthy${NC}"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ LLM Server is not healthy${NC}"
    echo "$HEALTH_RESPONSE"
    exit 1
fi

echo ""
echo "=========================================="
echo ""

# Test 2: Simple Question (Ask endpoint)
echo -e "${YELLOW}Test 2: Ask Endpoint - Simple Question${NC}"
echo "Question: How do I book a movie ticket?"
echo ""

ASK_REQUEST='{
  "question": "How do I book a movie ticket?"
}'

ASK_RESPONSE=$(curl -s -X POST $LLM_URL/ask \
  -H "Content-Type: application/json" \
  -d "$ASK_REQUEST")

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Ask endpoint working${NC}"
    echo ""
    echo "Response:"
    echo "$ASK_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Ask endpoint failed${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo ""

# Test 3: Chat endpoint with conversation history
echo -e "${YELLOW}Test 3: Chat Endpoint - Conversation${NC}"
echo "User: What cities are available for booking?"
echo ""

CHAT_REQUEST='{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant for a movie booking system."
    },
    {
      "role": "user",
      "content": "What cities are available for booking?"
    }
  ]
}'

CHAT_RESPONSE=$(curl -s -X POST $LLM_URL/chat \
  -H "Content-Type: application/json" \
  -d "$CHAT_REQUEST")

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Chat endpoint working${NC}"
    echo ""
    echo "Response:"
    echo "$CHAT_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Chat endpoint failed${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo ""

# Test 4: FAQ Questions
echo -e "${YELLOW}Test 4: Multiple FAQ Questions${NC}"
echo ""

QUESTIONS=(
  "How do I register as a new user?"
  "What is the admin password?"
  "Can I cancel my booking?"
  "How do refunds work?"
)

for QUESTION in "${QUESTIONS[@]}"; do
    echo -e "${YELLOW}Q: $QUESTION${NC}"
    
    FAQ_REQUEST=$(cat <<EOF
{
  "question": "$QUESTION"
}
EOF
)
    
    FAQ_RESPONSE=$(curl -s -X POST $LLM_URL/ask \
      -H "Content-Type: application/json" \
      -d "$FAQ_REQUEST")
    
    if [ $? -eq 0 ]; then
        ANSWER=$(echo "$FAQ_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['answer'][:150] + '...')")
        echo -e "${GREEN}A: $ANSWER${NC}"
    else
        echo -e "${RED}Failed to get answer${NC}"
    fi
    echo ""
done

echo "=========================================="
echo ""

# Test 5: Multi-turn conversation
echo -e "${YELLOW}Test 5: Multi-turn Conversation${NC}"
echo ""

CONVERSATION_REQUEST='{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant for a movie booking system."
    },
    {
      "role": "user",
      "content": "I want to book a movie"
    },
    {
      "role": "assistant",
      "content": "Great! I can help you book a movie ticket. What movie would you like to watch?"
    },
    {
      "role": "user",
      "content": "How many seats are available?"
    }
  ]
}'

echo "User: I want to book a movie"
echo "Assistant: Great! I can help you book a movie ticket..."
echo "User: How many seats are available?"
echo ""

CONVERSATION_RESPONSE=$(curl -s -X POST $LLM_URL/chat \
  -H "Content-Type: application/json" \
  -d "$CONVERSATION_REQUEST")

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Multi-turn conversation working${NC}"
    echo ""
    echo "Assistant Response:"
    CONV_ANSWER=$(echo "$CONVERSATION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])")
    echo "$CONV_ANSWER"
else
    echo -e "${RED}❌ Multi-turn conversation failed${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ All LLM tests passed successfully!${NC}"
echo "=========================================="
echo ""
echo "LLM Server is fully operational and ready to assist users."
echo ""
