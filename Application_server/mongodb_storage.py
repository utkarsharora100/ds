"""
MongoDB Storage Module for Movie Booking System
Replaces in-memory and SQLite storage with MongoDB
"""

import os
from typing import Dict, List, Optional, Any
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
import time

class MongoDBStorage:
    def __init__(self, connection_string: str = None):
        """
        Initialize MongoDB connection
        """
        if connection_string is None:
            # Default connection string for Docker environment
            connection_string = os.environ.get(
                "MONGODB_URL",
                "mongodb://mongodb:27017/"
            )

        self.client = MongoClient(connection_string)
        self.db = self.client['movie_booking']

        # Collections
        self.users = self.db['users']
        self.sessions = self.db['sessions']
        self.movies = self.db['movies']
        self.bookings = self.db['bookings']

        # Create indexes for better performance
        self._create_indexes()

        # Initialize with default admin user if not exists
        self._initialize_default_data()

        print("[MONGODB] ✅ Connected to MongoDB successfully")

    def _create_indexes(self):
        """Create indexes for better query performance"""
        # Unique index on username
        self.users.create_index([("username", ASCENDING)], unique=True)

        # Index on session tokens
        self.sessions.create_index([("token", ASCENDING)], unique=True)

        # Index on movie + city combination (unique)
        self.movies.create_index([("movie", ASCENDING), ("city", ASCENDING)], unique=True)

        # Index on bookings
        self.bookings.create_index([("user", ASCENDING)])
        self.bookings.create_index([("requestId", ASCENDING)])

        print("[MONGODB] ✅ Indexes created")

    def _initialize_default_data(self):
        """Initialize default admin user and sample user"""
        try:
            # Create default admin if not exists
            if self.users.count_documents({"username": "admin"}) == 0:
                self.users.insert_one({
                    "username": "admin",
                    "password": "123",
                    "created_at": time.time()
                })
                print("[MONGODB] ✅ Default admin user created")

            # Create sample user if not exists
            if self.users.count_documents({"username": "utkarsh"}) == 0:
                self.users.insert_one({
                    "username": "utkarsh",
                    "password": "password123",
                    "created_at": time.time()
                })
                print("[MONGODB] ✅ Sample user 'utkarsh' created")

        except Exception as e:
            print(f"[MONGODB] ⚠️  Error initializing default data: {e}")

    # ==================== USER MANAGEMENT ====================

    def create_user(self, username: str, password: str) -> Dict[str, Any]:
        """Create a new user"""
        try:
            self.users.insert_one({
                "username": username,
                "password": password,
                "created_at": time.time()
            })
            print(f"[MONGODB] ✅ User created: {username}")
            return {"status": "success", "message": "User created"}
        except DuplicateKeyError:
            return {"status": "failure", "message": "User already exists"}
        except Exception as e:
            print(f"[MONGODB] ❌ Error creating user: {e}")
            return {"status": "failure", "message": str(e)}

    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        user = self.users.find_one({"username": username, "password": password})
        return user is not None

    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return self.users.find_one({"username": username}, {"_id": 0, "password": 0})

    # ==================== SESSION MANAGEMENT ====================

    def create_session(self, token: str, username: str) -> bool:
        """Create a new session"""
        try:
            self.sessions.insert_one({
                "token": token,
                "username": username,
                "created_at": time.time()
            })
            return True
        except Exception as e:
            print(f"[MONGODB] ❌ Error creating session: {e}")
            return False

    def get_session(self, token: str) -> Optional[str]:
        """Get username from session token"""
        session = self.sessions.find_one({"token": token})
        return session["username"] if session else None

    def delete_session(self, token: str) -> bool:
        """Delete a session"""
        result = self.sessions.delete_one({"token": token})
        return result.deleted_count > 0

    # ==================== MOVIE MANAGEMENT ====================

    def add_movie(self, movie: str, city: str, seats: int = 50) -> bool:
        """Add a new movie"""
        try:
            self.movies.insert_one({
                "movie": movie,
                "city": city,
                "seats": seats,
                "created_at": time.time()
            })
            print(f"[MONGODB] ✅ Movie added: {movie} ({city}) - {seats} seats")
            return True
        except DuplicateKeyError:
            print(f"[MONGODB] ⚠️  Movie already exists: {movie} ({city})")
            return False
        except Exception as e:
            print(f"[MONGODB] ❌ Error adding movie: {e}")
            return False

    def get_all_movies(self) -> List[Dict]:
        """Get all movies"""
        movies = list(self.movies.find({}, {"_id": 0}))
        return movies

    def update_movie_seats(self, movie: str, city: str, seats_to_book: int) -> bool:
        """Update movie seats (decrement)"""
        result = self.movies.update_one(
            {"movie": movie, "city": city, "seats": {"$gte": seats_to_book}},
            {"$inc": {"seats": -seats_to_book}}
        )

        if result.modified_count > 0:
            print(f"[MONGODB] ✅ Seats updated: {movie} ({city}) - booked {seats_to_book}")
            return True
        else:
            print(f"[MONGODB] ❌ Insufficient seats or movie not found: {movie} ({city})")
            return False

    def clear_all_movies(self) -> int:
        """Clear all movies"""
        result = self.movies.delete_many({})
        count = result.deleted_count
        print(f"[MONGODB] 🗑️  Cleared {count} movies")
        return count

    # ==================== BOOKING MANAGEMENT ====================

    def create_booking(self, booking_data: Dict) -> bool:
        """Create a new booking"""
        try:
            booking_data["created_at"] = time.time()
            self.bookings.insert_one(booking_data)
            print(f"[MONGODB] ✅ Booking created: {booking_data.get('id')}")
            return True
        except Exception as e:
            print(f"[MONGODB] ❌ Error creating booking: {e}")
            return False

    def get_all_bookings(self) -> List[Dict]:
        """Get all bookings (admin view)"""
        bookings = list(self.bookings.find({}, {"_id": 0}))
        return bookings

    def get_user_bookings(self, username: str) -> List[Dict]:
        """Get bookings for a specific user"""
        bookings = list(self.bookings.find({"data.user": username}, {"_id": 0}))
        return bookings

    def clear_all_bookings(self) -> int:
        """Clear all bookings"""
        result = self.bookings.delete_many({})
        count = result.deleted_count
        print(f"[MONGODB] 🗑️  Cleared {count} bookings")
        return count

    # ==================== SAMPLE DATA ====================

    def load_sample_movies(self) -> int:
        """Load sample movies for testing"""
        sample_movies = [
            {"movie": "Inception", "city": "New York", "seats": 50},
            {"movie": "The Dark Knight", "city": "Los Angeles", "seats": 60},
            {"movie": "Interstellar", "city": "Chicago", "seats": 45},
            {"movie": "Tenet", "city": "Miami", "seats": 40},
            {"movie": "Dune", "city": "San Francisco", "seats": 55},
            {"movie": "Avatar", "city": "Seattle", "seats": 70},
            {"movie": "Avengers: Endgame", "city": "Boston", "seats": 80},
            {"movie": "Spider-Man: No Way Home", "city": "Austin", "seats": 50},
            {"movie": "The Matrix", "city": "Portland", "seats": 45},
            {"movie": "Joker", "city": "Denver", "seats": 40},
            {"movie": "Parasite", "city": "Phoenix", "seats": 35},
            {"movie": "1917", "city": "Philadelphia", "seats": 50},
            {"movie": "Oppenheimer", "city": "San Diego", "seats": 60},
            {"movie": "Barbie", "city": "Dallas", "seats": 65},
            {"movie": "The Batman", "city": "Atlanta", "seats": 55}
        ]

        loaded_count = 0
        for movie_data in sample_movies:
            if self.add_movie(**movie_data):
                loaded_count += 1

        print(f"[MONGODB] ✅ Loaded {loaded_count} sample movies")
        return loaded_count

    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        print("[MONGODB] ❌ Connection closed")


# ==================== HELPER FUNCTIONS ====================

def create_mongodb_storage() -> MongoDBStorage:
    """Create and return MongoDB storage instance"""
    return MongoDBStorage()


if __name__ == "__main__":
    # Test the MongoDB connection
    print("Testing MongoDB Storage...")
    storage = create_mongodb_storage()

    # Test user creation
    result = storage.create_user("testuser", "testpass")
    print(f"Create user: {result}")

    # Test user verification
    verified = storage.verify_user("testuser", "testpass")
    print(f"Verify user: {verified}")

    # Test movie addition
    success = storage.add_movie("Test Movie", "Test City", 100)
    print(f"Add movie: {success}")

    # Test get movies
    movies = storage.get_all_movies()
    print(f"Movies: {len(movies)}")

    storage.close()
    print("Test complete!")
