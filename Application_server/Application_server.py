import uuid
import time
import os
import sys
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx

# Import storage module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from llm import storage

# ---------------------- APPLICATION SERVER ----------------------
class ApplicationServer:
    def __init__(self):
        # Initialize database connection
        self.db = storage.create_in_memory_db()
        print("[SERVER] ✅ Database initialized with sample data")
        
        # Keep minimal in-memory storage for bookings, documents, messages
        self.users: Dict[str, str] = {
            "admin": "123",     # default admin
            "utkarsh": "password123"
        }
        self.sessions: Dict[str, str] = {}  # token -> username
        self.store = {
            "bookings": [],
            "documents": [],
            "messages": [],
        }
        print("[SERVER] ✅ Application Server initialized.")

    # ---------------------- AUTH ----------------------
    def register_user(self, username: str, password: str) -> Dict[str, Any]:
        if username in self.users:
            return {"status": "failure", "message": "User already exists"}
        self.users[username] = password
        
        # Also create in DB
        storage.create_user(self.db, username, password)
        
        print(f"[SERVER] New user created → {username}")
        return {"status": "success", "message": "User created"}

    def loginResponse(self, username: str, password: str) -> Dict[str, Any]:
        if username not in self.users or self.users[username] != password:
            return {"status": "failure", "message": "Invalid credentials"}
        token = str(uuid.uuid4())
        self.sessions[token] = username
        print(f"[SERVER] 🔑 User '{username}' logged in. Token = {token}")
        return {"status": "success", "token": token, "user": username}

    # ---------------------- DATA GETTER ----------------------
    def getResponse(self, token: str, data_type: str) -> Dict[str, Any]:
        if token not in self.sessions:
            return {"status": "failure", "message": "Unauthorized"}
        
        username = self.sessions[token]
        
        # If requesting movies, fetch from database
        if data_type == "movies":
            movies = storage.get_all_movies(self.db)
            # Format to match existing API response structure
            formatted_movies = [
                {"id": idx + 1, "data": movie} 
                for idx, movie in enumerate(movies)
            ]
            return {"status": "success", "data": formatted_movies}
        
        # For bookings, filter based on user role
        if data_type == "bookings":
            # Admin sees all bookings, regular users see only their bookings
            if username == "admin":
                # Admin: return all bookings with username in data field
                bookings_with_username = []
                for booking in self.store.get("bookings", []):
                    booking_copy = booking.copy()
                    # Ensure username is in the data field for frontend display
                    if "data" in booking_copy and "user" in booking_copy["data"]:
                        booking_copy["data"]["username"] = booking_copy["data"]["user"]
                    bookings_with_username.append(booking_copy)
                return {"status": "success", "data": bookings_with_username}
            else:
                # Regular user: filter to show only their bookings
                user_bookings = [
                    booking for booking in self.store.get("bookings", [])
                    if booking.get("data", {}).get("user") == username
                ]
                return {"status": "success", "data": user_bookings}
        
        # For other data types, use in-memory store
        if data_type not in self.store:
            return {"status": "failure", "message": "Invalid data type"}
        return {"status": "success", "data": self.store[data_type]}

    # ---------------------- BUSINESS ----------------------
    def processBusinessRequest(self, requestId: str, payload: Dict[str, Any], context: Dict[str, Any]):
        token = context.get("token")
        if token not in self.sessions:
            return {"status": "failure", "message": "Unauthorized"}
        user = self.sessions[token]
        rtype = payload.get("type")

        if rtype == "book_seat":
            movie = payload["data"].get("movie")
            city = payload["data"].get("city")
            seats = payload["data"].get("seats", 1)
            
            # Try to decrement seats in database
            success = storage.update_movie_seats(self.db, movie, city, seats)
            
            if not success:
                return {
                    "status": "failure", 
                    "message": "Insufficient seats or movie not found"
                }
            
            # Create booking record with requestId
            booking_id = str(uuid.uuid4())
            entry = {
                "id": booking_id,
                "requestId": requestId,  # Store the requestId for frontend display
                "data": {
                    "user": user,
                    "username": user,  # Add username field for display
                    "movie": movie,
                    "city": city,
                    "seats": seats,
                    "timestamp": time.time()
                }
            }
            self.store["bookings"].append(entry)
            print(f"[SERVER] 🎟️ Booking created → User: {user}, Movie: {movie}, Seats: {seats}")
            return {"status": "success", "booking_id": booking_id, "requestId": requestId}

        return {"status": "failure", "message": "Unknown request type"}

    # ---------------------- ADMIN ----------------------
    def add_movie(self, token: str, movie: str, city: str, seats: int = 50):
        if token not in self.sessions:
            return {"status": "failure", "message": "Unauthorized"}
        
        # Add movie to database with seat count
        success = storage.add_movie_to_db(self.db, movie, city, seats)
        
        if not success:
            return {
                "status": "failure", 
                "message": "Movie already exists in this city"
            }
        
        print(f"[SERVER] 🍿 Movie added → {movie} ({city}) with {seats} seats")
        return {"status": "success"}


# ---------------------- FASTAPI WRAPPER ----------------------
app = FastAPI(title="Movie Booking Application Server")
server = ApplicationServer()

# Add CORS middleware for Docker environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "application-server"}

@app.post("/register")
async def register(req: Request):
    data = await req.json()
    return JSONResponse(server.register_user(data["username"], data["password"]))

@app.post("/login")
async def login(req: Request):
    data = await req.json()
    return JSONResponse(server.loginResponse(data["username"], data["password"]))

@app.get("/data/{data_type}")
async def get_data(data_type: str, token: str):
    return JSONResponse(server.getResponse(token, data_type))

@app.post("/business")
async def business(req: Request):
    data = await req.json()
    return JSONResponse(server.processBusinessRequest(
        requestId=data.get("requestId", ""),
        payload=data.get("payload", {}),
        context=data.get("context", {})
    ))

@app.post("/add_movie")
async def add_movie(req: Request):
    data = await req.json()
    return JSONResponse(server.add_movie(
        token=data["token"],
        movie=data["movie"],
        city=data["city"],
        seats=data.get("seats", 50)  # Default to 50 seats if not provided
    ))

# ---------------------- NEW: ADMIN ENDPOINTS ----------------------
@app.post("/admin/clear_database")
async def clear_database_endpoint(req: Request):
    """Admin endpoint to clear all movies and bookings"""
    data = await req.json()
    token = data.get("token")
    
    if token not in server.sessions:
        return JSONResponse({"status": "failure", "message": "Unauthorized"})
    
    user = server.sessions[token]
    if user != "admin":
        return JSONResponse({"status": "failure", "message": "Admin access required"})
    
    # Clear database
    movies = storage.get_all_movies(server.db)
    movies_count = len(movies)
    bookings_count = len(server.store["bookings"])
    
    # Clear SQLite movies
    cursor = server.db.cursor()
    cursor.execute("DELETE FROM movies")
    server.db.commit()
    
    # Clear in-memory bookings
    server.store["bookings"] = []
    
    print(f"[SERVER] 🗑️ Database cleared by admin - {bookings_count} bookings, {movies_count} movies removed")
    return JSONResponse({
        "status": "success",
        "message": "Database cleared successfully",
        "cleared": {
            "bookings": bookings_count,
            "movies": movies_count
        }
    })

@app.post("/admin/load_sample_data")
async def load_sample_data_endpoint(req: Request):
    """Admin endpoint to load sample movies for demonstration"""
    try:
        data = await req.json()
        token = data.get("token")
        
        if token not in server.sessions:
            return JSONResponse({"status": "failure", "message": "Unauthorized"})
        
        user = server.sessions[token]
        if user != "admin":
            return JSONResponse({"status": "failure", "message": "Admin access required"})
        
        # Clear existing data
        cursor = server.db.cursor()
        cursor.execute("DELETE FROM movies")
        server.db.commit()
        server.store["bookings"] = []
        
        # Load sample movies
        sample_movies = [
            ("Inception", "New York", 120),
            ("Inception", "Los Angeles", 100),
            ("The Dark Knight", "New York", 150),
            ("The Dark Knight", "Chicago", 80),
            ("Interstellar", "San Francisco", 90),
            ("Interstellar", "Boston", 110),
            ("Avengers Endgame", "New York", 200),
            ("Avengers Endgame", "Los Angeles", 180),
            ("Spider-Man", "Chicago", 100),
            ("Spider-Man", "Miami", 75),
            ("Joker", "New York", 85),
            ("Joker", "Seattle", 95),
            ("Parasite", "San Francisco", 70),
            ("Dune", "Los Angeles", 130),
            ("Oppenheimer", "New York", 160)
        ]
        
        for movie, city, seats in sample_movies:
            storage.add_movie_to_db(server.db, movie, city, seats)
        
        print(f"[SERVER] 📦 Sample data loaded - {len(sample_movies)} movies")
        return JSONResponse({
            "status": "success",
            "message": "Sample data loaded successfully",
            "loaded": {
                "movies": len(sample_movies)
            }
        })
    except Exception as e:
        print(f"[SERVER] ❌ Error loading sample data: {e}")
        return JSONResponse({
            "status": "failure",
            "message": f"Error loading sample data: {str(e)}"
        })

# Proxy endpoints for health checks (to avoid CORS issues)
@app.get("/proxy/llm/health")
async def proxy_llm_health():
    """Proxy endpoint for LLM health check"""
    try:
        llm_url = os.environ.get("LLM_SERVER_URL", "http://llm-server:8500")
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{llm_url}/health")
            return JSONResponse(response.json())
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"LLM server unreachable: {str(e)}",
            "model_loaded": False
        })

@app.post("/proxy/llm/ask")
async def proxy_llm_ask(req: Request):
    """Proxy endpoint for LLM ask"""
    try:
        data = await req.json()
        llm_url = os.environ.get("LLM_SERVER_URL", "http://llm-server:8500")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{llm_url}/ask", json=data)
            return JSONResponse(response.json())
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "answer": f"LLM server error: {str(e)}"
        })

@app.get("/proxy/raft/{node_id}/status")
async def proxy_raft_status(node_id: str):
    """Proxy endpoint for Raft node status"""
    try:
        port_map = {"1": "50051", "2": "50052", "3": "50053"}
        port = port_map.get(node_id, "50051")
        raft_url = os.environ.get(f"RAFT_NODE{node_id}_URL", f"http://raft-node{node_id}:{port}")
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{raft_url}/status")
            return JSONResponse(response.json())
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Raft node {node_id} unreachable: {str(e)}"
        })

@app.get("/admin/health/all")
async def check_all_health():
    """Check health of all services"""
    results = {}
    
    # App server
    results["app_server"] = {"status": "healthy", "service": "application-server"}
    
    # LLM server
    try:
        llm_url = os.environ.get("LLM_SERVER_URL", "http://llm-server:8500")
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{llm_url}/health")
            results["llm_server"] = response.json()
    except:
        results["llm_server"] = {"status": "error", "message": "Unreachable"}
    
    # Raft nodes
    for node_id in ["1", "2", "3"]:
        try:
            port_map = {"1": "50051", "2": "50052", "3": "50053"}
            port = port_map[node_id]
            raft_url = os.environ.get(f"RAFT_NODE{node_id}_URL", f"http://raft-node{node_id}:{port}")
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{raft_url}/status")
                results[f"raft_node_{node_id}"] = response.json()
        except:
            results[f"raft_node_{node_id}"] = {"status": "error", "message": "Unreachable"}
    
    return JSONResponse(results)

# ---------------------- RUN SERVER ----------------------
if __name__ == "__main__":
    # Use 0.0.0.0 to allow external connections (required for Docker)
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = int(os.environ.get("APP_PORT", "9000"))
    uvicorn.run(app, host=host, port=port)
