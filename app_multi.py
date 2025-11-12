"""
Multi-Window Distributed Movie Booking System
Demonstrates Raft consistency by running 3 clients + 1 admin simultaneously
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import threading
import subprocess
import os
import sys
import time
import requests
import uuid
import multiprocessing

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ----------------------------------------------------------------------------
# ADMIN WINDOW
# ----------------------------------------------------------------------------
class AdminWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("ADMIN - Movie Booking System")
        self.geometry("800x600+50+50")
        
        self.token = None
        self.auto_refresh = True
        
        # Auto-login as admin
        self.login_admin()
        
        # Build UI
        self.build_ui()
        
        # Start auto-refresh thread
        self.start_auto_refresh()
    
    def login_admin(self):
        """Auto-login as admin"""
        try:
            resp = requests.post(
                "http://127.0.0.1:9000/login",
                json={"username": "admin", "password": "123"},
                timeout=5
            ).json()
            
            if resp.get("status") == "success":
                self.token = resp["token"]
                print("[ADMIN] Logged in successfully")
            else:
                print("[ADMIN] Login failed:", resp.get("message"))
        except Exception as e:
            print(f"[ADMIN] Login error: {e}")
    
    def build_ui(self):
        """Build admin dashboard UI"""
        # Header
        ctk.CTkLabel(self, text="🎬 ADMIN DASHBOARD", font=("Arial", 28, "bold")).pack(pady=10)
        
        # Add Movie Section
        add_frame = ctk.CTkFrame(self)
        add_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(add_frame, text="Add New Movie:", font=("Arial", 16)).grid(row=0, column=0, padx=5, sticky="w")
        
        self.movie_entry = ctk.CTkEntry(add_frame, placeholder_text="Movie Name", width=200)
        self.movie_entry.grid(row=1, column=0, padx=5, pady=5)
        
        self.city_entry = ctk.CTkEntry(add_frame, placeholder_text="City", width=150)
        self.city_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.seats_entry = ctk.CTkEntry(add_frame, placeholder_text="Seats", width=100)
        self.seats_entry.insert(0, "100")
        self.seats_entry.grid(row=1, column=2, padx=5, pady=5)
        
        ctk.CTkButton(
            add_frame, text="➕ Add Movie", 
            command=self.add_movie,
            width=150
        ).grid(row=1, column=3, padx=5, pady=5)
        
        # Movies Table
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(table_frame, text="📋 Movies & Seat Availability", font=("Arial", 18)).pack(pady=5)
        
        self.movie_table = ttk.Treeview(
            table_frame, 
            columns=("movie", "city", "seats"), 
            show="headings", 
            height=12
        )
        self.movie_table.heading("movie", text="Movie")
        self.movie_table.heading("city", text="City")
        self.movie_table.heading("seats", text="Available Seats")
        
        self.movie_table.column("movie", width=300)
        self.movie_table.column("city", width=150)
        self.movie_table.column("seats", width=150)
        
        self.movie_table.pack(fill="both", expand=True, pady=5, padx=10)
        
        # All Bookings Table
        bookings_frame = ctk.CTkFrame(self)
        bookings_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(bookings_frame, text="📖 All User Bookings", font=("Arial", 18)).pack(pady=5)
        
        self.bookings_table = ttk.Treeview(
            bookings_frame,
            columns=("user", "movie", "city", "seats"),
            show="headings",
            height=8
        )
        self.bookings_table.heading("user", text="Username")
        self.bookings_table.heading("movie", text="Movie")
        self.bookings_table.heading("city", text="City")
        self.bookings_table.heading("seats", text="Seats")
        
        self.bookings_table.column("user", width=150)
        self.bookings_table.column("movie", width=250)
        self.bookings_table.column("city", width=120)
        self.bookings_table.column("seats", width=100)
        
        self.bookings_table.pack(fill="both", expand=True, pady=5, padx=10)
        
        # Status bar
        self.status_label = ctk.CTkLabel(self, text="🔄 Auto-refresh: ON", font=("Arial", 12))
        self.status_label.pack(pady=5)
        
        # Initial load
        self.refresh_data()
    
        # --- Add simulate concurrent booking button ---
        sim_btn_frame = ctk.CTkFrame(self)
        sim_btn_frame.pack(pady=10)

        # (helper moved to module-level)
        ctk.CTkButton(
            sim_btn_frame,
            text="Simulate Concurrent Booking",
            fg_color="#0078D7",
            hover_color="#005A9E",
            command=self.simulate_concurrent_booking
        ).pack()
    def add_movie(self):
        """Add movie via API"""
        movie = self.movie_entry.get().strip()
        city = self.city_entry.get().strip()
        
        if not movie or not city:
            messagebox.showwarning("Input Error", "Please enter movie name and city")
            return
        
        try:
            seats = int(self.seats_entry.get())
        except:
            seats = 100
        
        try:
            resp = requests.post(
                "http://127.0.0.1:9000/add_movie",
                json={
                    "token": self.token,
                    "movie": movie,
                    "city": city,
                    "seats": seats
                },
                timeout=5
            ).json()
            
            if resp.get("status") == "success":
                print(f"[ADMIN] ✅ Added: {movie} ({city}) - {seats} seats")
                self.movie_entry.delete(0, 'end')
                self.city_entry.delete(0, 'end')
                self.seats_entry.delete(0, 'end')
                self.seats_entry.insert(0, "100")
                self.refresh_data()
            else:
                print(f"[ADMIN] ❌ Failed: {resp.get('message')}")
        except Exception as e:
            print(f"[ADMIN] Error adding movie: {e}")
    
    def refresh_data(self):
        """Refresh movies and bookings from server"""
        # Refresh movies
        for item in self.movie_table.get_children():
            self.movie_table.delete(item)
        
        try:
            resp = requests.get(
                "http://127.0.0.1:9000/data/movies",
                params={"token": self.token},
                timeout=5
            ).json()
            
            if resp.get("status") == "success":
                movies_data = resp.get("data", [])
                for movie_item in movies_data:
                    movie_info = movie_item.get("data", {})
                    self.movie_table.insert(
                        "", "end",
                        values=(
                            movie_info.get("movie", "N/A"),
                            movie_info.get("city", "N/A"),
                            movie_info.get("seats", "N/A")
                        )
                    )
                self.status_label.configure(text=f"🔄 Last refresh: {time.strftime('%H:%M:%S')} | Movies: {len(movies_data)}")
        except Exception as e:
            print(f"[ADMIN] Error refreshing movies: {e}")
        
        # Refresh all bookings
        for item in self.bookings_table.get_children():
            self.bookings_table.delete(item)
        
        try:
            resp = requests.get(
                "http://127.0.0.1:9000/data/bookings",
                params={"token": self.token},
                timeout=5
            ).json()
            
            if resp.get("status") == "success":
                bookings_data = resp.get("data", [])
                for booking in bookings_data:
                    booking_info = booking.get("data", {})
                    # Extract username from context if available
                    username = booking.get("context", {}).get("username", "Unknown")
                    self.bookings_table.insert(
                        "", "end",
                        values=(
                            username,
                            booking_info.get("movie", "N/A"),
                            booking_info.get("city", "N/A"),
                            booking_info.get("seats", "N/A")
                        )
                    )
        except Exception as e:
            print(f"[ADMIN] Error refreshing bookings: {e}")
    
    def start_auto_refresh(self):
        """Start auto-refresh thread"""
        def refresh_loop():
            while self.auto_refresh:
                time.sleep(3)  # Refresh every 3 seconds
                try:
                    self.after(0, self.refresh_data)
                except:
                    break
        
        threading.Thread(target=refresh_loop, daemon=True).start()

    # ------------------ Simulation helpers ------------------
    def _get_invoke_python(self):
        venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'Scripts', 'python.exe')
        if os.path.exists(venv_python):
            return venv_python
        return sys.executable

    def _run_invoke_task_bg(self, task_name):
        """Run invoke <task_name> in background thread."""
        def run():
            py = self._get_invoke_python()
            cmd = [py, '-m', 'invoke', task_name]
            try:
                proc = subprocess.run(cmd, cwd=os.path.dirname(__file__), capture_output=True, text=True)
                print(f"[INVOKE:{task_name}] rc={proc.returncode}\n{proc.stdout}\n{proc.stderr}")
            except Exception as e:
                print(f"Failed to run invoke {task_name}: {e}")

        threading.Thread(target=run, daemon=True).start()

    def simulate_concurrent_booking(self):
        """Simulate many clients concurrently booking the same movie.
        Creates mock users, logs them in, and posts booking requests concurrently using threads.
        """
        # Choose first movie if available
        try:
            resp = requests.get("http://127.0.0.1:9000/data/movies", params={"token": self.token}, timeout=5).json()
            movies = resp.get('data', [])
            if not movies:
                messagebox.showwarning("No Movies", "No movies available to simulate booking.")
                return
            movie = movies[0]['data']['movie']
            city = movies[0]['data']['city']
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch movies: {e}")
            return

        # Number of mock users to create
        N = 8
        users = [(f"sim_user_{i+1}", f"pass{i+1}123") for i in range(N)]

        results = []

        def worker(username, password, out_list):
            # Register (ignore failures)
            try:
                requests.post("http://127.0.0.1:9000/register", json={"username": username, "password": password}, timeout=5)
            except:
                pass

            # Login
            try:
                r = requests.post("http://127.0.0.1:9000/login", json={"username": username, "password": password}, timeout=5).json()
                token = r.get('token')
            except Exception as e:
                out_list.append((username, False, f"login error: {e}"))
                return

            if not token:
                out_list.append((username, False, "no token"))
                return

            # Attempt booking
            payload = {
                "requestId": str(uuid.uuid4()),
                "payload": {"type": "book_seat", "data": {"movie": movie, "city": city, "seats": 1}},
                "context": {"token": token}
            }
            try:
                b = requests.post("http://127.0.0.1:9000/business", json=payload, timeout=8).json()
                if b.get('status') == 'success':
                    out_list.append((username, True, b.get('booking_id') or b.get('booking', 'ok')))
                else:
                    out_list.append((username, False, b.get('message', 'failed')))
            except Exception as e:
                out_list.append((username, False, f"booking error: {e}"))

        threads = []
        for (u, p) in users:
            t = threading.Thread(target=worker, args=(u, p, results))
            t.start()
            threads.append(t)

        # Wait for threads
        for t in threads:
            t.join()

        # Summarize results
        success = [r for r in results if r[1]]
        fail = [r for r in results if not r[1]]
        msg = f"Sim complete — Success: {len(success)}, Fail: {len(fail)}\n"
        msg += "\n".join([f"{r[0]} -> {r[2]}" for r in results])
        messagebox.showinfo("Simulation Results", msg)


# ----------------------------------------------------------------------------
# CLIENT WINDOW (FIXED)
# ----------------------------------------------------------------------------
class ClientWindow(ctk.CTk):
    def __init__(self, username, position_offset=0):
        super().__init__()
        
        self.username = username
        self.token = None
        self.auto_refresh = True
        
        # --- FIX 1: Add instance variable to store selection data ---
        self.selected_movie_data = None 
        
        # Position windows side by side
        x_pos = 900 + (position_offset * 650)
        y_pos = 50
        
        self.title(f"CLIENT: {username}")
        self.geometry(f"630x700+{x_pos}+{y_pos}")
        
        # Auto-register and login
        self.register_and_login()
        
        # Build UI
        self.build_ui()
        
        # Start auto-refresh
        self.start_auto_refresh()
    
    def register_and_login(self):
        """Auto-register and login user"""
        # Try to register (will fail if exists, that's ok)
        try:
            requests.post(
                "http://127.0.0.1:9000/register",
                json={"username": self.username, "password": "pass123"},
                timeout=5
            )
        except:
            pass
        
        # Login
        try:
            resp = requests.post(
                "http://127.0.0.1:9000/login",
                json={"username": self.username, "password": "pass123"},
                timeout=5
            ).json()
            
            if resp.get("status") == "success":
                self.token = resp["token"]
                print(f"[{self.username}] Logged in successfully")
            else:
                print(f"[{self.username}] Login failed:", resp.get("message"))
        except Exception as e:
            print(f"[{self.username}] Login error: {e}")
    
    def build_ui(self):
        """Build client dashboard UI"""
        # Header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            header, 
            text=f"👤 {self.username}", 
            font=("Arial", 24, "bold")
        ).pack(side="left", padx=10)
        
        # Available Movies Section
        movies_frame = ctk.CTkFrame(self)
        movies_frame.pack(pady=5, padx=10, fill="both", expand=True)
        
        ctk.CTkLabel(
            movies_frame, 
            text="🎬 Available Movies", 
            font=("Arial", 18, "bold")
        ).pack(pady=5)
        
        self.movies_table = ttk.Treeview(
            movies_frame,
            columns=("movie", "city", "seats"),
            show="headings",
            height=8
        )
        self.movies_table.heading("movie", text="Movie")
        self.movies_table.heading("city", text="City")
        self.movies_table.heading("seats", text="Seats")
        
        self.movies_table.column("movie", width=250)
        self.movies_table.column("city", width=120)
        self.movies_table.column("seats", width=100)
        
        self.movies_table.pack(fill="both", expand=True, pady=5, padx=10)
        
        # --- FIX 1: Bind the selection event to a helper function ---
        self.movies_table.bind("<<TreeviewSelect>>", self.on_movie_select)

        # Booking controls
        booking_frame = ctk.CTkFrame(movies_frame)
        booking_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(booking_frame, text="Seats:").pack(side="left", padx=5)
        
        self.seats_entry = ctk.CTkEntry(booking_frame, width=60)
        self.seats_entry.insert(0, "5")
        self.seats_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            booking_frame,
            text="🎫 Book Selected",
            command=self.book_movie,
            width=150
        ).pack(side="left", padx=5)
        
        # My Bookings Section
        bookings_frame = ctk.CTkFrame(self)
        bookings_frame.pack(pady=5, padx=10, fill="both", expand=True)
        
        ctk.CTkLabel(
            bookings_frame,
            text="📋 My Bookings",
            font=("Arial", 18, "bold")
        ).pack(pady=5)
        
        self.bookings_table = ttk.Treeview(
            bookings_frame,
            columns=("movie", "city", "seats"),
            show="headings",
            height=8
        )
        self.bookings_table.heading("movie", text="Movie")
        self.bookings_table.heading("city", text="City")
        self.bookings_table.heading("seats", text="Seats Booked")
        
        self.bookings_table.column("movie", width=250)
        self.bookings_table.column("city", width=120)
        self.bookings_table.column("seats", width=100)
        
        self.bookings_table.pack(fill="both", expand=True, pady=5, padx=10)
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, 
            text="🔄 Connected", 
            font=("Arial", 12)
        )
        self.status_label.pack(pady=5)
        
        # Initial load
        self.refresh_data()
    
    def book_movie(self):
        """Book selected movie"""
        
        # --- FIX 1: Read from the stored selection data, not the live table ---
        if not self.selected_movie_data:
            messagebox.showwarning("No Selection", "Please select a movie")
            return
        
        movie, city = self.selected_movie_data
        
        try:
            seats = int(self.seats_entry.get())
        except:
            messagebox.showerror("Error", "Invalid seat count")
            return
        
        try:
            payload = {
                "requestId": str(uuid.uuid4()),
                "payload": {
                    "type": "book_seat",
                    "data": {"movie": movie, "city": city, "seats": seats}
                },
                "context": {"token": self.token}
            }
            
            resp = requests.post(
                "http://127.0.0.1:9000/business",
                json=payload,
                timeout=5
            ).json()
            
            if resp.get("status") == "success":
                print(f"[{self.username}] ✅ Booked {seats} seats for {movie}")
                # --- FIX 2: REMOVED the immediate call to self.refresh_data() ---
                # Let the 2-second auto-refresh loop handle picking up the new booking.
                # This gives the Raft backend time to commit the change.
                # self.refresh_data() 
            else:
                messagebox.showerror("Booking Failed", resp.get("message", "Unknown error"))
                print(f"[{self.username}] ❌ Booking failed: {resp.get('message')}")
        except Exception as e:
            messagebox.showerror("Error", f"Booking error: {e}")
    
    # --- FIX 1: Add the helper function to store selection ---
    # --- FIX 1: (Modified) Only update selection, never clear it on deselect ---
    def on_movie_select(self, event):
        """
        Callback to store selection data when a user clicks a row.
        This prevents the auto-refresh from clearing the selection.
        """
        selection = self.movies_table.selection()
        
        # We ONLY update the data if there is a valid, new selection.
        # We REMOVED the 'else' block that was setting it to None.
        if selection:
            try:
                item = self.movies_table.item(selection[0])
                # Store the data (movie and city) from the selected row
                self.selected_movie_data = (item["values"][0], item["values"][1]) 
            except Exception:
                # This can happen if the refresh deletes the item just as we click
                # Just ignore it and keep the old selection.
                pass

    # --- FIX 2: (Modified) Clear selection *after* successful booking ---
    def book_movie(self):
        """Book selected movie"""
        
        # Read from the stored selection data
        if not self.selected_movie_data:
            messagebox.showwarning("No Selection", "Please select a movie")
            return
        
        movie, city = self.selected_movie_data
        
        try:
            seats = int(self.seats_entry.get())
        except:
            messagebox.showerror("Error", "Invalid seat count")
            return
        
        try:
            payload = {
                "requestId": str(uuid.uuid4()),
                "payload": {
                    "type": "book_seat",
                    "data": {"movie": movie, "city": city, "seats": seats}
                },
                "context": {"token": self.token}
            }
            
            resp = requests.post(
                "http://127.0.0.1:9000/business",
                json=payload,
                timeout=5
            ).json()
            
            if resp.get("status") == "success":
                print(f"[{self.username}] ✅ Booked {seats} seats for {movie}")
                
                # --- THIS IS THE NEW LINE ---
                # Booking was successful, so clear the selection
                # to prevent accidental double-booking.
                self.selected_movie_data = None
                
                # We still let the auto-refresh handle showing the new data
            else:
                messagebox.showerror("Booking Failed", resp.get("message", "Unknown error"))
                print(f"[{self.username}] ❌ Booking failed: {resp.get('message')}")
        except Exception as e:
            messagebox.showerror("Error", f"Booking error: {e}")

    def refresh_data(self):
        """Refresh movies and personal bookings"""
        # Refresh movies
        for item in self.movies_table.get_children():
            self.movies_table.delete(item)
        
        try:
            resp = requests.get(
                "http://127.0.0.1:9000/data/movies",
                params={"token": self.token},
                timeout=5
            ).json()
            
            if resp.get("status") == "success":
                movies_data = resp.get("data", [])
                for movie_item in movies_data:
                    movie_info = movie_item.get("data", {})
                    self.movies_table.insert(
                        "", "end",
                        values=(
                            movie_info.get("movie", "N/A"),
                            movie_info.get("city", "N/A"),
                            movie_info.get("seats", "N/A")
                        )
                    )
        except Exception as e:
            print(f"[{self.username}] Error refreshing movies: {e}")
        
        # Refresh MY bookings only
        for item in self.bookings_table.get_children():
            self.bookings_table.delete(item)
        
        try:
            resp = requests.get(
                "http://127.0.0.1:9000/data/bookings",
                params={"token": self.token},
                timeout=5
            ).json()
            
            if resp.get("status") == "success":
                bookings_data = resp.get("data", [])
                my_bookings = []
                
                # Filter bookings for this user only
                for booking in bookings_data:
                    # Check if booking belongs to this user
                    context = booking.get("context", {})
                    booking_user = context.get("username", "")
                    
                    if booking_user == self.username:
                        booking_info = booking.get("data", {})
                        my_bookings.append(booking_info)
                        self.bookings_table.insert(
                            "", "end",
                            values=(
                                booking_info.get("movie", "N/A"),
                                booking_info.get("city", "N/A"),
                                booking_info.get("seats", "N/A")
                            )
                        )
                
                self.status_label.configure(
                    text=f"🔄 {time.strftime('%H:%M:%S')} | My Bookings: {len(my_bookings)}"
                )
        except Exception as e:
            print(f"[{self.username}] Error refreshing bookings: {e}")
    
    def start_auto_refresh(self):
        """Start auto-refresh thread"""
        def refresh_loop():
            while self.auto_refresh:
                time.sleep(2)  # Refresh every 2 seconds
                try:
                    self.after(0, self.refresh_data)
                except:
                    break
        
        threading.Thread(target=refresh_loop, daemon=True).start()


# ----------------------------------------------------------------------------
# WINDOW LAUNCHERS (for multiprocessing)
# ----------------------------------------------------------------------------
def launch_admin():
    """Launch admin window in separate process"""
    app = AdminWindow()
    app.mainloop()

def launch_client(username, position):
    """Launch client window in separate process"""
    app = ClientWindow(username, position)
    app.mainloop()


def ensure_qwen2_installed():
    """Try to detect qwen2 (or qwen). If not available, attempt to install via pip.

    This is a best-effort helper to reduce the chance that the LLM server fails
    at startup due to a missing qwen tokenizer package. It will try to install
    `qwen2` first, then fall back to `qwen`.
    """
    try:
        import importlib.util
        if importlib.util.find_spec("qwen2") or importlib.util.find_spec("qwen"):
            print("[MAIN] qwen/qwen2 package already present")
            return
    except Exception:
        pass

    py = None
    try:
        # Attempt to reuse the same python executable that runs this script
        py = sys.executable
    except Exception:
        py = None

    if not py:
        print("[MAIN] Could not determine Python executable for pip install")
        return

    for pkg in ("qwen2", "qwen"):
        try:
            print(f"[MAIN] Attempting to install '{pkg}' via pip...")
            subprocess.run([py, "-m", "pip", "install", pkg], check=False)
            # re-check
            try:
                import importlib.util
                if importlib.util.find_spec(pkg):
                    print(f"[MAIN] Successfully installed '{pkg}'")
                    return
            except Exception:
                pass
        except Exception as e:
            print(f"[MAIN] pip install {pkg} failed: {e}")

    print("[MAIN] qwen/qwen2 not detected or could not be installed automatically.")


# ----------------------------------------------------------------------------
# MAIN LAUNCHER
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 80)
    print("🎬 MULTI-WINDOW DISTRIBUTED MOVIE BOOKING SYSTEM")
    print("=" * 80)
    print("\n🚀 Launching windows:")
    print("   1. Admin Dashboard (left)")
    print("   2. Client: alice (right-top)")
    print("   3. Client: bob (right-middle)")
    print("   4. Client: charlie (right-bottom)")
    print("\n📋 Demonstration Flow:")
    print("   → Admin adds movies with seat counts")
    print("   → All 3 clients see movies instantly (Raft sync)")
    print("   → Clients book tickets independently")
    print("   → Seats decrement in real-time across all windows")
    print("   → Each client sees ONLY their own bookings")
    print("   → Admin sees ALL bookings from all users")
    print("\n✅ This showcases Raft consensus and data consistency!")
    print("=" * 80)
    print("\n⏳ Starting windows in 2 seconds...\n")
    
    time.sleep(2)
    # --- Start Docker Compose services (app server, raft nodes, llm) via invoke in background ---
    def _get_invoke_python_main():
        venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'Scripts', 'python.exe')
        if os.path.exists(venv_python):
            return venv_python
        return sys.executable

    def _start_compose_all():
        py = _get_invoke_python_main()
        # Start app server, raft nodes and llm (equivalent to `invoke up`)
        try:
            print('[MAIN] Starting docker compose services via "docker compose up -d" (background)')
            # Use exact command: docker compose up -d
            subprocess.run(["docker", "compose", "up", "-d"], cwd=os.path.dirname(__file__), check=False)
            print('[MAIN] docker compose up -d completed (check docker for container status)')
        except Exception as e:
            print(f'[MAIN] Failed to run docker compose up -d: {e}')

    # Ensure qwen2 (or qwen) is installed if possible, then launch compose
    try:
        ensure_qwen2_installed()
    except Exception as e:
        print(f"[MAIN] ensure_qwen2_installed() raised an error: {e}")

    # Launch compose startup in a daemon thread so UI can continue
    threading.Thread(target=_start_compose_all, daemon=True).start()
    
    # Launch admin in separate process
    admin_process = multiprocessing.Process(target=launch_admin)
    admin_process.start()
    
    time.sleep(1)
    
    # Launch 3 clients in separate processes
    client_processes = []
    
    for i, username in enumerate(["alice", "bob", "charlie"]):
        client_process = multiprocessing.Process(target=launch_client, args=(username, i))
        client_process.start()
        client_processes.append(client_process)
        time.sleep(0.5)
    
    print("\n✅ All windows launched!")
    print("💡 Tip: Try these actions to see Raft consistency:")
    print("   1. Admin: Add a movie (e.g., 'Inception', 'Delhi', 100 seats)")
    print("   2. Watch all 3 clients auto-refresh and show the new movie")
    print("   3. Alice: Book 15 seats")
    print("   4. Bob: Book 20 seats")
    print("   5. Watch seat count drop to 65 in ALL windows")
    print("   6. Check 'My Bookings' - each user sees only their bookings")
    print("   7. Admin: See ALL bookings from alice, bob, and charlie")
    print("\n🛑 Close any window to exit\n")
    
    # Wait for admin process to finish
    admin_process.join()
    
    # Cleanup
    for process in client_processes:
        if process.is_alive():
            process.terminate()
