import uuid
import time
import requests
import random

APP_SERVER_URL = "http://127.0.0.1:9000"  # Application server


class Client:
    def __init__(self):
        self.token = None
        self.username = None

    # --------------------------------------------------------------------
    # 🔐 LOGIN
    # --------------------------------------------------------------------
    def login(self, username: str, password: str):
        """Authenticate user via application server"""
        try:
            resp = requests.post(
                f"{APP_SERVER_URL}/login",
                json={"username": username, "password": password}
            ).json()

            if resp["status"] == "success":
                self.token = resp["token"]
                self.username = username
                print(f"[CLIENT-{username}] ✅ Logged in. Token = {self.token}")
            else:
                print(f"[CLIENT-{username}] ❌ Login failed: {resp['message']}")
        except Exception as e:
            print(f"[CLIENT-{username}] ERROR connecting to server: {e}")

    # --------------------------------------------------------------------
    # 🎬 GET MOVIES LIST
    # --------------------------------------------------------------------
    def get_movies(self):
        try:
            resp = requests.get(f"{APP_SERVER_URL}/data/movies", params={"token": self.token}).json()
            if resp["status"] == "success":
                print(f"[CLIENT-{self.username}] Movies: {resp['data']}")
                return resp["data"]
            else:
                print(f"[CLIENT-{self.username}] ❌ Failed to fetch movies: {resp['message']}")
        except Exception as e:
            print(f"[CLIENT-{self.username}] ERROR fetching movies: {e}")
        return []

    # --------------------------------------------------------------------
    # 🎟️ BOOK SEAT
    # --------------------------------------------------------------------
    def book_seat(self, movie, city, seats=1):
        try:
            # Include username in requestId so it can be correlated client-side if needed
            req_id = f"{self.username}-{uuid.uuid4()}" if self.username else str(uuid.uuid4())
            payload = {
                "requestId": req_id,
                "payload": {
                    "type": "book_seat",
                    "data": {"movie": movie, "city": city, "seats": seats}
                },
                "context": {"token": self.token}
            }
            resp = requests.post(f"{APP_SERVER_URL}/business", json=payload).json()
            print(f"[CLIENT-{self.username}] Booking result → {resp}")
        except Exception as e:
            print(f"[CLIENT-{self.username}] ERROR sending booking request: {e}")


# ------------------------------------------------------------------------
# 🧪 EXECUTION (this is what runs per spawned client)
# ------------------------------------------------------------------------
if __name__ == "__main__":
    client = Client()
    username = f"user_{random.randint(1, 9999)}"
    
    # Register first (optional)
    try:
        requests.post(f"{APP_SERVER_URL}/register", json={"username": username, "password": "pass123"})
    except:
        pass  # ignore if already exists

    client.login(username, "pass123")

    movies = client.get_movies()
    if movies:
        selected = random.choice(movies)
        client.book_seat(selected["data"]["movie"], selected["data"]["city"], seats=random.randint(1, 3))
    else:
        print(f"[CLIENT-{username}] No movies to book.")
