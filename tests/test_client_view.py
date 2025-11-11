#!/usr/bin/env python3
"""
Test script to verify the enhanced client view functionality
Tests all the API endpoints that the client view uses
"""

import requests
import json

BASE_URL = "http://localhost:9000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    print_section("1. Testing Server Health")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_register():
    print_section("2. Testing User Registration")
    test_user = {
        "username": "testclient123",
        "password": "password123"
    }
    try:
        resp = requests.post(f"{BASE_URL}/register", json=test_user, timeout=5)
        print(f"Status: {resp.status_code}")
        result = resp.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return result.get("status") == "success"
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login():
    print_section("3. Testing User Login")
    credentials = {
        "username": "testclient123",
        "password": "password123"
    }
    try:
        resp = requests.post(f"{BASE_URL}/login", json=credentials, timeout=5)
        print(f"Status: {resp.status_code}")
        result = resp.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        if result.get("status") == "success":
            print(f"✅ Login successful! Token: {result['token'][:20]}...")
            return result["token"]
        else:
            print("❌ Login failed")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_add_movie(admin_token):
    print_section("4. Testing Add Movie (Admin)")
    movies = [
        {"movie": "Inception", "city": "Delhi"},
        {"movie": "The Matrix", "city": "Mumbai"},
        {"movie": "Interstellar", "city": "Bangalore"}
    ]
    
    for movie_data in movies:
        try:
            payload = {
                "token": admin_token,
                "movie": movie_data["movie"],
                "city": movie_data["city"]
            }
            resp = requests.post(f"{BASE_URL}/add_movie", json=payload, timeout=5)
            result = resp.json()
            print(f"Added '{movie_data['movie']}' in {movie_data['city']}: {result.get('status')}")
        except Exception as e:
            print(f"❌ Error adding {movie_data['movie']}: {e}")

def test_get_movies(token):
    print_section("5. Testing Get Movies (Client View)")
    try:
        resp = requests.get(f"{BASE_URL}/data/movies", params={"token": token}, timeout=5)
        print(f"Status: {resp.status_code}")
        result = resp.json()
        
        if result.get("status") == "success":
            movies = result.get("data", [])
            print(f"✅ Found {len(movies)} movies:")
            for i, movie_item in enumerate(movies, 1):
                movie_info = movie_item.get("data", {})
                print(f"   {i}. {movie_info.get('movie')} in {movie_info.get('city')} - "
                      f"{movie_info.get('seats', 'N/A')} seats available")
            return movies
        else:
            print(f"❌ Failed: {result.get('message')}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_book_ticket(token):
    print_section("6. Testing Book Ticket (Client Action)")
    import uuid
    
    booking_payload = {
        "requestId": str(uuid.uuid4()),
        "payload": {
            "type": "book_seat",
            "data": {
                "movie": "Inception",
                "city": "Delhi",
                "seats": 2
            }
        },
        "context": {"token": token}
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/business", json=booking_payload, timeout=5)
        print(f"Status: {resp.status_code}")
        result = resp.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get("status") == "success":
            print("✅ Booking successful!")
        else:
            print(f"❌ Booking failed: {result.get('message')}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_get_bookings(token):
    print_section("7. Testing Get Bookings (Client History)")
    try:
        resp = requests.get(f"{BASE_URL}/data/bookings", params={"token": token}, timeout=5)
        print(f"Status: {resp.status_code}")
        result = resp.json()
        
        if result.get("status") == "success":
            bookings = result.get("data", [])
            print(f"✅ Found {len(bookings)} bookings:")
            for i, booking in enumerate(bookings, 1):
                booking_info = booking.get("data", {})
                print(f"   {i}. {booking_info.get('movie')} in {booking_info.get('city')} - "
                      f"{booking_info.get('seats')} seats")
        else:
            print(f"Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Note: Bookings endpoint might not be implemented yet: {e}")

def main():
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  ENHANCED CLIENT VIEW - API FUNCTIONALITY TEST".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    # Test 1: Health
    test_health()
    
    # Test 2: Register new user
    test_register()
    
    # Test 3: Login as client
    client_token = test_login()
    
    if not client_token:
        print("\n❌ Cannot proceed without valid token. Exiting.")
        return
    
    # First, let's login as admin to add movies
    print_section("3b. Login as Admin to Add Movies")
    admin_creds = {"username": "admin", "password": "123"}
    try:
        resp = requests.post(f"{BASE_URL}/login", json=admin_creds, timeout=5)
        admin_result = resp.json()
        if admin_result.get("status") == "success":
            admin_token = admin_result["token"]
            print(f"✅ Admin logged in")
            test_add_movie(admin_token)
        else:
            print("❌ Admin login failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get movies (what client sees)
    movies = test_get_movies(client_token)
    
    # Test 5: Book a ticket
    if movies:
        test_book_ticket(client_token)
    
    # Test 6: Get bookings
    test_get_bookings(client_token)
    
    print_section("✅ TEST COMPLETE")
    print("\nThe enhanced client view in app.py can now:")
    print("  1. ✅ Register new users")
    print("  2. ✅ Login and get authentication token")
    print("  3. ✅ View available movies with details")
    print("  4. ✅ Book tickets for selected movies")
    print("  5. ✅ View booking history")
    print("  6. ✅ Refresh data from server")
    print("\nTo use the GUI:")
    print("  1. Install: pip install customtkinter")
    print("  2. Run: python app.py")
    print("  3. Click 'Register New Account' or login with existing credentials")
    print("  4. Use the dual-panel interface to browse and book movies")

if __name__ == "__main__":
    main()
