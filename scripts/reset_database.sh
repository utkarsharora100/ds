#!/bin/bash
# Reset Database - Clear all movies and bookings
# Use this to start fresh with a clean database

set -e

echo "=========================================="
echo "  Database Reset Script"
echo "=========================================="
echo ""

APP_URL="http://localhost:9000"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}⚠️  WARNING: This will delete ALL movies and bookings!${NC}"
echo ""

# Check for --force flag
if [ "$1" != "--force" ]; then
    read -p "Are you sure you want to continue? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "Database reset cancelled."
        exit 0
    fi
fi

echo ""
echo "Clearing database..."
echo ""

# Get current movies
echo "Fetching current movies..."
CURRENT_MOVIES=$(curl -s "$APP_URL/data/movies")

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to connect to application server${NC}"
    echo "Make sure the server is running on port 9000"
    exit 1
fi

MOVIE_COUNT=$(echo "$CURRENT_MOVIES" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('movies', [])))")

echo "Found $MOVIE_COUNT movies in database"
echo ""

# Note: The current system uses in-memory database with SQLite
# Restart the container to fully reset
echo -e "${YELLOW}Restarting application server to reset database...${NC}"
sudo docker compose restart app-server

sleep 3

echo ""
echo -e "${GREEN}✅ Database reset complete!${NC}"
echo ""

# Verify empty database
echo "Verifying database is empty..."
NEW_MOVIES=$(curl -s "$APP_URL/data/movies")
NEW_COUNT=$(echo "$NEW_MOVIES" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('movies', [])))")

echo "Current movie count: $NEW_COUNT"

if [ "$NEW_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ Database is now empty${NC}"
else
    echo -e "${YELLOW}⚠️  Database still has $NEW_COUNT movies${NC}"
fi

echo ""
echo "=========================================="
echo "Database reset complete!"
echo ""
echo "You can now:"
echo "  1. Add movies manually via GUI"
echo "  2. Load sample data: ./scripts/load_sample_data.sh"
echo "=========================================="
