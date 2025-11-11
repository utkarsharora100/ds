#!/bin/bash
# Test script for database integration and seat management

echo "======================================"
echo "DATABASE INTEGRATION TEST"
echo "======================================"
echo ""

BASE_URL="http://127.0.0.1:9000"

# Step 1: Health check
echo "1. Testing health endpoint..."
curl -s $BASE_URL/health | jq '.'
echo ""

# Step 2: Login as admin
echo "2. Logging in as admin..."
LOGIN_RESP=$(curl -s -X POST $BASE_URL/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}')
echo "$LOGIN_RESP" | jq '.'
TOKEN=$(echo "$LOGIN_RESP" | jq -r '.token')
echo "Token: $TOKEN"
echo ""

# Step 3: Check initial movies (should show sample data from DB)
echo "3. Checking initial movies from database..."
curl -s "$BASE_URL/data/movies?token=$TOKEN" | jq '.'
echo ""

# Step 4: Add a new movie with seats
echo "4. Adding new movie 'Dune 2' with 100 seats..."
curl -s -X POST $BASE_URL/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$TOKEN\",\"movie\":\"Dune 2\",\"city\":\"New York\",\"seats\":100}" | jq '.'
echo ""

# Step 5: Verify movie was added to database
echo "5. Verifying movie was added to database..."
curl -s "$BASE_URL/data/movies?token=$TOKEN" | jq '.data[] | select(.data.movie == "Dune 2")'
echo ""

# Step 6: Book tickets
echo "6. Booking 5 tickets for Dune 2..."
BOOKING_RESP=$(curl -s -X POST $BASE_URL/business \
  -H "Content-Type: application/json" \
  -d "{
    \"requestId\":\"test-req-1\",
    \"payload\":{
      \"type\":\"book_seat\",
      \"data\":{
        \"movie\":\"Dune 2\",
        \"city\":\"New York\",
        \"seats\":5
      }
    },
    \"context\":{\"token\":\"$TOKEN\"}
  }")
echo "$BOOKING_RESP" | jq '.'
BOOKING_ID=$(echo "$BOOKING_RESP" | jq -r '.booking_id')
echo ""

# Step 7: Check updated seat count (should be 95)
echo "7. Checking seat count after booking (should be 95)..."
curl -s "$BASE_URL/data/movies?token=$TOKEN" | jq '.data[] | select(.data.movie == "Dune 2")'
echo ""

# Step 8: Verify booking was recorded
echo "8. Verifying booking was recorded..."
curl -s "$BASE_URL/data/bookings?token=$TOKEN" | jq ".data[] | select(.id == \"$BOOKING_ID\")"
echo ""

# Step 9: Test insufficient seats error
echo "9. Testing insufficient seats error (trying to book 100 seats when only 95 available)..."
curl -s -X POST $BASE_URL/business \
  -H "Content-Type: application/json" \
  -d "{
    \"requestId\":\"test-req-2\",
    \"payload\":{
      \"type\":\"book_seat\",
      \"data\":{
        \"movie\":\"Dune 2\",
        \"city\":\"New York\",
        \"seats\":100
      }
    },
    \"context\":{\"token\":\"$TOKEN\"}
  }" | jq '.'
echo ""

# Step 10: Add another movie
echo "10. Adding another movie 'The Matrix' with 50 seats..."
curl -s -X POST $BASE_URL/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$TOKEN\",\"movie\":\"The Matrix\",\"city\":\"Los Angeles\",\"seats\":50}" | jq '.'
echo ""

# Step 11: Show all movies
echo "11. Final movie list..."
curl -s "$BASE_URL/data/movies?token=$TOKEN" | jq '.data'
echo ""

echo "======================================"
echo "✅ DATABASE INTEGRATION TEST COMPLETE"
echo "======================================"
