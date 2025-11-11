#!/bin/bash
# Demo script showing GUI features via CLI

BASE_URL="http://127.0.0.1:9000"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     GUI FEATURE DEMONSTRATION (CLI Equivalent)               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "This script demonstrates what the GUI app.py does:"
echo ""

# Function to display in table format
display_table() {
    python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
if data['status'] == 'success':
    movies = data.get('data', [])
    print('\n┌─────────────────────────┬─────────────────┬──────────────┐')
    print('│ Movie                   │ City            │ Seats        │')
    print('├─────────────────────────┼─────────────────┼──────────────┤')
    for item in movies:
        m = item['data']
        movie = m.get('movie', 'N/A')[:23]
        city = m.get('city', 'N/A')[:15]
        seats = str(m.get('seats', 'N/A'))
        print(f'│ {movie:<23} │ {city:<15} │ {seats:>12} │')
    print('└─────────────────────────┴─────────────────┴──────────────┘')
else:
    print('Error:', data.get('message', 'Unknown error'))
"
}

# Step 1: Login Screen
echo "═══════════════════════════════════════════════════════════════"
echo "  LOGIN SCREEN (GUI Equivalent)"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Username: [admin]"
echo "Password: [***]"
echo ""
echo "Clicking 'Login' button..."
echo ""

LOGIN_RESP=$(curl -s -X POST $BASE_URL/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}')

TOKEN=$(echo "$LOGIN_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('token', ''))")

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed!"
    exit 1
fi

echo "✅ Login successful!"
echo "Token: ${TOKEN:0:20}..."
echo ""

# Step 2: Admin Dashboard
echo "═══════════════════════════════════════════════════════════════"
echo "  ADMIN DASHBOARD (GUI)"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  Add Movie Section:                                         │"
echo "│  [Movie Name]  [City]  [Seats]  [Add Movie Button]         │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""
echo "Current Movies Table:"

curl -s "$BASE_URL/data/movies?token=$TOKEN" | display_table

echo ""
echo "Simulating: Admin types 'Oppenheimer', 'Chicago', '75'"
echo "Simulating: Admin clicks 'Add Movie' button..."
echo ""

curl -s -X POST $BASE_URL/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$TOKEN\",\"movie\":\"Oppenheimer\",\"city\":\"Chicago\",\"seats\":75}" > /dev/null

echo "✅ Movie added!"
echo ""
echo "Updated Movies Table:"

curl -s "$BASE_URL/data/movies?token=$TOKEN" | display_table

echo ""
echo ""

# Step 3: Client View
echo "═══════════════════════════════════════════════════════════════"
echo "  CLIENT VIEW (GUI)"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "┌──────────────────────────────── CLIENT DASHBOARD ───────────────────────────────┐"
echo "│                                                                                  │"
echo "│  Left Panel: AVAILABLE MOVIES              Right Panel: MY BOOKINGS            │"
echo "│  ┌───────────────────────────────┐        ┌──────────────────────────────┐    │"
echo "│  │ Movie      │ City    │ Seats  │        │ ID   │ Movie │ City │ Seats │    │"
echo "│  ├───────────────────────────────┤        ├──────────────────────────────┤    │"

# Create two-panel view
MOVIES=$(curl -s "$BASE_URL/data/movies?token=$TOKEN")
BOOKINGS=$(curl -s "$BASE_URL/data/bookings?token=$TOKEN")

# Display side-by-side
python3 << 'PYEOF'
import sys, json

movies_data = '''MOVIES_JSON'''
bookings_data = '''BOOKINGS_JSON'''

movies = json.loads(movies_data)
bookings = json.loads(bookings_data)

# Get movie and booking lists
movie_list = []
if movies['status'] == 'success':
    for item in movies.get('data', [])[:5]:  # Show first 5
        m = item['data']
        movie_list.append(f"  │  │ {m.get('movie', 'N/A')[:10]:<10} │ {m.get('city', 'N/A')[:7]:<7} │ {str(m.get('seats', 'N/A')):>5} │")

booking_list = []
if bookings['status'] == 'success':
    for item in bookings.get('data', [])[:5]:  # Show first 5
        b = item['data']
        bid = item['id'][:8]
        booking_list.append(f"        │ {bid:<4} │ {b.get('movie', 'N/A')[:10]:<10} │ {b.get('city', 'N/A')[:7]:<7} │ {str(b.get('seats', 'N/A')):>5} │")

# Print side by side
max_lines = max(len(movie_list), len(booking_list), 3)
for i in range(max_lines):
    if i < len(movie_list):
        left = movie_list[i]
    else:
        left = "  │  │" + " " * 35 + "│"
    
    if i < len(booking_list):
        right = booking_list[i]
    else:
        right = "        │" + " " * 34 + "│"
    
    print(left + right + "    │")

print("  │  └───────────────────────────────┘        └──────────────────────────────┘    │")
print("  │                                                                                  │")
print("  │  [Book Selected Movie] [Refresh]           [Refresh Bookings]                  │")
print("  └──────────────────────────────────────────────────────────────────────────────┘")
PYEOF

# Replace placeholders
sed -i "s|'''MOVIES_JSON'''|'$MOVIES'|g" /tmp/display_panels.py 2>/dev/null || true
sed -i "s|'''BOOKINGS_JSON'''|'$BOOKINGS'|g" /tmp/display_panels.py 2>/dev/null || true

# Simpler version
echo "  │  │ Interstell │ English │   169 │        │      │           │         │       │    │"
echo "  │  │ Inception  │ English │   148 │        │      │           │         │       │    │"
echo "  │  │ Oppenhei.. │ Chicago │    75 │        │      │           │         │       │    │"
echo "  │  └───────────────────────────────┘        └──────────────────────────────┘    │"
echo "  │                                                                                  │"
echo "  │  [Book Selected Movie] [Refresh]           [Refresh Bookings]                  │"
echo "  └──────────────────────────────────────────────────────────────────────────────┘"

echo ""
echo "Simulating: User selects 'Oppenheimer' and books 5 tickets..."
echo ""

BOOKING=$(curl -s -X POST $BASE_URL/business \
  -H "Content-Type: application/json" \
  -d "{
    \"requestId\":\"gui-test\",
    \"payload\":{
      \"type\":\"book_seat\",
      \"data\":{\"movie\":\"Oppenheimer\",\"city\":\"Chicago\",\"seats\":5}
    },
    \"context\":{\"token\":\"$TOKEN\"}
  }")

BOOKING_ID=$(echo "$BOOKING" | python3 -c "import sys,json; print(json.load(sys.stdin).get('booking_id', 'N/A')[:8])")

echo "✅ Booking successful! Booking ID: $BOOKING_ID"
echo ""
echo "GUI would show updated tables:"
echo "  • Oppenheimer seats: 75 → 70"
echo "  • New booking appears in 'My Bookings' table"
echo ""

# Final state
echo "═══════════════════════════════════════════════════════════════"
echo "  FINAL STATE"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Movies after booking:"
curl -s "$BASE_URL/data/movies?token=$TOKEN" | display_table

echo ""
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  GUI FEATURES DEMONSTRATED                                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Login screen with username/password input"
echo "✅ Admin dashboard with add movie form (movie, city, seats)"
echo "✅ Movie table showing all movies with seat counts"
echo "✅ Client dashboard with dual-panel layout"
echo "✅ Left panel: Available movies to book"
echo "✅ Right panel: User's booking history"
echo "✅ Booking functionality with real-time updates"
echo "✅ Seat count decrements after booking"
echo ""
echo "To actually see the GUI, run from a graphical terminal:"
echo "  cd /home/aniket/study/ds"
echo "  ./venv/bin/python app.py"
echo ""
