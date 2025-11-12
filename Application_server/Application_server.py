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
        
        # --- FIXED: Point to the Raft HTTP/FastAPI ports (8001-8003) ---
        nodes = os.environ.get("RAFT_HTTP_NODES", "http://127.0.0.1:8001,http://127.0.0.1:8002,http://127.0.0.1:8003")
        self.raft_nodes = [n.strip() for n in nodes.split(",") if n.strip()]
        
        # This server only handles user sessions. All data is in Raft.
        self.users: Dict[str, str] = {
            "admin": "123",      # default admin
        }
        self.sessions: Dict[str, str] = {}  # token -> username
        
        # Bookings are now fetched directly from Raft
        
        print("[SERVER] ✅ Application Server initialized.")
        print(f"[SERVER] 🌐 Raft HTTP nodes: {self.raft_nodes}")
    
    def _raft_request(self, path: str, method: str = 'get', json_payload: dict = None, params: dict = None):
        """
        Call the first responsive RAFT node over HTTP.
        This will proxy requests to the FastAPI apps running on ports 8001-8003.
        """
        last_err = None
        # Try all nodes until one responds
        for base in self.raft_nodes:
            url = f"{base.rstrip('/')}/{path.lstrip('/')}"
            try:
                if method.lower() == 'get':
                    r = requests.get(url, params=params, timeout=3)
                else:
                    r = requests.post(url, json=(json_payload or {}), timeout=3)
                
                r.raise_for_status() # Raise exception for 4xx/5xx
                return r.json() # Return successful JSON response
            
            except requests.exceptions.RequestException as e:
                # This node is down or not the leader, try next one
                last_err = e
                continue
                
        # If all nodes failed
        raise last_err if last_err is not None else RuntimeError('No RAFT nodes configured or reachable')

    # ---------------------- AUTH ----------------------
    def register_user(self, username: str, password: str) -> Dict[str, Any]:
        if username in self.users:
            return {"status": "failure", "message": "User already exists"}
        
        # 1. Create in Raft DB
        try:
            resp = self._raft_request(
                "create_user", 
                "post", 
                json_payload={"username": username, "password": password}
            )
            # Allow "exists" to be a soft success for simulation
            if resp.get("status") != "success" and "exists" not in resp.get("message", ""):
                 return {"status": "failure", "message": resp.get("message", "Failed to create user in Raft")}
        except Exception as e:
            print(f"[SERVER] ⚠️ Failed to create user in RAFT: {e}")
            return {"status": "failure", "message": f"Raft error: {e}"}
        
        # 2. Create in local session store (if Raft succeeded)
        self.users[username] = password
        print(f"[SERVER] New user created → {username}")
        return {"status": "success", "message": "User created"}

    def loginResponse(self, username: str, password: str) -> Dict[str, Any]:
        # 1. Check local cache first (for admin)
        if username in self.users and self.users[username] == password:
             # Grant session
            token = str(uuid.uuid4())
            self.sessions[token] = username
            print(f"[SERVER] 🔑 User '{username}' logged in (local). Token = {token}")
            return {"status": "success", "token": token, "user": username}

        # 2. Try to authenticate against Raft DB
        try:
            resp = self._raft_request(
                "authenticate",
                "post",
                json_payload={"username": username, "password": password}
            )
            if resp.get("status") == "success" and resp.get("user_id"):
                token = str(uuid.uuid4())
                self.sessions[token] = username
                print(f"[SERVER] 🔑 User '{username}' logged in (Raft). Token = {token}")
                return {"status": "success", "token": token, "user": username}
            else:
                 return {"status": "failure", "message": "Invalid credentials"}
        except Exception as e:
            print(f"[SERVER] ⚠️ Failed to authenticate with RAFT: {e}")
            return {"status": "failure", "message": "Invalid credentials"}

    # ---------------------- DATA GETTER ----------------------
    def getResponse(self, token: str, data_type: str) -> Dict[str, Any]:
        if token not in self.sessions:
            return {"status": "failure", "message": "Unauthorized"}
        
        username = self.sessions[token]
        
        # --- Get Movies (from Raft) ---
        if data_type == "movies":
            try:
                resp = self._raft_request("movies", "get")
                if resp.get("status") == "success":
                    # Convert RAFT response to match existing API response structure
                    formatted_movies = [
                        {"id": idx + 1, "data": m} # m is already {"movie": ..., "city": ..., "seats": ...}
                        for idx, m in enumerate(resp.get("movies", []))
                    ]
                    return {"status": "success", "data": formatted_movies}
                else:
                    return {"status": "failure", "message": "Failed to fetch movies from Raft"}
            except Exception as e:
                print(f"[SERVER] ⚠️ Failed to fetch movies from RAFT: {e}")
                return {"status": "failure", "message": "Failed to fetch movies"}
        
        # --- Get Bookings (from Raft DB) ---
        if data_type == "bookings":
            try:
                resp = self._raft_request("get_bookings", "get")
                if resp.get("status") != "success":
                    return {"status": "failure", "message": "Failed to fetch bookings"}
                
                all_bookings = resp.get("bookings", [])
                
                # Admins see all bookings
                if username == "admin":
                    return {"status": "success", "data": all_bookings}
                
                # Users see only their own bookings
                user_bookings = [
                    b for b in all_bookings 
                    if b.get("context", {}).get("username") == username
                ]
                return {"status": "success", "data": user_bookings}
            except Exception as e:
                print(f"[SERVER] ⚠️ Failed to fetch bookings from RAFT: {e}")
                return {"status": "failure", "message": "Failed to fetch bookings"}

        return {"status": "failure", "message": "Invalid data type"}

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
            
            # 1. Update seats in Raft
            try:
                resp = self._raft_request(
                    "update_seats",
                    "post",
                    json_payload={"movie": movie, "city": city, "seats": seats}
                )
                if resp.get("status") != "success":
                    return {
                        "status": "failure", 
                        "message": resp.get("message", "Insufficient seats or movie not found")
                    }
            except Exception as e:
                print(f"[SERVER] ⚠️ Failed to update seats in RAFT: {e}")
                return {"status": "failure", "message": f"Failed to book seats: {e}"}
            
            # 2. Create booking record (in Raft)
            booking_id = f"{user}-{uuid.uuid4()}"
            entry = {
                "id": booking_id,
                "data": { # This is the booking info
                    "movie": movie,
                    "city": city,
                    "seats": seats,
                    "timestamp": time.time()
                },
                "context": { # This contains the user info
                    "token": token,
                    "username": user
                }
            }
            
            try:
                resp = self._raft_request(
                    "add_booking",
                    "post",
                    json_payload=entry # Send the whole booking entry
                )
                if resp.get("status") != "success":
                    # TODO: Should try to roll back the seat update
                    return {"status": "failure", "message": "Failed to save booking record"}
            except Exception as e:
                 print(f"[SERVER] ⚠️ Failed to save booking to RAFT: {e}")
                 # TODO: Should try to roll back the seat update
                 return {"status": "failure", "message": f"Failed to save booking: {e}"}

            print(f"[SERVER] 🎟️ Booking created → {entry}")
            return {"status": "success", "booking_id": booking_id}

        return {"status": "failure", "message": "Unknown request type"}

    # ---------------------- ADMIN ----------------------
    def add_movie(self, token: str, movie: str, city: str, seats: int = 50):
        if token not in self.sessions:
            return {"status": "failure", "message": "Unauthorized"}
        
        try:
            resp = self._raft_request(
                "add_movie",
                "post",
                json_payload={"movie": movie, "city": city, "seats": seats}
            )
            if resp.get("status") == "success":
                print(f"[SERVER] 🍿 Movie added → {movie} ({city}) with {seats} seats")
                return {"status": "success"}
            else:
                return {
                    "status": "failure", 
                    "message": resp.get("message", "Movie already exists in this city")
                }
        except Exception as e:
            print(f"[SERVER] ⚠️ Failed to add movie to RAFT: {e}")
            return {"status": "failure", "message": f"Failed to add movie: {e}"}
    
    # ---------------------- ADMIN: DATABASE MANAGEMENT ----------------------
    def clear_database(self, token: str) -> Dict[str, Any]:
        """Clear all bookings from RAFT-hosted database."""
        if token not in self.sessions:
            return {"status": "failure", "message": "Unauthorized"}
        
        user = self.sessions[token]
        if user != "admin":
            return {"status": "failure", "message": "Admin access required"}
        
        try:
            resp = self._raft_request("clear_bookings", "post", json_payload={"token": token})
            if resp.get("status") != "success":
                return {"status": "failure", "message": "Failed to clear bookings in Raft"}
        except Exception as e:
            print(f"[SERVER] ⚠️ Failed to clear bookings in RAFT: {e}")
            return {"status": "failure", "message": f"Raft error: {e}"}
        
        print(f"[SERVER] 🗑️ Raft bookings cleared by admin")
        return {
            "status": "success",
            "message": "Raft bookings cleared successfully",
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
        errors = []
        try:
            for movie, city, seats in sample_movies:
                resp = self._raft_request(
                    "add_movie",
                    "post",
                    json_payload={"movie": movie, "city": city, "seats": seats}
                )
                if resp.get("status") == "success":
                    success_count += 1
                else:
                    # Ignore "exists" errors, but log others
                    if "exists" not in resp.get("message", ""):
                        errors.append(f"{movie} ({city}): {resp.get('message')}")

        except Exception as e:
            print(f"[SERVER] ⚠️ Failed to load sample data to RAFT: {e}")
            return {"status": "failure", "message": f"Failed to load sample data: {e}"}
        
        print(f"[SERVER] 📦 Sample data loaded - {success_count}/{len(sample_movies)} movies")
        return {
            "status": "success",
            "message": "Sample data loaded successfully",
            "loaded": {"movies": success_count},
            "errors": errors
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

# --- NEW: RAFT PROGRESS ENDPOINT ---
@app.get("/raft_progress")
async def raft_progress():
    """
    Fetches the status from one of the Raft nodes.
    The _raft_request function will try nodes until one responds.
    The responding node (if leader) will include its progress.
    """
    try:
        # We just need to hit the /status endpoint.
        # The raft_node.py /status endpoint is now smart:
        # if it's the leader, it includes next_index and match_index.
        resp = server._raft_request("status", "get")
        
        # The response from /status is already in the correct format
        # e.g., {"is_leader": true, "next_index": ...}
        return JSONResponse({"status": "success", **resp})
    
    except Exception as e:
        print(f"[SERVER] ⚠️ Failed to get /raft_progress: {e}")
        return JSONResponse({"status": "failure", "message": str(e)})
# --- END NEW ---


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
    # This function is now just a simple wrapper
    return JSONResponse(server.load_sample_data(token))


@app.get("/admin/raft_logs")
async def admin_raft_logs(token: str):
    """Return persisted raft logs (admin only)"""
    if token not in server.sessions:
        return JSONResponse({"status": "failure", "message": "Unauthorized"})
    user = server.sessions[token]
    if user != "admin":
        return JSONResponse({"status": "failure", "message": "Admin access required"})

    try:
        resp = server._raft_request("raft_logs", "get")
        return JSONResponse(resp)
    except Exception as e:
         return JSONResponse({"status": "failure", "message": str(e)})


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
    city = data.get("city") # Allow specifying city
    seats_per_client = int(data.get("seats_per_client", 1))

    import threading

    results = []
    results_lock = threading.Lock()

    def worker(client_id):
        # create temp user
        temp_user = f"sim_user_{int(time.time()*1000)}_{client_id}"
        temp_pass = "password"
        
        # We must use the public /register endpoint
        register_resp = server.register_user(temp_user, temp_pass)
        if register_resp.get("status") != "success" and "exists" not in register_resp.get("message", ""):
             with results_lock:
                results.append({"user": temp_user, "status": "register_failed"})
             return

        login_res = server.loginResponse(temp_user, temp_pass)
        if login_res.get("status") != "success":
            with results_lock:
                results.append({"user": temp_user, "status": "login_failed"})
            return
        client_token = login_res.get("token")

        payload = {
            "type": "book_seat",
            "data": {"movie": movie, "city": city, "seats": seats_per_client}
        }

        if not movie:
            with results_lock:
                results.append({"user": temp_user, "status": "no_movie_specified"})
            return

        # If city is not provided, try to find one
        if not city:
            try:
                movies_resp = server.getResponse(client_token, "movies")
                if movies_resp.get("status") == "success":
                    for m_entry in movies_resp.get("data", []):
                        m_data = m_entry.get("data", {})
                        if m_data.get("movie") == movie:
                            payload["data"]["city"] = m_data.get("city")
                            break
            except Exception:
                pass # Will fail if no city is found
        
        if not payload["data"]["city"]:
            with results_lock:
                results.append({"user": temp_user, "status": "could_not_find_city"})
            return

        resp = server.processBusinessRequest(
            requestId=f"sim-{temp_user}", 
            payload=payload, 
            context={"token": client_token}
        )
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
    """Proxy health check for services (app server, raft nodes, llm)."""
    # Require admin token
    if token not in server.sessions:
        return JSONResponse({"status": "failure", "message": "Unauthorized"})
    if server.sessions[token] != "admin":
        return JSONResponse({"status": "failure", "message": "Admin access required"})

    # --- THIS IS THE FIX ---
    # The Raft HTTP servers are on 8001-8003.
    # The gRPC servers are on 50051-50053.
    # We must use the HTTP ports here.
    services = {
        "app_server": f"http://127.0.0.1:{os.environ.get('APP_PORT', '9000')}/health",
        "llm": "http://1.2.3.4:8500/health", # Placeholder, update if needed
        "raft_node_1": "http://127.0.0.1:8001/status",
        "raft_node_2": "http://127.0.0.1:8002/status",
        "raft_node_3": "http://127.0.0.1:8003/status",
    }
    # --- END FIX ---

    results = {}
    for name, url in services.items():
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
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