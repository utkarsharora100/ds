import sqlite3
import random
import datetime
import hashlib
import secrets


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_in_memory_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    c = conn.cursor()

    # ---------------- USERS & SESSION TABLES ----------------
    c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ---------------- EXISTING MOVIE + SEAT SCHEMA ----------------
    c.execute('''
        CREATE TABLE movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            language TEXT,
            format TEXT,
            duration INTEGER
        )
    ''')

    c.execute('''
        CREATE TABLE showtimes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER,
            start_time DATETIME,
            screen TEXT,
            FOREIGN KEY(movie_id) REFERENCES movies(id)
        )
    ''')

    c.execute('''
        CREATE TABLE seats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            showtime_id INTEGER,
            row TEXT,
            seat_number INTEGER,
            price REAL,
            available BOOLEAN,
            FOREIGN KEY(showtime_id) REFERENCES showtimes(id)
        )
    ''')

    # -------- Seed Sample Data (random movie + seats) ----------
    movie_titles = [
        ("Interstellar", "English", "IMAX", 169),
        ("Inception", "English", "2D", 148),
        ("Dangal", "Hindi", "2D", 161),
        ("Avatar", "English", "3D", 181),
        ("Baahubali", "Telugu", "IMAX", 167)
    ]

    for title, lang, fmt, dur in movie_titles:
        c.execute("INSERT INTO movies (title, language, format, duration) VALUES (?, ?, ?, ?)",
                  (title, lang, fmt, dur))
        movie_id = c.lastrowid

        for _ in range(random.randint(1, 3)):
            start_time = datetime.datetime.now() + datetime.timedelta(days=random.randint(0, 3))
            screen = f"Screen-{random.randint(1, 5)}"
            c.execute("INSERT INTO showtimes (movie_id, start_time, screen) VALUES (?, ?, ?)",
                      (movie_id, start_time, screen))
            showtime_id = c.lastrowid

            for row in "ABCDE":
                for seat_no in range(1, 11):
                    price = random.choice([200, 250, 300, 400])
                    c.execute(
                        "INSERT INTO seats (showtime_id, row, seat_number, price, available) VALUES (?, ?, ?, ?, ?)",
                        (showtime_id, row, seat_no, price, True)
                    )

    conn.commit()
    return conn


# ---------------- USER FUNCTIONS ----------------

def create_user(conn, username: str, password: str):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def authenticate_user(conn, username: str, password: str):
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    result = c.fetchone()

    if result and hash_password(password) == result[1]:
        return result[0]  # return user_id
    return None


def create_session(conn, user_id: int):
    token = secrets.token_hex(32)
    expiration = datetime.datetime.now() + datetime.timedelta(hours=4)

    c = conn.cursor()
    c.execute(
        "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
        (token, user_id, expiration)
    )
    conn.commit()
    return token


def get_user_by_token(conn, token: str):
    c = conn.cursor()
    c.execute(
        "SELECT users.id, users.username FROM users JOIN sessions ON users.id = sessions.user_id WHERE token = ?",
        (token,)
    )
    return c.fetchone()


def logout(conn, token: str):
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    return True


# ---------------- MOVIE MANAGEMENT FUNCTIONS ----------------

def add_movie_to_db(conn, movie: str, city: str, seats: int = 50):
    """
    Add a new movie with available seats to the database.
    Returns True on success, False if movie already exists in that city.
    """
    try:
        c = conn.cursor()
        # Check if movie already exists in this city
        c.execute(
            "SELECT id FROM movies WHERE title = ? AND language = ?",
            (movie, city)
        )
        if c.fetchone():
            return False
        
        # Insert new movie (using language field as city for simplicity)
        c.execute(
            "INSERT INTO movies (title, language, format, duration) VALUES (?, ?, ?, ?)",
            (movie, city, "2D", seats)  # storing seats in duration field temporarily
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB ERROR] Failed to add movie: {e}")
        return False


def get_all_movies(conn):
    """
    Retrieve all movies with their available seat counts.
    Returns list of dicts: [{"movie": ..., "city": ..., "seats": ...}, ...]
    """
    c = conn.cursor()
    c.execute("SELECT title, language, duration FROM movies")
    rows = c.fetchall()
    
    movies = []
    for row in rows:
        movies.append({
            "movie": row[0],
            "city": row[1],
            "seats": row[2]  # duration field used as seats
        })
    return movies


def update_movie_seats(conn, movie: str, city: str, seats_to_remove: int):
    """
    Decrement available seats when booking tickets.
    Returns True on success, False if insufficient seats or movie not found.
    """
    try:
        c = conn.cursor()
        # Get current seat count
        c.execute(
            "SELECT id, duration FROM movies WHERE title = ? AND language = ?",
            (movie, city)
        )
        result = c.fetchone()
        
        if not result:
            return False
        
        movie_id, current_seats = result
        
        if current_seats < seats_to_remove:
            return False  # Not enough seats
        
        # Update seat count
        new_seats = current_seats - seats_to_remove
        c.execute(
            "UPDATE movies SET duration = ? WHERE id = ?",
            (new_seats, movie_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB ERROR] Failed to update seats: {e}")
        return False


# ---------------- LOCAL TESTING ----------------
if __name__ == "__main__":
    db = create_in_memory_db()

    print("DB Ready")

    # create user
    create_user(db, "admin", "pass123")

    user = authenticate_user(db, "admin", "pass123")
    print("User:", user)

    token = create_session(db, user)
    print("Token:", token)

    print("Session:", get_user_by_token(db, token))
