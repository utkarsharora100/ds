# 🧪 Client View Testing Quick Reference

## Prerequisites

```bash
# Ensure all services are running
sudo docker compose ps

# Check services health
curl http://localhost:9000/health  # App server
curl http://localhost:8500/health  # LLM server
curl http://localhost:50051/status # Raft node 1
```

## Quick Test Commands

### 1. Check Server Status
```bash
curl http://localhost:9000/health
```
**Expected:**
```json
{"status":"healthy","service":"application-server"}
```

### 2. Register New User
```bash
curl -X POST http://localhost:9000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```
**Expected:**
```json
{"status":"success","message":"User created"}
```

**If user exists:**
```json
{"status":"failure","message":"User already exists"}
```

### 3. Login and Get Token
```bash
curl -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```
**Expected:**
```json
{
  "status":"success",
  "token":"97c00095-13d0-4080-b78f-be075b55fecc",
  "user":"testuser"
}
```

**Save the token:**
```bash
TOKEN=$(curl -s -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}' | \
  grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo "Token: $TOKEN"
```

### 4. View Available Movies
```bash
curl "http://localhost:9000/data/movies?token=$TOKEN"
```
**Expected:**
```json
{
  "status":"success",
  "data":[
    {"id":1,"data":{"movie":"Inception","city":"Delhi"}},
    {"id":2,"data":{"movie":"The Matrix","city":"Mumbai"}},
    {"id":3,"data":{"movie":"Interstellar","city":"Bangalore"}}
  ]
}
```

**If unauthorized:**
```json
{"status":"failure","message":"Unauthorized"}
```

### 5. Book a Ticket
```bash
curl -X POST http://localhost:9000/business \
  -H "Content-Type: application/json" \
  -d "{
    \"requestId\":\"booking-$(date +%s)\",
    \"payload\":{
      \"type\":\"book_seat\",
      \"data\":{
        \"movie\":\"Inception\",
        \"city\":\"Delhi\",
        \"seats\":2
      }
    },
    \"context\":{\"token\":\"$TOKEN\"}
  }"
```
**Expected:**
```json
{
  "status":"success",
  "booking_id":"8a665a1f-8f9e-4ea1-963c-7062fc94c62a"
}
```

**If unauthorized:**
```json
{"status":"failure","message":"Unauthorized"}
```

### 6. View Your Bookings
```bash
curl "http://localhost:9000/data/bookings?token=$TOKEN"
```
**Expected:**
```json
{
  "status":"success",
  "data":[
    {
      "id":"8a665a1f-8f9e-4ea1-963c-7062fc94c62a",
      "data":{
        "user":"testuser",
        "movie":"Inception",
        "city":"Delhi",
        "seats":2,
        "timestamp":1731234567.89
      }
    }
  ]
}
```

### 7. Check Raft Cluster Status
```bash
# Node 1
curl http://localhost:50051/status

# Node 2  
curl http://localhost:50052/status

# Node 3
curl http://localhost:50053/status
```
**Expected (Leader):**
```json
{
  "node_id":"node1",
  "state":"leader",
  "term":2,
  "leader_id":"node1",
  "peers":["node2","node3"]
}
```

**Expected (Follower):**
```json
{
  "node_id":"node2",
  "state":"follower",
  "term":2,
  "leader_id":"node1",
  "peers":["node1","node3"]
}
```

### 8. Test AI Assistant
```bash
# Quick FAQ
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I book a ticket?"}'

# Chat
curl -X POST http://localhost:8500/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Tell me about your system","history":[]}'
```

## Complete Test Flow Script

```bash
#!/bin/bash

echo "=== 1. Health Check ==="
curl -s http://localhost:9000/health
echo -e "\n"

echo "=== 2. Register User ==="
curl -s -X POST http://localhost:9000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"pass123"}'
echo -e "\n"

echo "=== 3. Login ==="
TOKEN=$(curl -s -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"pass123"}' | \
  grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo "Token: $TOKEN"
echo -e "\n"

echo "=== 4. Add Movies (Admin) ==="
ADMIN_TOKEN=$(curl -s -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}' | \
  grep -o '"token":"[^"]*"' | cut -d'"' -f4)

curl -s -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"Inception\",\"city\":\"Delhi\"}"
echo ""

curl -s -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"The Matrix\",\"city\":\"Mumbai\"}"
echo -e "\n"

echo "=== 5. View Movies ==="
curl -s "http://localhost:9000/data/movies?token=$TOKEN"
echo -e "\n"

echo "=== 6. Book Ticket ==="
curl -s -X POST http://localhost:9000/business \
  -H "Content-Type: application/json" \
  -d "{
    \"requestId\":\"test-$(date +%s)\",
    \"payload\":{
      \"type\":\"book_seat\",
      \"data\":{\"movie\":\"Inception\",\"city\":\"Delhi\",\"seats\":2}
    },
    \"context\":{\"token\":\"$TOKEN\"}
  }"
echo -e "\n"

echo "=== 7. View Bookings ==="
curl -s "http://localhost:9000/data/bookings?token=$TOKEN"
echo -e "\n"

echo "=== 8. Raft Status ==="
curl -s http://localhost:50051/status
echo -e "\n"

echo "✅ All tests complete!"
```

## Automated Demo

Run the complete demonstration:
```bash
./demo_client_view.sh
```

**This demonstrates:**
- ✅ Server health check
- ✅ User registration
- ✅ Client authentication
- ✅ Admin adding movies
- ✅ Client viewing movies
- ✅ Client booking tickets
- ✅ Full end-to-end flow

## GUI Application Testing

### Install Dependencies
```bash
# In virtual environment
source venv/bin/activate
pip install customtkinter requests
```

### Run Application
```bash
# Make sure you're in a graphical session
export DISPLAY=:0
python app.py
```

### Test Flow (GUI)

**1. Register New User:**
- Click "Register New Account" button
- Enter username (e.g., "john_doe")
- Enter password
- Confirm password
- Click "Register"
- Expected: Success message → redirects to login

**2. Login as Client:**
- Enter username and password
- Click "Login"
- Expected: Opens client dashboard with dual-panel layout

**3. Start Raft Nodes (Optional):**
- Click "Start Node 1" → Indicator turns 🟢
- Click "Start Node 2" → Indicator turns 🟢
- Click "Start Node 3" → Indicator turns 🟢
- Expected: Terminals open for each node

**4. View Movies (Left Panel):**
- Browse available movies in table
- Columns: Movie | City | Available Seats
- Expected: Movies fetched from server displayed

**5. Book Tickets:**
- Select a movie by clicking on row
- Enter number of seats (default: 1)
- Click "Book Selected Movie"
- Expected: Success message, booking appears in right panel

**6. View Booking History (Right Panel):**
- Check "My Bookings" table
- Columns: Booking ID | Movie | City | Seats
- Expected: All your bookings displayed

**7. Refresh Data:**
- Click "Refresh Movies" to reload movies
- Click "Refresh Bookings" to reload booking history
- Expected: Latest data fetched from server

**8. Admin Dashboard (Login as admin/123):**
- Add new movies with "Add Movie" button
- Simulate multiple clients
- Test database consistency
- Expected: Admin functions work correctly

## Expected Results

### Health Check
```json
{"status":"healthy","service":"application-server"}
```

### Registration Success
```json
{"status":"success","message":"User created"}
```

### Registration Failure (User Exists)
```json
{"status":"failure","message":"User already exists"}
```

### Login Success
```json
{
  "status":"success",
  "token":"97c00095-13d0-4080-b78f-be075b55fecc",
  "user":"testuser"
}
```

### Login Failure
```json
{"status":"failure","message":"Invalid credentials"}
```

### Get Movies Success
```json
{
  "status":"success",
  "data":[
    {"id":1,"data":{"movie":"Inception","city":"Delhi"}},
    {"id":2,"data":{"movie":"The Matrix","city":"Mumbai"}},
    {"id":3,"data":{"movie":"Interstellar","city":"Bangalore"}}
  ]
}
```

### Get Movies/Bookings Unauthorized
```json
{"status":"failure","message":"Unauthorized"}
```

### Book Ticket Success
```json
{
  "status":"success",
  "booking_id":"8a665a1f-8f9e-4ea1-963c-7062fc94c62a"
}
```

### Get Bookings Success
```json
{
  "status":"success",
  "data":[
    {
      "id":"8a665a1f-8f9e-4ea1-963c-7062fc94c62a",
      "data":{
        "user":"testuser",
        "movie":"Inception",
        "city":"Delhi",
        "seats":2,
        "timestamp":1731234567.89
      }
    }
  ]
}
```

### Raft Node Status (Leader)
```json
{
  "node_id":"node1",
  "state":"leader",
  "term":2,
  "leader_id":"node1",
  "peers":["node2","node3"]
}
```

### Raft Node Status (Follower)
```json
{
  "node_id":"node2",
  "state":"follower",
  "term":2,
  "leader_id":"node1",
  "peers":["node1","node3"]
}
```

### LLM Health Check
```json
{
  "status":"healthy",
  "service":"llm-server",
  "model":"Qwen/Qwen2.5-0.5B",
  "model_loaded":true
}
```

### LLM Ask Response
```json
{
  "answer":"To book a ticket, first login to your account...",
  "confidence":0.92
}
```

## Troubleshooting

### Service Not Running
```bash
# Check status
sudo docker compose ps

# View logs
sudo docker compose logs app-server --tail=50
sudo docker compose logs llm-server --tail=50
sudo docker compose logs raft-node1 --tail=50

# Restart services
sudo docker compose restart app-server

# Full restart
sudo docker compose down
sudo docker compose up -d
```

### Port Already in Use
```bash
# Find process using port 9000
sudo lsof -i :9000

# Kill process
sudo kill <PID>

# Or kill all on port
sudo fuser -k 9000/tcp

# Then restart
sudo docker compose up -d
```

### Connection Refused
```bash
# Check if server is listening
netstat -tlnp | grep 9000

# Test connection
telnet localhost 9000

# Check Docker network
sudo docker network ls
sudo docker network inspect movie-booking-net
```

### Unauthorized Errors
```bash
# Verify token is valid
echo $TOKEN

# Try logging in again
TOKEN=$(curl -s -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"pass123"}' | \
  grep -o '"token":"[^"]*"' | cut -d'"' -f4)
```

### No Movies Available
```bash
# Add movies as admin first
ADMIN_TOKEN=$(curl -s -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}' | \
  grep -o '"token":"[^"]*"' | cut -d'"' -f4)

# Add some movies
curl -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"Test Movie\",\"city\":\"Delhi\"}"
```

### GUI Display Error
```bash
# Check display variable
echo $DISPLAY

# Set display
export DISPLAY=:0

# If in TTY, start graphical session
startx

# Or use virtual display
sudo pacman -S xorg-server-xvfb
DISPLAY=:99 Xvfb :99 -screen 0 1024x768x24 &
DISPLAY=:99 python app.py

# Or just use CLI testing
./demo_client_view.sh
```

### Module Not Found
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install customtkinter requests

# Or use venv python directly
./venv/bin/python app.py
```

### Docker Build Timeout
```bash
# Already fixed in Dockerfile.app and Dockerfile.llm
# with increased timeout: --default-timeout=1000

# If still having issues, build with no cache
sudo docker compose build --no-cache

# Or increase Docker memory (in Docker Desktop settings)
```

## Admin Functions (for setup)

### Login as Admin
```bash
ADMIN_TOKEN=$(curl -s -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}' | \
  grep -o '"token":"[^"]*"' | cut -d'"' -f4)

echo "Admin Token: $ADMIN_TOKEN"
```

### Add Multiple Movies
```bash
# Inception in multiple cities
curl -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"Inception\",\"city\":\"Delhi\"}"

curl -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"Inception\",\"city\":\"Mumbai\"}"

# Other movies
curl -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"The Matrix\",\"city\":\"Mumbai\"}"

curl -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"Interstellar\",\"city\":\"Bangalore\"}"

curl -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"The Dark Knight\",\"city\":\"Delhi\"}"
```

### Trigger Raft Election
```bash
# Manually trigger election on a node
curl -X POST http://localhost:50051/trigger-election

# Check leader after election
sleep 5
curl http://localhost:50051/status | grep leader
curl http://localhost:50052/status | grep leader
curl http://localhost:50053/status | grep leader
```

### Monitor Cluster
```bash
# Watch Raft cluster status
watch -n 2 'curl -s http://localhost:50051/status; \
             echo ""; \
             curl -s http://localhost:50052/status; \
             echo ""; \
             curl -s http://localhost:50053/status'
```

### View System Logs
```bash
# Follow all logs
sudo docker compose logs -f

# Follow specific service
sudo docker compose logs -f app-server

# Last 100 lines
sudo docker compose logs --tail=100 app-server

# With timestamps
sudo docker compose logs --tail=50 -t app-server
```

### Performance Testing
```bash
# Register multiple users
for i in {1..10}; do
  curl -X POST http://localhost:9000/register \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"user$i\",\"password\":\"pass$i\"}"
done

# Book multiple tickets
for i in {1..10}; do
  TOKEN=$(curl -s -X POST http://localhost:9000/login \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"user$i\",\"password\":\"pass$i\"}" | \
    grep -o '"token":"[^"]*"' | cut -d'"' -f4)
  
  curl -X POST http://localhost:9000/business \
    -H "Content-Type: application/json" \
    -d "{
      \"requestId\":\"booking-$i-$(date +%s)\",
      \"payload\":{
        \"type\":\"book_seat\",
        \"data\":{\"movie\":\"Inception\",\"city\":\"Delhi\",\"seats\":$i}
      },
      \"context\":{\"token\":\"$TOKEN\"}
    }"
done
```

## Full Documentation

For complete documentation, see [CLIENT_VIEW.md](CLIENT_VIEW.md)
