import uuid
import time
import os
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ---------------------- APPLICATION SERVER ----------------------
class ApplicationServer:
    def __init__(self):
        self.users: Dict[str, str] = {
            "admin": "123",     # default admin
            "utkarsh": "password123"
        }
        self.sessions: Dict[str, str] = {}  # token -> username
        self.store = {
            "movies": [],
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
    def add_movie(self, token: str, movie: str, city: str):
        if token not in self.sessions:
            return {"status": "failure", "message": "Unauthorized"}
        entry = {
            "id": len(self.store["movies"]) + 1,
            "data": {"movie": movie, "city": city},
        }
        self.store["movies"].append(entry)
        print(f"[SERVER] 🍿 Movie added → {movie} ({city})")
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
        city=data["city"]
    ))

# ---------------------- RUN SERVER ----------------------
if __name__ == "__main__":
    # Use 0.0.0.0 to allow external connections (required for Docker)
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = int(os.environ.get("APP_PORT", "9000"))
    uvicorn.run(app, host=host, port=port)
