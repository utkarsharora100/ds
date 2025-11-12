import customtkinter as ctk
from tkinter import messagebox, ttk
import subprocess
import threading
import os, sys
import random
import uuid
from client.client import Client  # ✅ USING your client simulation
import requests

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Distributed Movie Booking System")
        self.geometry("900x600")

        # track external subprocesses for nodes
        self.node_processes = {"node1": None, "node2": None, "node3": None}

        # default user store
        self.users = {"admin": "123"}

        # In-memory movie list
        self.movies = []

        self.load_login()

    # ----------------------------------------------------------------------------
    # REGISTRATION PAGE
    # ----------------------------------------------------------------------------
    def load_register(self):
        self.clear()

        frame = ctk.CTkFrame(self, corner_radius=20, width=450, height=400)
        frame.pack(expand=True)

        ctk.CTkLabel(frame, text="Register New Account", font=("Arial", 30)).pack(pady=20)

        username = ctk.CTkEntry(frame, placeholder_text="Choose Username", width=280)
        username.pack(pady=10)
        password = ctk.CTkEntry(frame, placeholder_text="Choose Password", width=280, show="*")
        password.pack(pady=10)
        confirm_password = ctk.CTkEntry(frame, placeholder_text="Confirm Password", width=280, show="*")
        confirm_password.pack(pady=10)

        def register():
            user = username.get()
            pwd = password.get()
            cpwd = confirm_password.get()

            if not user or not pwd:
                messagebox.showerror("Error", "Username and password cannot be empty")
                return
            
            if pwd != cpwd:
                messagebox.showerror("Error", "Passwords do not match")
                return
            
            if user in self.users:
                messagebox.showerror("Error", "Username already exists")
                return
            
            # Register via API
            try:
                resp = requests.post(
                    "http://127.0.0.1:9000/register",
                    json={"username": user, "password": pwd},
                    timeout=5
                ).json()
                
                if resp.get("status") == "success":
                    self.users[user] = pwd
                    messagebox.showinfo("Success", "Registration successful! Please login.")
                    self.load_login()
                else:
                    messagebox.showerror("Error", resp.get("message", "Registration failed"))
            except Exception as e:
                messagebox.showerror("Error", f"Could not connect to server: {e}")

        ctk.CTkButton(frame, text="Register", width=220, command=register).pack(pady=10)
        ctk.CTkButton(frame, text="Back to Login", width=220, command=self.load_login).pack(pady=5)

    # ----------------------------------------------------------------------------
    # LOGIN PAGE
    # ----------------------------------------------------------------------------
    def load_login(self):
        self.clear()

        frame = ctk.CTkFrame(self, corner_radius=20, width=450, height=500)
        frame.pack(expand=True)

        ctk.CTkLabel(frame, text="User Login", font=("Arial", 30)).pack(pady=20)

        username = ctk.CTkEntry(frame, placeholder_text="Enter Username", width=280)
        username.pack(pady=10)
        password = ctk.CTkEntry(frame, placeholder_text="Enter Password", width=280, show="*")
        password.pack(pady=10)

        ctk.CTkButton(frame, text="Login", width=220,
                      command=lambda: self.login(username.get(), password.get())).pack(pady=10)
        
        ctk.CTkButton(frame, text="Register New Account", width=220,
                      command=self.load_register).pack(pady=5)

        # ---------------- NODE CONTROLS ----------------
        node_frame = ctk.CTkFrame(frame, corner_radius=15)
        node_frame.pack(pady=30)

        ctk.CTkLabel(node_frame, text="Start Raft Server Nodes", font=("Arial", 18)).grid(row=0, column=0, columnspan=3)

        self.node1_indicator = ctk.CTkLabel(node_frame, text="🔴", font=("Arial", 20))
        self.node2_indicator = ctk.CTkLabel(node_frame, text="🔴", font=("Arial", 20))
        self.node3_indicator = ctk.CTkLabel(node_frame, text="🔴", font=("Arial", 20))

        ctk.CTkButton(node_frame, text="Start Node 1", width=150,
                      command=lambda: self.start_node("node1", self.node1_indicator)).grid(row=1, column=0, pady=5)
        self.node1_indicator.grid(row=1, column=1)

        ctk.CTkButton(node_frame, text="Start Node 2", width=150,
                      command=lambda: self.start_node("node2", self.node2_indicator)).grid(row=2, column=0, pady=5)
        self.node2_indicator.grid(row=2, column=1)

        ctk.CTkButton(node_frame, text="Start Node 3", width=150,
                      command=lambda: self.start_node("node3", self.node3_indicator)).grid(row=3, column=0, pady=5)
        self.node3_indicator.grid(row=3, column=1)

    # ----------------------------------------------------------------------------
    # NODE STARTER
    # ----------------------------------------------------------------------------
    def start_node(self, node_name, indicator):

        def launch():
            script_path = os.path.join(PROJECT_ROOT, "main.py")
            self.node_processes[node_name] = subprocess.Popen(
                [sys.executable, script_path, node_name],
                cwd=PROJECT_ROOT,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
            )
            self.after(100, lambda: indicator.configure(text="🟢"))

        threading.Thread(target=launch).start()

    # ----------------------------------------------------------------------------
    # LOGIN LOGIC
    # ----------------------------------------------------------------------------
    def login(self, username, password):
        if username in self.users and self.users[username] == password:
            if username == "admin":
                self.load_admin_dashboard()
            else:
                self.load_user_dashboard(username)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    # ----------------------------------------------------------------------------
    # ADMIN DASHBOARD
    # ----------------------------------------------------------------------------
    def load_admin_dashboard(self):
        self.clear()

        ctk.CTkLabel(self, text="ADMIN DASHBOARD", font=("Arial", 30)).pack(pady=10)

        # ---------------- ADD MOVIE SECTION ----------------
        add_frame = ctk.CTkFrame(self)
        add_frame.pack(pady=10)

        movie_entry = ctk.CTkEntry(add_frame, placeholder_text="Movie Name", width=200)
        movie_entry.grid(row=0, column=0, padx=5)
        
        city_entry = ctk.CTkEntry(add_frame, placeholder_text="City", width=150)
        city_entry.grid(row=0, column=1, padx=5)
        
        seats_entry = ctk.CTkEntry(add_frame, placeholder_text="Seats", width=100)
        seats_entry.insert(0, "50")  # Default value
        seats_entry.grid(row=0, column=2, padx=5)

        add_btn = ctk.CTkButton(add_frame, text="Add Movie",
                                command=lambda: self.add_movie(movie_entry.get(), city_entry.get(), seats_entry.get()))
        add_btn.grid(row=0, column=3, padx=5)
        
        # Add "Load Sample Data" button
        sample_btn = ctk.CTkButton(add_frame, text="Load Sample Movies",
                                    command=self.load_sample_movies,
                                    fg_color="green", hover_color="darkgreen")
        sample_btn.grid(row=0, column=4, padx=5)
        
        # Add "Clear Database" button
        clear_btn = ctk.CTkButton(add_frame, text="Clear Database",
                                  command=self.clear_database,
                                  fg_color="red", hover_color="darkred")
        clear_btn.grid(row=0, column=5, padx=5)

        # ---------------- MOVIE TABLE ----------------
        self.movie_table = ttk.Treeview(self, columns=("movie", "city", "seats"), show="headings", height=6)
        self.movie_table.heading("movie", text="Movie")
        self.movie_table.heading("city", text="City")
        self.movie_table.heading("seats", text="Available Seats")
        self.movie_table.pack(pady=10)
        
        # Refresh movies on load
        self.refresh_movies_admin()

        # ---------------- SIMULATE CLIENT BOOKINGS ----------------
        ctk.CTkButton(self, text="Simulate Multiple Clients (5 users booking)",
                      command=self.simulate_clients).pack(pady=10)

        # ---------------- TEST DATABASE CONSISTENCY ----------------
        ctk.CTkButton(
            self,
            text="Test Database Consistency (Raft Verification)",
            command=self.test_database_consistency
        ).pack(pady=10)

        ctk.CTkButton(self, text="Logout", command=self.load_login).pack(pady=20)

    def add_movie(self, movie_name, city, seats):
        if movie_name.strip() == "" or city.strip() == "":
            return
        
        try:
            seats_count = int(seats)
        except ValueError:
            seats_count = 50  # Default if invalid
        
        # Send to server
        resp = requests.post(
            "http://127.0.0.1:9000/add_movie",
            json={
                "token": self.client.token,
                "movie": movie_name,
                "city": city,
                "seats": seats_count
            },
            timeout=5
        ).json()
        
        if resp.get("status") == "success":
            print(f"[CLIENT] Movie added: {movie_name} ({city}) - {seats_count} seats")
            self.refresh_movies_admin()
        else:
            print(f"[CLIENT] Failed to add movie: {resp.get('message')}")
    
    def load_sample_movies(self):
        """Load sample movies using the new admin endpoint"""
        try:
            resp = requests.post(
                "http://127.0.0.1:9000/admin/load_sample_data",
                json={"token": self.client.token},
                timeout=5
            ).json()
            
            if resp.get("status") == "success":
                loaded = resp.get("loaded", {})
                messagebox.showinfo(
                    "Sample Data Loaded",
                    f"Successfully loaded {loaded.get('movies', 0)} sample movies!"
                )
                self.refresh_movies_admin()
            else:
                messagebox.showerror("Error", resp.get("message", "Failed to load sample data"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sample data: {str(e)}")
    
    def clear_database(self):
        """Clear all movies and bookings from database"""
        # Confirm action
        if not messagebox.askyesno(
            "Confirm Clear Database",
            "⚠️ This will DELETE all movies and bookings!\n\nAre you sure you want to continue?"
        ):
            return
        
        try:
            resp = requests.post(
                "http://127.0.0.1:9000/admin/clear_database",
                json={"token": self.client.token},
                timeout=5
            ).json()
            
            if resp.get("status") == "success":
                cleared = resp.get("cleared", {})
                messagebox.showinfo(
                    "Database Cleared",
                    f"Cleared {cleared.get('movies', 0)} movies and {cleared.get('bookings', 0)} bookings"
                )
                self.refresh_movies_admin()
            else:
                messagebox.showerror("Error", resp.get("message", "Failed to clear database"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear database: {str(e)}")
    
    def refresh_movies_admin(self):
        """Fetch and display movies from the server for admin view"""
        for item in self.movie_table.get_children():
            self.movie_table.delete(item)
        
        try:
            resp = requests.get(
                "http://127.0.0.1:9000/data/movies",
                params={"token": self.client.token},
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
        except Exception as e:
            print(f"[CLIENT] Error refreshing movies: {e}")

    # ----------------------------------------------------------------------------
    # CLIENT SIMULATION
    # ----------------------------------------------------------------------------
    def simulate_clients(self):
        def simulate():
            for i in range(5):
                client = Client()
                login = client.login(f"user{i}", "pass")
                # This assumes client.login sets client.token internally
                token = getattr(client, "token", None)
                if token:
                    client.book_seat("Random Movie", "Delhi", 1)

            messagebox.showinfo("Simulation Complete", "Multiple bookings submitted.")

        threading.Thread(target=simulate).start()

    # ----------------------------------------------------------------------------
    # TEST DATABASE CONSISTENCY (RAFT)
    # ----------------------------------------------------------------------------
    def test_database_consistency(self):
        """
        Simulates a DB change and checks if Raft replicated it.
        """
        def run_test():
            test_movie = f"RaftTestMovie-{random.randint(1000,9999)}"
            self.movies.append(test_movie)
            self.movie_table.insert("", "end", values=(test_movie,))
            print(f"[TEST] Added test movie locally: {test_movie}")

            raft_nodes = {"node1": 50051, "node2": 50052, "node3": 50053}
            leader_found = False

            for node, port in raft_nodes.items():
                try:
                    resp = requests.get(f"http://0.0.0.0:{port}/status", timeout=2).json()
                    print(f"[TEST] Node {node} status: {resp}")
                    if resp.get("state") == "leader":
                        leader_found = True
                except Exception as e:
                    print(f"[TEST] Node {node} unreachable: {e}")

            if leader_found:
                messagebox.showinfo("Raft Test", "✅ Raft Verified: Leader detected and DB change simulated.")
            else:
                messagebox.showwarning("Raft Test", "❌ Raft Verification Failed: No leader detected.")

        threading.Thread(target=run_test).start()

    # ----------------------------------------------------------------------------
    # USER DASHBOARD
    # ----------------------------------------------------------------------------
    def load_user_dashboard(self, username):
        self.clear()

        # Header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(header, text=f"Welcome, {username}!", font=("Arial", 28)).pack(side="left", padx=10)
        ctk.CTkButton(header, text="Logout", command=self.load_login, width=100).pack(side="right", padx=10)

        # Create Client instance
        self.client = Client()
        
        # Login via API to get token
        try:
            resp = requests.post(
                "http://127.0.0.1:9000/login",
                json={"username": username, "password": self.users.get(username, "")},
                timeout=5
            ).json()
            
            if resp.get("status") == "success":
                self.client.token = resp["token"]
                self.client.username = username
        except Exception as e:
            print(f"Failed to authenticate: {e}")

        # Main content area
        content = ctk.CTkFrame(self)
        content.pack(fill="both", expand=True, padx=20, pady=10)

        # Left panel - Available Movies
        left_panel = ctk.CTkFrame(content)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(left_panel, text="Available Movies", font=("Arial", 20, "bold")).pack(pady=10)

        # Movies table
        self.movies_table = ttk.Treeview(
            left_panel, 
            columns=("movie", "city", "seats"), 
            show="headings", 
            height=15
        )
        self.movies_table.heading("movie", text="Movie")
        self.movies_table.heading("city", text="City")
        self.movies_table.heading("seats", text="Available Seats")
        
        self.movies_table.column("movie", width=200)
        self.movies_table.column("city", width=100)
        self.movies_table.column("seats", width=100)
        
        self.movies_table.pack(fill="both", expand=True, pady=10, padx=10)

        # Booking controls
        booking_frame = ctk.CTkFrame(left_panel)
        booking_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(booking_frame, text="Seats to Book:").pack(side="left", padx=5)
        
        self.seats_entry = ctk.CTkEntry(booking_frame, width=60, placeholder_text="1")
        self.seats_entry.pack(side="left", padx=5)
        self.seats_entry.insert(0, "1")

        ctk.CTkButton(
            booking_frame, 
            text="Book Selected Movie", 
            command=lambda: self.book_movie_client(username),
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            booking_frame, 
            text="Refresh Movies", 
            command=lambda: self.refresh_movies_client(),
            width=120
        ).pack(side="left", padx=5)

        # Right panel - My Bookings
        right_panel = ctk.CTkFrame(content)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(right_panel, text="My Bookings", font=("Arial", 20, "bold")).pack(pady=10)

        # Bookings table
        self.bookings_table = ttk.Treeview(
            right_panel,
            columns=("booking_id", "movie", "city", "seats"),
            show="headings",
            height=15
        )
        self.bookings_table.heading("booking_id", text="Booking ID")
        self.bookings_table.heading("movie", text="Movie")
        self.bookings_table.heading("city", text="City")
        self.bookings_table.heading("seats", text="Seats")
        
        self.bookings_table.column("booking_id", width=100)
        self.bookings_table.column("movie", width=150)
        self.bookings_table.column("city", width=80)
        self.bookings_table.column("seats", width=60)
        
        self.bookings_table.pack(fill="both", expand=True, pady=10, padx=10)

        ctk.CTkButton(
            right_panel,
            text="Refresh Bookings",
            command=lambda: self.refresh_bookings_client(),
            width=150
        ).pack(pady=10)

        # Load initial data
        self.refresh_movies_client()
        self.refresh_bookings_client()

    def refresh_movies_client(self):
        """Fetch and display movies from the server"""
        # Clear table
        for item in self.movies_table.get_children():
            self.movies_table.delete(item)

        try:
            resp = requests.get(
                "http://127.0.0.1:9000/data/movies",
                params={"token": self.client.token},
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
            else:
                messagebox.showerror("Error", resp.get("message", "Failed to fetch movies"))
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch movies: {e}")

    def refresh_bookings_client(self):
        """Fetch and display user bookings"""
        # Clear table
        for item in self.bookings_table.get_children():
            self.bookings_table.delete(item)

        try:
            resp = requests.get(
                "http://127.0.0.1:9000/data/bookings",
                params={"token": self.client.token},
                timeout=5
            ).json()

            if resp.get("status") == "success":
                bookings_data = resp.get("data", [])
                for booking in bookings_data:
                    booking_info = booking.get("data", {})
                    self.bookings_table.insert(
                        "", "end",
                        values=(
                            booking.get("requestId", "N/A")[:8],
                            booking_info.get("movie", "N/A"),
                            booking_info.get("city", "N/A"),
                            booking_info.get("seats", "N/A")
                        )
                    )
        except Exception as e:
            # Bookings endpoint might not exist, fail silently
            print(f"Could not fetch bookings: {e}")

    def book_movie_client(self, username):
        """Book selected movie for the client"""
        selection = self.movies_table.selection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select a movie to book")
            return

        item = self.movies_table.item(selection[0])
        movie = item["values"][0]
        city = item["values"][1]
        
        try:
            seats = int(self.seats_entry.get())
            if seats <= 0:
                raise ValueError()
        except:
            messagebox.showerror("Error", "Please enter a valid number of seats")
            return

        # Book via API
        try:
            payload = {
                "requestId": str(uuid.uuid4()),
                "payload": {
                    "type": "book_seat",
                    "data": {"movie": movie, "city": city, "seats": seats}
                },
                "context": {"token": self.client.token}
            }
            
            resp = requests.post(
                "http://127.0.0.1:9000/business",
                json=payload,
                timeout=5
            ).json()

            if resp.get("status") == "success":
                messagebox.showinfo(
                    "Success", 
                    f"Successfully booked {seats} seat(s) for '{movie}' in {city}!"
                )
                # Refresh data
                self.refresh_movies_client()
                self.refresh_bookings_client()
            else:
                messagebox.showerror("Booking Failed", resp.get("message", "Unknown error"))
        except Exception as e:
            messagebox.showerror("Error", f"Could not complete booking: {e}")

    # ----------------------------------------------------------------------------
    # HELPER
    # ----------------------------------------------------------------------------
    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
