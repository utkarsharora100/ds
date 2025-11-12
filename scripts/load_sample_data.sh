#!/bin/bash
# Load Sample Movie Data
# Populates the database with sample movies across multiple cities

set -e

echo "=========================================="
echo "  Sample Movie Data Loader"
echo "=========================================="
echo ""

APP_URL="http://localhost:9000"
ADMIN_USER="admin"
ADMIN_PASS="123"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "This script will add 15 sample movies to the database."
echo ""

# Check for --force flag
if [ "$1" != "--force" ]; then
    read -p "Continue? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "Sample data loading cancelled."
        exit 0
    fi
fi

echo ""
echo -e "${BLUE}Loading sample movies...${NC}"
echo ""

# Login as admin to get token
echo "Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$APP_URL/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$ADMIN_USER\",\"password\":\"$ADMIN_PASS\"}")

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('token', ''))" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to login as admin${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ Admin logged in successfully${NC}"
echo ""

# Sample movies with varied seat counts
declare -a MOVIES=(
    "Inception:New York:120"
    "Inception:Los Angeles:100"
    "The Dark Knight:New York:150"
    "The Dark Knight:Chicago:80"
    "Interstellar:San Francisco:90"
    "Interstellar:Boston:110"
    "Avengers Endgame:New York:200"
    "Avengers Endgame:Los Angeles:180"
    "Spider-Man:Chicago:100"
    "Spider-Man:Miami:75"
    "Joker:New York:85"
    "Joker:Seattle:95"
    "Parasite:San Francisco:70"
    "Dune:Los Angeles:130"
    "Oppenheimer:New York:160"
)

SUCCESS_COUNT=0
FAIL_COUNT=0

for MOVIE_DATA in "${MOVIES[@]}"; do
    # Split by colon
    IFS=':' read -r MOVIE CITY SEATS <<< "$MOVIE_DATA"
    
    echo -e "${YELLOW}Adding: $MOVIE | $CITY | $SEATS seats${NC}"
    
    # Create request with token
    REQUEST=$(cat <<EOF
{
  "token": "$TOKEN",
  "movie": "$MOVIE",
  "city": "$CITY",
  "seats": $SEATS
}
EOF
)
    
    # Make API call to /add_movie endpoint
    RESPONSE=$(curl -s -X POST "$APP_URL/add_movie" \
      -H "Content-Type: application/json" \
      -d "$REQUEST")
    
    # Check if successful
    if echo "$RESPONSE" | grep -q "success"; then
        echo -e "${GREEN}✅ Added successfully${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}❌ Failed to add${NC}"
        echo "Response: $RESPONSE"
        ((FAIL_COUNT++))
    fi
    echo ""
    
    # Small delay to not overwhelm the server
    sleep 0.2
done

echo "=========================================="
echo ""
echo -e "${GREEN}Sample data loading complete!${NC}"
echo ""
echo "Summary:"
echo "  ✅ Successfully added: $SUCCESS_COUNT movies"
if [ $FAIL_COUNT -gt 0 ]; then
    echo "  ❌ Failed to add: $FAIL_COUNT movies"
fi
echo ""
echo "=========================================="
echo ""

# Verify by fetching all movies
echo "Verifying movies in database..."
ALL_MOVIES=$(curl -s "$APP_URL/data/movies")
TOTAL_COUNT=$(echo "$ALL_MOVIES" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('movies', [])))")

echo "Total movies in database: $TOTAL_COUNT"
echo ""

if [ $TOTAL_COUNT -gt 0 ]; then
    echo "Sample movies by city:"
    echo "$ALL_MOVIES" | python3 -c "
import sys, json
from collections import defaultdict

data = json.load(sys.stdin)
movies = data.get('movies', [])

by_city = defaultdict(list)
for movie in movies:
    parts = movie.split('|')
    if len(parts) >= 3:
        name = parts[0].strip()
        city = parts[1].strip()
        seats = parts[2].strip().replace('Available Seats: ', '')
        by_city[city].append(f'{name} ({seats} seats)')

for city, movie_list in sorted(by_city.items()):
    print(f'  {city}: {len(movie_list)} movies')
    for movie in movie_list:
        print(f'    - {movie}')
"
fi

echo ""
echo "=========================================="
echo "You can now:"
echo "  1. Open admin dashboard to view all movies"
echo "  2. Open client dashboard to book tickets"
echo "  3. Run: python3 app_multi.py (for multi-window demo)"
echo "=========================================="
