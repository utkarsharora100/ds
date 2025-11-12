import uuid
import time
import os
import sys
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx
import random

# ---------------------- RAFT CLIENT ----------------------
class RaftClient:
    """Client to interact with the Raft cluster."""
    def __init__(self, node_addrs: List[str]):
        self.nodes = node_addrs
        self.leader_id = None

    async def _find_leader(self) -> Optional[str]:
        """Probe nodes to find the current leader."""
        # Shuffle nodes to distribute probe load
        random.shuffle(self.nodes)
        for node_addr in self.nodes:
            try:
                async with httpx.AsyncClient(timeout=1.0) as client:
                    resp = await client.get(f"http://{node_addr}/status")
                    if resp.status_code == 200 and resp.json().get("state") == "leader":
                        self.leader_id = node_addr
                        print(f"[RAFT CLIENT] Found leader: {self.leader_id}")
                        return self.leader_id
            except httpx.RequestError:
                print(f"[RAFT CLIENT] Node {node_addr} is down.")
                continue
        print("[RAFT CLIENT] ⚠️ No leader found.")
        return None

    async def get_leader(self) -> Optional[str]:
        """Get the current leader, finding it if necessary."""
        if self.leader_id:
            # Check if current leader is still the leader
            try:
                async with httpx.AsyncClient(timeout=1.0) as client:
                    resp = await client.get(f"http://{self.leader_id}/status")
                    if resp.status_code == 200 and resp.json().get("state") == "leader":
                        return self.leader_id
            except httpx.RequestError:
                self.leader_id = None # Leader is down

        # If no leader or old leader is gone, find a new one
        return await self._find_leader()

    async def propose(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send a command to the Raft cluster to be added to the log."""
        leader = await self.get_leader()
        if not leader:
            return {"status": "failure", "message": "No leader available in the Raft cluster."}

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(f"http://{leader}/propose", json=command)
                return resp.json()
        except httpx.RequestError as e:
            return {"status": "failure", "message": f"Failed to communicate with Raft leader: {e}"}

    async def query(self, key: str) -> Dict[str, Any]:
        """Query the state machine of the Raft cluster."""
        leader = await self.get_leader()
        if not leader:
            return {"status": "failure", "message": "No leader available in the Raft cluster."}
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"http://{leader}/query/{key}")
                return resp.json()
        except httpx.RequestError as e:
            return {"status": "failure", "message": f"Failed to communicate with Raft leader: {e}"}


# ---------------------- APPLICATION SERVER ----------------------
class ApplicationServer:
    def __init__(self):
        # Raft nodes are identified by their service names in Docker Compose
        raft_nodes = ["raft-node1:50051", "raft-node2:50052", "raft-node3:50053"]
        self.raft_client = RaftClient(raft_nodes)
        
        self.sessions: Dict[str, str] = {}  # token -> username
        print("[SERVER] ✅ Application Server initialized.")

    # ---------------------- AUTH ----------------------
    async def register_user(self, username: str, password: str) -> Dict[str, Any]:
        command = {"type": "register_user", "username": username, "password": password}
        result = await self.raft_client.propose(command)
        if result.get("status") == "success":
            print(f"[SERVER] New user registration proposed → {username}")
        return result

    async def loginResponse(self, username: str, password: str) -> Dict[str, Any]:
        # Query the Raft state for the user
        users_state = await self.raft_client.query("users")
        users = users_state.get("data", {})
        
        if username not in users or users[username] != password:
            return {"status": "failure", "message": "Invalid credentials"}
        
        token = str(uuid.uuid4())
        self.sessions[token] = username
        print(f"[SERVER] 🔑 User '{username}' logged in. Token = {token}")
        return {"status": "success", "token": token, "user": username}

    # ---------------------- DATA GETTER ----------------------
    async def getResponse(self, token: str, data_type: str) -> Dict[str, Any]:
        if token not in self.sessions:
            return {"status": "failure", "message": "Unauthorized"}
        
        # All data is now fetched from the Raft state machine
        result = await self.raft_client.query(data_type)
        return result

    # ---------------------- BUSINESS ----------------------
    async def processBusinessRequest(self, requestId: str, payload: Dict[str, Any], context: Dict[str, Any]):
        token = context.get("token")
        if token not in self.sessions:
            return {"status": "failure", "message": "Unauthorized"}
        user = self.sessions[token]
        rtype = payload.get("type")

        if rtype == "book_seat":
            command = {
                "type": "book_seat",
                "user": user,
                "movie": payload["data"].get("movie"),
                "city": payload["data"].get("city"),
                "seats": payload["data"].get("seats", 1),
                "booking_id": str(uuid.uuid4()),
                "timestamp": time.time()
            }
            result = await self.raft_client.propose(command)
            if result.get("status") == "success":
                print(f"[SERVER] 🎟️ Booking proposed for {user} → {command['movie']}")
            return result

        return {"status": "failure", "message": "Unknown request type"}

    # ---------------------- ADMIN ----------------------
    async def add_movie(self, token: str, movie: str, city: str, seats: int = 50):
        if token not in self.sessions:
            return {"status": "failure", "message": "Unauthorized"}
        
        command = {"type": "add_movie", "movie": movie, "city": city, "seats": seats}
        result = await self.raft_client.propose(command)
        if result.get("status") == "success":
            print(f"[SERVER] 🍿 Movie proposed → {movie} ({city}) with {seats} seats")
        return result


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
    return JSONResponse(await server.add_movie(
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
    
    # Propose a command to clear the database in the Raft state machine
    command = {"type": "clear_database"}
    result = await server.raft_client.propose(command)
    
    if result.get("status") == "success":
        cleared_counts = result.get("cleared", {})
        print(f"[SERVER] 🗑️ Database clear proposed by admin. "
              f"Cleared {cleared_counts.get('movies', 0)} movies and "
              f"{cleared_counts.get('bookings', 0)} bookings.")
    
    return JSONResponse(result)

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
        
        # Propose a command to load sample data in the Raft state machine
        command = {"type": "load_sample_data"}
        result = await server.raft_client.propose(command)

        if result.get("status") == "success":
            loaded_count = result.get("loaded", {}).get("movies", 0)
            print(f"[SERVER] 📦 Sample data load proposed - {loaded_count} movies")
        
        return JSONResponse(result)

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
    results["app_server"] = {"status": "healthy", "service": "application-server", "model_loaded": True}
    
    # LLM server
    llm_health_response = await proxy_llm_health()
    results["llm_server"] = llm_health_response.body.decode()
    
    # Raft nodes
    for node_id in ["1", "2", "3"]:
        raft_health_response = await proxy_raft_status(node_id)
        results[f"raft_node_{node_id}"] = raft_health_response.body.decode()
    
    return JSONResponse(results)

# ---------------------- RUN SERVER ----------------------
if __name__ == "__main__":
    # Use 0.0.0.0 to allow external connections (required for Docker)
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = int(os.environ.get("APP_PORT", "9000"))
    uvicorn.run(app, host=host, port=port)
