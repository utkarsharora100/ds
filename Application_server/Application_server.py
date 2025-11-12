import uuid
import time
import os
import sys
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests

# Import storage module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from llm import storage

# ---------------------- APPLICATION SERVER ----------------------
class ApplicationServer:
    def __init__(self, raft_leader_address: str = None):
        # ✅ NEW: Initialize RAFT client stub for database operations
        nodes = raft_leader_address or os.environ.get("RAFT_NODES", "http://127.0.0.1:50051,http://127.0.0.1:50052,http://127.0.0.1:50053")
        self.raft_nodes = [n.strip() for n in nodes.split(",") if n.strip()]
        
        # For backward compatibility during development, still keep local sessions
        # (Users/sessions stay in app server, database queries go to RAFT)
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
        print(f"[SERVER] 🌐 RAFT nodes: {self.raft_nodes}")
    
    def _connect_to_raft(self):
        # kept for compatibility; no-op when using HTTP
        return

    def _raft_request(self, path: str, method: str = 'get', json_payload: dict = None, params: dict = None):
        """Call the first responsive RAFT node over HTTP. Returns response.json() or raises."""
        last_err = None
        for base in self.raft_nodes:
            url = f"{base.rstrip('/')}/{path.lstrip('/')}"
            try:
                if method.lower() == 'get':
                    r = requests.get(url, params=params, timeout=3)
                else:
                    r = requests.post(url, json=(json_payload or {}), timeout=3)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                last_err = e
                continue
        raise last_err if last_err is not None else RuntimeError('No RAFT nodes configured')

    # ---------------------- AUTH ----------------------
    def register_user(self, username: str, password: str) -> Dict[str, Any]:
        if username in self.users:
            return {"status": "failure", "message": "User already exists"}
        self.users[username] = password
        
        # ✅ NEW: Create user in RAFT-hosted database
        try:
            if self.raft_stub:
                req = raft_pb2.CreateUserRequest(username=username, password=password)
                resp = self.raft_stub.CreateUser(req)
                if not resp.success:
                    return {"status": "failure", "message": "Failed to create user in RAFT"}
        except Exception as e:
            print(f"[SERVER] ⚠️ Failed to create user in RAFT: {e}")
            # Continue with local user creation for backward compatibility
        
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
        
        # If requesting movies, fetch from RAFT database
        if data_type == "movies":
            try:
                if self.raft_stub:
                    resp = self.raft_stub.GetMovies(raft_pb2.GetMoviesRequest())
                    # Convert RAFT response to match existing API response structure
                    formatted_movies = [
                        {"id": idx + 1, "data": {"movie": m.title, "city": m.city, "seats": m.seats}}
                        for idx, m in enumerate(resp.movies)
                    ]
                    return {"status": "success", "data": formatted_movies}
                else:
                    return {"status": "failure", "message": "RAFT connection not available"}
            except Exception as e:
                print(f"[SERVER] ⚠️ Failed to fetch movies from RAFT: {e}")
                return {"status": "failure", "message": "Failed to fetch movies"}
        
        # For bookings, only return bookings belonging to the requesting user (admins see all)
        if data_type == "bookings":
            all_bookings = self.store.get("bookings", [])
            # admins may view all bookings
            if username == "admin":
                return {"status": "success", "data": all_bookings}
            # otherwise filter to bookings owned by this username
            user_bookings = [b for b in all_bookings if b.get("data", {}).get("user") == username]
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
            
            # ✅ NEW: Try to decrement seats in RAFT database
            try:
                if self.raft_stub:
                    req = raft_pb2.UpdateSeatsRequest(movie=movie, city=city, seats=seats)
                    resp = self.raft_stub.UpdateSeats(req)
                    if not resp.success:
                        return {
                            "status": "failure", 
                            "message": "Insufficient seats or movie not found"
                        }
                else:
                    return {"status": "failure", "message": "RAFT connection not available"}
            except Exception as e:
                print(f"[SERVER] ⚠️ Failed to update seats in RAFT: {e}")
                return {"status": "failure", "message": "Failed to book seats"}
            
            # Create booking record (server-generated id includes username for easy correlation)
            booking_id = f"{user}-{uuid.uuid4()}"
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
        
        # ✅ NEW: Add movie to RAFT-hosted database
        try:
            if self.raft_stub:
                req = raft_pb2.AddMovieRequest(movie=movie, city=city, seats=seats)
                resp = self.raft_stub.AddMovie(req)
                if not resp.success:
                    return {
                        "status": "failure", 
                        "message": resp.message or "Movie already exists in this city"
                    }
            else:
                return {"status": "failure", "message": "RAFT connection not available"}
        except Exception as e:
            print(f"[SERVER] ⚠️ Failed to add movie to RAFT: {e}")
            return {"status": "failure", "message": "Failed to add movie"}
        
        print(f"[SERVER] 🍿 Movie added → {movie} ({city}) with {seats} seats")
        return {"status": "success"}
    
    # ---------------------- ADMIN: DATABASE MANAGEMENT ----------------------
    def clear_database(self, token: str) -> Dict[str, Any]:
        """Clear all movies from RAFT-hosted database."""
        if token not in self.sessions:
            return {"status": "failure", "message": "Unauthorized"}
        
        user = self.sessions[token]
        if user != "admin":
            return {"status": "failure", "message": "Admin access required"}
        
        # For now, we can't easily clear RAFT database from app server
        # Instead, we clear local bookings
        bookings_count = len(self.store["bookings"])
        self.store["bookings"] = []
        
        print(f"[SERVER] 🗑️ Local data cleared by admin - {bookings_count} bookings removed")
        return {
            "status": "success",
            "message": "Database cleared successfully",
            "cleared": {
                "bookings": bookings_count,
                "movies": 0  # Movies are in RAFT
            }
        }
    
    def load_sample_data(self, token: str) -> Dict[str, Any]:
        """Load sample movies to RAFT-hosted database."""
        if token not in self.sessions:
            return {"status": "failure", "message": "Unauthorized"}
        
        user = self.sessions[token]
        if user != "admin":
            return {"status": "failure", "message": "Admin access required"}
        
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
        
        success_count = 0
        try:
            if self.raft_stub:
                for movie, city, seats in sample_movies:
                    req = raft_pb2.AddMovieRequest(movie=movie, city=city, seats=seats)
                    resp = self.raft_stub.AddMovie(req)
                    if resp.success:
                        success_count += 1
            else:
                return {"status": "failure", "message": "RAFT connection not available"}
        except Exception as e:
            print(f"[SERVER] ⚠️ Failed to load sample data to RAFT: {e}")
            return {"status": "failure", "message": "Failed to load sample data"}
        
        print(f"[SERVER] 📦 Sample data loaded - {success_count}/{len(sample_movies)} movies")
        return {
            "status": "success",
            "message": "Sample data loaded successfully",
            "loaded": {
                "movies": success_count
            }
        }


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
    return JSONResponse(server.clear_database(token))

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


@app.get("/admin/raft_logs")
async def admin_raft_logs(token: str):
    """Return persisted raft logs (admin only)"""
    if token not in server.sessions:
        return JSONResponse({"status": "failure", "message": "Unauthorized"})
    user = server.sessions[token]
    if user != "admin":
        return JSONResponse({"status": "failure", "message": "Admin access required"})

    logs = storage.get_all_logs(server.db)
    return JSONResponse({"status": "success", "logs": logs})


@app.post("/admin/simulate_clients")
async def admin_simulate_clients(req: Request):
    """Admin endpoint to simulate multiple clients booking concurrently.
    Expects JSON: { token, num_clients (int), movie (str), seats_per_client (int) }
    """
    data = await req.json()
    token = data.get("token")
    if token not in server.sessions:
        return JSONResponse({"status": "failure", "message": "Unauthorized"})
    user = server.sessions[token]
    if user != "admin":
        return JSONResponse({"status": "failure", "message": "Admin access required"})

    num_clients = int(data.get("num_clients", 10))
    movie = data.get("movie")
    seats_per_client = int(data.get("seats_per_client", 1))

    import threading

    results = []
    results_lock = threading.Lock()

    def worker(client_id):
        # create temp user
        temp_user = f"sim_user_{int(time.time()*1000)}_{client_id}"
        temp_pass = "password"
        server.register_user(temp_user, temp_pass)
        login_res = server.loginResponse(temp_user, temp_pass)
        if login_res.get("status") != "success":
            with results_lock:
                results.append({"user": temp_user, "status": "login_failed"})
            return
        client_token = login_res.get("token")

        payload = {
            "type": "book_seat",
            "data": {"movie": movie, "city": None, "seats": seats_per_client}
        }

        # Try to determine a city if not provided by picking first matching movie
        if not movie:
            with results_lock:
                results.append({"user": temp_user, "status": "no_movie_specified"})
            return

        # If movie exists in DB with cities, pick the first matching city
        try:
            # find a movie row with matching title
            rows = server.db.cursor()
            rows.execute("SELECT title, language FROM movies WHERE title = ?", (movie,))
            r = rows.fetchone()
            if r:
                payload["data"]["city"] = r[1]
        except Exception:
            payload["data"]["city"] = None

        resp = server.processBusinessRequest(requestId=f"sim-{temp_user}", payload=payload, context={"token": client_token})
        with results_lock:
            results.append({"user": temp_user, "result": resp})

    threads = []
    for i in range(num_clients):
        t = threading.Thread(target=worker, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # Summarize results
    success = sum(1 for r in results if r.get("result", {}).get("status") == "success")
    failed = len(results) - success

    return JSONResponse({"status": "success", "summary": {"total": len(results), "success": success, "failed": failed}, "details": results})


@app.get("/admin/check_cluster_health")
async def admin_check_cluster_health(token: str):
    """Proxy health check for services (app server, raft nodes, llm).
    This endpoint requires an admin token and aggregates health checks so the browser doesn't need CORS access to raft nodes.
    """
    # Require admin token
    if token not in server.sessions:
        return JSONResponse({"status": "failure", "message": "Unauthorized"})
    if server.sessions[token] != "admin":
        return JSONResponse({"status": "failure", "message": "Admin access required"})

    services = {
        "app_server": f"http://127.0.0.1:{os.environ.get('APP_PORT', '9000')}/health",
        "llm": "http://127.0.0.1:8500/health",
        "raft_node_1": "http://127.0.0.1:50051/status",
        "raft_node_2": "http://127.0.0.1:50052/status",
        "raft_node_3": "http://127.0.0.1:50053/status",
    }

    results = {}
    for name, url in services.items():
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                # try parse json
                try:
                    results[name] = {"ok": True, "data": r.json()}
                except Exception:
                    results[name] = {"ok": True, "data": r.text}
            else:
                results[name] = {"ok": False, "status_code": r.status_code, "text": r.text}
        except Exception as e:
            results[name] = {"ok": False, "error": str(e)}

    return JSONResponse({"status": "success", "services": results})

# ---------------------- RUN SERVER ----------------------
if __name__ == "__main__":
    # Use 0.0.0.0 to allow external connections (required for Docker)
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = int(os.environ.get("APP_PORT", "9000"))
    uvicorn.run(app, host=host, port=port)
