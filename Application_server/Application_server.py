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

# Add current directory to Python path for mongodb_storage import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import MongoDB storage module
from mongodb_storage import MongoDBStorage

# ---------------------- APPLICATION SERVER ----------------------
class ApplicationServer:
    def __init__(self):
        # Initialize MongoDB connection
        try:
            self.storage = MongoDBStorage()
            print("[SERVER]  MongoDB Storage initialized successfully")
        except Exception as e:
            print(f"[SERVER]  Failed to initialize MongoDB: {e}")
            raise

        print("[SERVER] Application Server initialized.")

    # ---------------------- AUTH ----------------------
    def register_user(self, username: str, password: str) -> Dict[str, Any]:
        result = self.storage.create_user(username, password)
        if result["status"] == "success":
            print(f"[SERVER] New user created → {username}")
        return result

    def loginResponse(self, username: str, password: str) -> Dict[str, Any]:
        # Verify credentials against MongoDB
        if not self.storage.verify_user(username, password):
            return {"status": "failure", "message": "Invalid credentials"}

        # Create session
        token = str(uuid.uuid4())
        self.storage.create_session(token, username)

        print(f"[SERVER]  User '{username}' logged in. Token = {token}")
        return {"status": "success", "token": token, "user": username}

    def logout(self, token: str) -> Dict[str, Any]:
        if self.storage.delete_session(token):
            print(f"[SERVER]  User logged out")
            return {"status": "success", "message": "Logged out successfully"}
        return {"status": "failure", "message": "Invalid token"}

    # ---------------------- DATA GETTER ----------------------
    def getResponse(self, token: str, data_type: str) -> Dict[str, Any]:
        # Verify session
        username = self.storage.get_session(token)
        if not username:
            return {"status": "failure", "message": "Unauthorized"}

        # Handle movies request
        if data_type == "movies":
            movies = self.storage.get_all_movies()
            # Format to match existing API response structure
            formatted_movies = [
                {"id": idx + 1, "data": movie}
                for idx, movie in enumerate(movies)
            ]
            return {"status": "success", "data": formatted_movies}

        # Handle bookings request
        if data_type == "bookings":
            if username == "admin":
                # Admin sees all bookings
                bookings = self.storage.get_all_bookings()
                return {"status": "success", "data": bookings}
            else:
                # Regular user sees only their bookings
                bookings = self.storage.get_user_bookings(username)
                return {"status": "success", "data": bookings}

        return {"status": "failure", "message": "Invalid data type"}

    # ---------------------- BUSINESS ----------------------
    def processBusinessRequest(self, requestId: str, payload: Dict[str, Any], context: Dict[str, Any]):
        token = context.get("token")
        username = self.storage.get_session(token)

        if not username:
            return {"status": "failure", "message": "Unauthorized"}

        rtype = payload.get("type")

        if rtype == "book_seat":
            movie = payload["data"].get("movie")
            city = payload["data"].get("city")
            seats = payload["data"].get("seats", 1)

            # Try to decrement seats in database
            success = self.storage.update_movie_seats(movie, city, seats)

            if not success:
                return {
                    "status": "failure",
                    "message": "Insufficient seats or movie not found"
                }

            # Create booking record
            booking_id = str(uuid.uuid4())
            booking_data = {
                "id": booking_id,
                "requestId": requestId,
                "data": {
                    "user": username,
                    "username": username,
                    "movie": movie,
                    "city": city,
                    "seats": seats,
                    "timestamp": time.time()
                }
            }

            self.storage.create_booking(booking_data)
            print(f"[SERVER]  Booking created → User: {username}, Movie: {movie}, Seats: {seats}")
            return {"status": "success", "booking_id": booking_id, "requestId": requestId}

        return {"status": "failure", "message": "Unknown request type"}

    # ---------------------- ADMIN ----------------------
    def add_movie(self, token: str, movie: str, city: str, seats: int = 50):
        username = self.storage.get_session(token)
        if not username:
            return {"status": "failure", "message": "Unauthorized"}

        success = self.storage.add_movie(movie, city, seats)

        if not success:
            return {
                "status": "failure",
                "message": "Movie already exists in this city"
            }

        print(f"[SERVER]  Movie added → {movie} ({city}) with {seats} seats")
        return {"status": "success"}

    def clear_database(self, token: str):
        """Clear all movies and bookings"""
        username = self.storage.get_session(token)
        if not username or username != "admin":
            return {"status": "failure", "message": "Admin access required"}

        movies_count = self.storage.clear_all_movies()
        bookings_count = self.storage.clear_all_bookings()

        print(f"[SERVER]  Database cleared - {movies_count} movies, {bookings_count} bookings")
        return {
            "status": "success",
            "message": "Database cleared successfully",
            "cleared": {
                "movies": movies_count,
                "bookings": bookings_count
            }
        }

    def load_sample_data(self, token: str):
        """Load sample movies"""
        username = self.storage.get_session(token)
        if not username or username != "admin":
            return {"status": "failure", "message": "Admin access required"}

        # Clear existing data first
        self.storage.clear_all_movies()
        self.storage.clear_all_bookings()

        # Load sample movies
        loaded_count = self.storage.load_sample_movies()

        print(f"[SERVER]  Sample data loaded - {loaded_count} movies")
        return {
            "status": "success",
            "message": "Sample data loaded successfully",
            "loaded": {
                "movies": loaded_count
            }
        }


# ---------------------- FASTAPI WRAPPER ----------------------
app = FastAPI(title="Movie Booking Application Server (MongoDB)")
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
    return {"status": "healthy", "service": "application-server", "database": "mongodb"}

@app.post("/register")
async def register(req: Request):
    data = await req.json()
    return JSONResponse(server.register_user(data["username"], data["password"]))

@app.post("/login")
async def login(req: Request):
    data = await req.json()
    return JSONResponse(server.loginResponse(data["username"], data["password"]))

@app.post("/logout")
async def logout(req: Request):
    data = await req.json()
    return JSONResponse(server.logout(data.get("token", "")))

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
        seats=data.get("seats", 50)
    ))

# ---------------------- ADMIN ENDPOINTS ----------------------
@app.post("/admin/clear_database")
async def clear_database_endpoint(req: Request):
    """Admin endpoint to clear all movies and bookings"""
    data = await req.json()
    token = data.get("token", "")
    return JSONResponse(server.clear_database(token))

@app.post("/admin/load_sample_data")
async def load_sample_data_endpoint(req: Request):
    """Admin endpoint to load sample movies for demonstration"""
    try:
        data = await req.json()
        token = data.get("token", "")
        return JSONResponse(server.load_sample_data(token))
    except Exception as e:
        print(f"[SERVER]  Error loading sample data: {e}")
        return JSONResponse({
            "status": "failure",
            "message": f"Error loading sample data: {str(e)}"
        })

# ---------------------- PROXY ENDPOINTS ----------------------
@app.get("/proxy/llm/health")
async def proxy_llm_health():
    """Proxy endpoint for LLM health check - LLM service is optional"""
    try:
        llm_url = os.environ.get("LLM_SERVER_URL", "http://llm-server:8500")
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{llm_url}/health")
            return JSONResponse(response.json())
    except httpx.ConnectError:
        return JSONResponse({
            "status": "unavailable",
            "message": "LLM server is not running (optional service)",
            "model_loaded": False,
            "service": "llm-server"
        })
    except httpx.TimeoutException:
        return JSONResponse({
            "status": "timeout",
            "message": "LLM server is starting up, please wait...",
            "model_loaded": False,
            "service": "llm-server"
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"LLM error: {str(e)}",
            "model_loaded": False,
            "service": "llm-server"
        })

@app.post("/proxy/llm/ask")
async def proxy_llm_ask(req: Request):
    """Proxy endpoint for LLM ask - DistilGPT-2 inference takes 2-5 seconds"""
    try:
        data = await req.json()
        llm_url = os.environ.get("LLM_SERVER_URL", "http://llm-server:8500")

        async with httpx.AsyncClient(timeout=15.0) as client:
            print(f"[LLM Proxy] Sending request to {llm_url}/ask")
            response = await client.post(f"{llm_url}/ask", json=data)
            print(f"[LLM Proxy] Got response: {response.status_code}")
            return JSONResponse(response.json())
    except httpx.TimeoutException as e:
        print(f"[LLM Proxy] Timeout error: {e}")
        return JSONResponse({
            "status": "error",
            "answer": "The AI is thinking... This should take 2-5 seconds. Please try again."
        })
    except Exception as e:
        print(f"[LLM Proxy] Error: {type(e).__name__}: {str(e)}")
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
    """Check health of all services - comprehensive health check"""
    results = {}

    # App server (always healthy if this endpoint is reached)
    results["app_server"] = {"status": "healthy", "service": "application-server", "database": "mongodb"}

    # LLM server (optional service)
    try:
        llm_url = os.environ.get("LLM_SERVER_URL", "http://llm-server:8500")
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{llm_url}/health")
            results["llm_server"] = response.json()
    except httpx.ConnectError:
        results["llm_server"] = {
            "status": "unavailable",
            "message": "LLM server not running (optional service)",
            "service": "llm-server"
        }
    except httpx.TimeoutException:
        results["llm_server"] = {
            "status": "timeout",
            "message": "LLM server timeout - may be starting up",
            "service": "llm-server"
        }
    except Exception as e:
        results["llm_server"] = {
            "status": "error",
            "message": f"Error: {str(e)}",
            "service": "llm-server"
        }

    # Raft nodes (critical services)
    for node_id in [1, 2, 3]:
        try:
            port_map = {1: "50051", 2: "50052", 3: "50053"}
            port = port_map[node_id]
            raft_url = os.environ.get(f"RAFT_NODE{node_id}_URL", f"http://raft-node{node_id}:{port}")
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{raft_url}/status")
                node_data = response.json()
                results[f"raft_node_{node_id}"] = node_data
        except httpx.ConnectError:
            results[f"raft_node_{node_id}"] = {
                "status": "unavailable",
                "message": f"Raft node {node_id} not running",
                "service": f"raft-node-{node_id}"
            }
        except httpx.TimeoutException:
            results[f"raft_node_{node_id}"] = {
                "status": "timeout",
                "message": f"Raft node {node_id} timeout",
                "service": f"raft-node-{node_id}"
            }
        except Exception as e:
            results[f"raft_node_{node_id}"] = {
                "status": "error",
                "message": f"Error: {str(e)}",
                "service": f"raft-node-{node_id}"
            }

    return JSONResponse(results)

# ---------------------- SERVER STARTUP ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9000))
    print(f"[SERVER]  Starting Application Server on port {port}")
    print(f"[SERVER]   Using MongoDB for persistent storage")
    uvicorn.run(app, host="0.0.0.0", port=port)
