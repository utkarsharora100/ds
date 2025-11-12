# 🎯 Enhanced Client View Documentation

## Overview

The enhanced client view provides a comprehensive user interface for customers to browse movies and book tickets. It features a dual-panel dashboard with real-time data synchronization and complete backend integration.

## Features

### 1. User Registration
- New user account creation
- Password confirmation validation
- Duplicate username detection
- Backend API integration via `/register` endpoint

### 2. User Authentication
- Secure token-based authentication
- Session management
- Auto-login after registration

### 3. Client Dashboard

#### Left Panel - Available Movies
- **Movie Browser**: Table view showing all available movies
- **Columns**: Movie Name | City | Available Seats
- **Seat Selection**: Custom input field for number of seats
- **Book Button**: One-click ticket booking
- **Refresh Button**: Reload movies from server

#### Right Panel - My Bookings
- **Booking History**: Table view of user's bookings
- **Columns**: Booking ID | Movie | City | Seats
- **Auto-Update**: Refreshes after successful booking
- **Refresh Button**: Manual reload of booking data

### 4. Real-Time API Integration
- Token-based authentication for all requests
- Error handling with user-friendly messages
- Automatic data refresh after operations
- Network timeout handling

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  GUI Application                     │
│                    (app.py)                          │
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐         ┌──────────────┐         │
│  │ Registration │         │    Login     │         │
│  │     Page     │──────────▶   Page       │         │
│  └──────────────┘         └──────┬───────┘         │
│                                   │                  │
│         ┌─────────────────────────┴─────────┐       │
│         │                                   │       │
│  ┌──────▼─────────┐            ┌───────────▼────┐  │
│  │     Admin      │            │     Client     │  │
│  │   Dashboard    │            │   Dashboard    │  │
│  │                │            │                │  │
│  │ • Add Movies   │            │ • View Movies  │  │
│  │ • Simulate     │            │ • Book Tickets │  │
│  │ • Test Raft    │            │ • View History │  │
│  └────────────────┘            └────────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │     Application Server         │
        │       (Port 9000)              │
        │                                │
        │  • /register  - Create user    │
        │  • /login     - Authenticate   │
        │  • /data/movies - List movies  │
        │  • /business  - Book tickets   │
        │  • /data/bookings - History    │
        └────────────────────────────────┘
```

## API Endpoints Documentation

### Application Server Endpoints (Port 9000)

#### 1. Health Check
**Endpoint:** `GET /health`  
**Purpose:** Check if application server is running  
**Authentication:** None required  
**Request:** None  
**Response:**
```json
{
  "status": "healthy",
  "service": "application-server"
}
```

#### 2. Register User
**Endpoint:** `POST /register`  
**Purpose:** Create a new user account  
**Authentication:** None required  
**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```
**Success Response (200):**
```json
{
  "status": "success",
  "message": "User created"
}
```
**Error Response (200):**
```json
{
  "status": "failure",
  "message": "User already exists"
}
```

#### 3. Login
**Endpoint:** `POST /login`  
**Purpose:** Authenticate user and get access token  
**Authentication:** None required  
**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```
**Success Response (200):**
```json
{
  "status": "success",
  "token": "uuid-string",
  "user": "username"
}
```
**Error Response (200):**
```json
{
  "status": "failure",
  "message": "Invalid credentials"
}
```

#### 4. Get Data (Movies/Bookings)
**Endpoint:** `GET /data/{data_type}`  
**Purpose:** Retrieve movies or bookings list  
**Authentication:** Required (token)  
**URL Parameters:**
- `data_type`: `movies` | `bookings` | `documents` | `messages`

**Query Parameters:**
- `token`: Authentication token from login

**Request Example:**
```bash
GET /data/movies?token=your-token-here
```

**Success Response - Movies (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "data": {
        "movie": "Inception",
        "city": "Delhi"
      }
    },
    {
      "id": 2,
      "data": {
        "movie": "The Matrix",
        "city": "Mumbai"
      }
    }
  ]
}
```

**Success Response - Bookings (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "booking-uuid",
      "data": {
        "user": "username",
        "movie": "Inception",
        "city": "Delhi",
        "seats": 2,
        "timestamp": 1731234567.89
      }
    }
  ]
}
```

**Error Response (200):**
```json
{
  "status": "failure",
  "message": "Unauthorized"
}
```
or
```json
{
  "status": "failure",
  "message": "Invalid data type"
}
```

#### 5. Book Tickets
**Endpoint:** `POST /business`  
**Purpose:** Book movie tickets  
**Authentication:** Required (token in context)  
**Request Body:**
```json
{
  "requestId": "unique-request-id",
  "payload": {
    "type": "book_seat",
    "data": {
      "movie": "Movie Name",
      "city": "City Name",
      "seats": 2
    }
  },
  "context": {
    "token": "your-auth-token"
  }
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "booking_id": "uuid-string"
}
```

**Error Responses (200):**
```json
{
  "status": "failure",
  "message": "Unauthorized"
}
```
or
```json
{
  "status": "failure",
  "message": "Unknown request type"
}
```

#### 6. Add Movie (Admin Only)
**Endpoint:** `POST /add_movie`  
**Purpose:** Add a new movie to the system  
**Authentication:** Required (admin token)  
**Request Body:**
```json
{
  "token": "admin-auth-token",
  "movie": "Movie Name",
  "city": "City Name",
  "seats": 100
}
```

**Success Response (200):**
```json
{
  "status": "success"
}
```

**Error Response (200):**
```json
{
  "status": "failure",
  "message": "Unauthorized"
}
```

#### 7. Clear Database (Admin Only)
**Endpoint:** `POST /admin/clear_database`  
**Purpose:** Clear all movies and bookings from database  
**Authentication:** Required (admin token)  
**Request Body:**
```json
{
  "token": "admin-auth-token"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Database cleared"
}
```

**Error Response (200):**
```json
{
  "status": "failure",
  "message": "Unauthorized"
}
```

#### 8. Load Sample Data (Admin Only)
**Endpoint:** `POST /admin/load_sample_data`  
**Purpose:** Load 15 sample movies into database  
**Authentication:** Required (admin token)  
**Request Body:**
```json
{
  "token": "admin-auth-token"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Sample data loaded",
  "movies_added": 15
}
```

**Error Response (200):**
```json
{
  "status": "failure",
  "message": "Unauthorized"
}
```

### Raft Node Endpoints (Ports 50051-50053)

#### 1. Node Status
**Endpoint:** `GET /status`  
**Purpose:** Get Raft node state and cluster information  
**Authentication:** None required  
**Request:** None  
**Response:**
```json
{
  "node_id": "node1",
  "state": "leader",
  "term": 2,
  "leader_id": "node1",
  "peers": ["node2", "node3"]
}
```

**States:**
- `follower`: Node is following a leader
- `candidate`: Node is participating in election
- `leader`: Node is the cluster leader

#### 2. Trigger Election
**Endpoint:** `POST /trigger-election`  
**Purpose:** Manually trigger a leader election  
**Authentication:** None required  
**Request:** None  
**Response:**
```json
{
  "message": "Election manually triggered."
}
```

### LLM Server Endpoints (Port 8500)

#### 1. Health Check
**Endpoint:** `GET /health`  
**Purpose:** Check LLM server status and model info  
**Authentication:** None required  
**Request:** None  
**Response:**
```json
{
  "status": "healthy",
  "service": "llm-server",
  "model": "Qwen/Qwen2.5-0.5B",
  "model_loaded": true
}
```

#### 2. Chat
**Endpoint:** `POST /chat`  
**Purpose:** Conversational AI interaction  
**Authentication:** None required  
**Request Body:**
```json
{
  "message": "Tell me about your booking system",
  "history": []
}
```

**Response:**
```json
{
  "response": "Our booking system allows you to...",
  "confidence": 0.85
}
```

#### 3. Ask FAQ
**Endpoint:** `POST /ask`  
**Purpose:** Quick FAQ-style questions  
**Authentication:** None required  
**Request Body:**
```json
{
  "question": "How do I book a ticket?"
}
```

**Response:**
```json
{
  "answer": "To book a ticket, first login to your account...",
  "confidence": 0.92
}
```

### Summary Table

| Endpoint | Method | Port | Auth Required | Purpose |
|----------|--------|------|---------------|---------|
| `/health` | GET | 9000 | No | App server health |
| `/register` | POST | 9000 | No | Create user account |
| `/login` | POST | 9000 | No | User authentication |
| `/data/{type}` | GET | 9000 | Yes (token) | Get movies/bookings |
| `/business` | POST | 9000 | Yes (token) | Book tickets |
| `/add_movie` | POST | 9000 | Yes (admin) | Add new movie |
| `/admin/clear_database` | POST | 9000 | Yes (admin) | Clear all data |
| `/admin/load_sample_data` | POST | 9000 | Yes (admin) | Load 15 sample movies |
| `/status` | GET | 50051-50053 | No | Raft node status |
| `/trigger-election` | POST | 50051-50053 | No | Force election |
| `/health` | GET | 8500 | No | LLM server health |
| `/chat` | POST | 8500 | No | AI conversation |
| `/ask` | POST | 8500 | No | AI FAQ answers |

## Testing Guide

### Prerequisites
```bash
# Ensure Docker services are running
sudo docker compose up -d

# Verify services
sudo docker compose ps
```

### Test 1: Command Line Testing

#### Step 1: Health Check
```bash
curl http://localhost:9000/health
```
**Expected Output:**
```json
{"status":"healthy","service":"application-server"}
```

#### Step 2: Register New User
```bash
curl -X POST http://localhost:9000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"pass123"}'
```
**Expected Output:**
```json
{"status":"success","message":"User created"}
```

#### Step 3: Login as Client
```bash
curl -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"pass123"}'
```
**Expected Output:**
```json
{
  "status":"success",
  "token":"<uuid-token>",
  "user":"testuser"
}
```

#### Step 4: Add Movies (Admin)
```bash
# Login as admin
ADMIN_TOKEN=$(curl -s -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}' | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

# Add movies
curl -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"Inception\",\"city\":\"Delhi\"}"

curl -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"The Matrix\",\"city\":\"Mumbai\"}"
```

#### Step 5: View Movies (Client)
```bash
# Use your client token from Step 3
curl "http://localhost:9000/data/movies?token=<YOUR_TOKEN>"
```
**Expected Output:**
```json
{
  "status":"success",
  "data":[
    {"id":1,"data":{"movie":"Inception","city":"Delhi"}},
    {"id":2,"data":{"movie":"The Matrix","city":"Mumbai"}}
  ]
}
```

#### Step 6: Book Tickets (Client)
```bash
curl -X POST http://localhost:9000/business \
  -H "Content-Type: application/json" \
  -d '{
    "requestId":"test-booking-001",
    "payload":{
      "type":"book_seat",
      "data":{
        "movie":"Inception",
        "city":"Delhi",
        "seats":2
      }
    },
    "context":{"token":"<YOUR_TOKEN>"}
  }'
```
**Expected Output:**
```json
{"status":"success","booking_id":"<uuid>"}
```

### Test 2: Automated Setup and Testing
```bash
# Run the comprehensive setup script
./quickstart.sh
```

This script automatically:
1. ✅ Checks prerequisites (Docker, Python, etc.)
2. ✅ Cleans up previous instances
3. ✅ Builds Docker images
4. ✅ Starts all services
5. ✅ Waits for initialization
6. ✅ Runs health checks & Raft verification
7. ✅ Loads sample data (optional)
8. ✅ Tests basic functionality (login, movies API)
9. ✅ Displays system ready with all URLs

### Test 3: GUI Application

#### Installation
```bash
pip install customtkinter requests
```

#### Running the Application
```bash
python app.py
```

#### Testing Steps

**1. Register New User:**
- Click "Register New Account" button
- Enter username (e.g., "john_doe")
- Enter password
- Confirm password
- Click "Register"
- Should show success message and redirect to login

**2. Login as Client:**
- Enter registered username and password
- Click "Login"
- Should open client dashboard

**3. View Movies:**
- Left panel shows available movies
- Each row displays: Movie Name | City | Available Seats
- Movies are fetched from live backend

**4. Book Tickets:**
- Select a movie by clicking on it
- Enter number of seats in input field (default: 1)
- Click "Book Selected Movie"
- Should show success message
- Booking appears in right panel

**6. View Booking History:**
- Right panel shows "My Bookings"
- Displays: Booking ID | Movie | City | Seats
- Click "Refresh Bookings" to reload

**7. Admin Features (when logged in as admin):**
- "Load Sample Movies" button - loads 15 test movies
- "Clear Database" button - removes all movies and bookings
- Both require confirmation

**6. Refresh Data:**
- Click "Refresh Movies" to reload movie list
- Click "Refresh Bookings" to reload booking history

## Code Structure

### Key Components in `app.py`

```python
# Main Application Class
class App(ctk.CTk):
    def __init__(self):
        # Initialize GUI window
        # Set up Raft node tracking
        # Load login page
    
    # Registration Page
    def load_register(self):
        # User registration form
        # Password validation
        # API call to /register
    
    # Login Page
    def load_login(self):
        # Login form
        # Raft node controls
        # API call to /login
    
    # Client Dashboard
    def load_user_dashboard(self, username):
        # Dual-panel layout
        # Movies table (left)
        # Bookings table (right)
        # API integration
    
    # Helper Methods
    def refresh_movies_client(self):
        # Fetch movies from API
        # Update table view
    
    def refresh_bookings_client(self):
        # Fetch bookings from API
        # Update table view
    
    def book_movie_client(self, username):
        # Validate selection
        # Send booking request
        # Refresh data
```

## Error Handling

### Connection Errors
```python
try:
    resp = requests.get(url, timeout=5)
    # Process response
except Exception as e:
    messagebox.showerror("Error", f"Could not connect to server: {e}")
```

### Validation Errors
- Empty username/password
- Password mismatch during registration
- Invalid seat count
- No movie selected

### API Errors
- Authentication failures
- Booking failures
- Network timeouts
- Server unavailability

## User Experience Features

### Visual Feedback
- ✅ Success messages for completed actions
- ❌ Error messages for failed operations
- 🔄 Loading states during API calls
- 🟢 Green indicators for active Raft nodes
- 🔴 Red indicators for inactive nodes

### Data Validation
- Username/password required fields
- Password confirmation matching
- Positive seat count validation
- Movie selection requirement

### Responsive Design
- Dual-panel layout maximizes screen space
- Scrollable tables for long lists
- Proper spacing and padding
- Dark theme for reduced eye strain

## Performance Considerations

### API Calls
- 5-second timeout for all requests
- Retry logic not implemented (can be added)
- Token caching in client instance

### Data Refresh
- Manual refresh buttons (not auto-refresh)
- Refresh after successful booking
- Minimal network calls

### Memory Usage
- Lightweight GUI framework (CustomTkinter)
- No local data caching
- Fresh data on each refresh

## Security Notes

⚠️ **Current Implementation - Development Mode**

For production deployment, implement:
- HTTPS/TLS encryption
- Password hashing (bcrypt, argon2)
- JWT with expiration
- Rate limiting
- Input sanitization
- CORS policy
- Session management
- Audit logging

## Future Enhancements

### Potential Features
- [ ] Auto-refresh movies/bookings
- [ ] Cancel booking functionality
- [ ] Seat selection interface
- [ ] Movie ratings and reviews
- [ ] Filter by city/movie
- [ ] Search functionality
- [ ] Booking confirmation emails
- [ ] Payment gateway integration
- [ ] Real-time seat availability
- [ ] Mobile responsive design

## Troubleshooting

### Issue: GUI Won't Start
**Symptom:** `ModuleNotFoundError: No module named 'customtkinter'`
```bash
# Solution
pip install customtkinter requests
```

### Issue: Cannot Connect to Server
**Symptom:** Connection refused errors
```bash
# Check if services are running
sudo docker compose ps

# Check app-server health
curl http://localhost:9000/health

# Restart services if needed
sudo docker compose restart app-server
```

### Issue: Login Fails
**Symptom:** "Invalid credentials" message
```bash
# Verify user exists
curl -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}'

# Register new user if needed
curl -X POST http://localhost:9000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"pass"}'
```

### Issue: No Movies Displayed
**Symptom:** Empty movie table
```bash
# Use the load sample data script
./scripts/load_sample_data.sh

# Or add movies manually as admin
python -c "
import requests
resp = requests.post('http://localhost:9000/login', 
    json={'username':'admin','password':'123'})
token = resp.json()['token']
requests.post('http://localhost:9000/add_movie',
    json={'token':token, 'movie':'Test Movie', 'city':'Delhi', 'seats':100})
"
```

### Issue: Booking Fails
**Symptom:** Booking error messages

Check:
1. Movie exists in system
2. Valid authentication token
3. Positive seat count
4. Server logs for errors:
   ```bash
   sudo docker compose logs app-server --tail=50
   ```

## Demo Output

```
╔════════════════════════════════════════════════════════════╗
║     ENHANCED CLIENT VIEW - LIVE DEMONSTRATION              ║
╚════════════════════════════════════════════════════════════╝

[1/7] Checking server health...
{"status":"healthy","service":"application-server"}
✓ Server is healthy

[2/7] Registering new client user 'demo_client'...
{"status":"success","message":"User created"}
✓ User registered

[3/7] Logging in as client...
{"status":"success","token":"b701844d-...","user":"demo_client"}
✓ Client logged in

[4/7] Adding movies...
✓ Movies added

[5/7] Fetching available movies (CLIENT VIEW)...
{
    "status": "success",
    "data": [
        {"id": 1, "data": {"movie": "Inception", "city": "Delhi"}},
        {"id": 2, "data": {"movie": "The Matrix", "city": "Mumbai"}},
        {"id": 3, "data": {"movie": "Interstellar", "city": "Bangalore"}}
    ]
}
✓ Movies retrieved

[6/7] Booking tickets as client...
{"status":"success","booking_id":"698dc39f-..."}
✓ Booking successful

╔════════════════════════════════════════════════════════════╗
║                    DEMONSTRATION COMPLETE                  ║
╚════════════════════════════════════════════════════════════╝
```

## Summary

The enhanced client view provides a complete user experience for movie booking with:

✅ **User Management**: Registration and authentication  
✅ **Movie Browsing**: Real-time movie list with details  
✅ **Ticket Booking**: Interactive booking with validation  
✅ **History Tracking**: Personal booking history  
✅ **Live Updates**: Manual refresh from server  
✅ **Error Handling**: User-friendly error messages  
✅ **Modern UI**: Dual-panel dashboard design  

All features are fully tested and integrated with the backend API.
