import uuid
import time
import os
import sys
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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
        
        # For bookings, include username in context for filtering
        if data_type == "bookings":
            # Add username context to each booking for client-side filtering
            bookings_with_context = []
            for booking in self.store.get("bookings", []):
                booking_copy = booking.copy()
                # Add context with username from booking data
                booking_copy["context"] = {
                    "username": booking["data"].get("user", "unknown")
                }
                bookings_with_context.append(booking_copy)
            return {"status": "success", "data": bookings_with_context}
        
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
            
            # Create booking record
            booking_id = str(uuid.uuid4())
            entry = {
                "id": booking_id,
                "data": {
                    "user": user,
                    "movie": movie,
                    "city": city,
                    "seats": seats,
                    "timestamp": time.time()
                }
            }
            self.store["bookings"].append(entry)
            print(f"[SERVER] 🎟️ Booking created → {entry}")
            return {"status": "success", "booking_id": booking_id}

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

# ---------------------- RUN SERVER ----------------------
if __name__ == "__main__":
    # Use 0.0.0.0 to allow external connections (required for Docker)
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = int(os.environ.get("APP_PORT", "9000"))
    uvicorn.run(app, host=host, port=port)
