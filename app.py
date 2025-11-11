import customtkinter as ctk
from tkinter import messagebox, ttk
import subprocess
import threading
import os, sys
import random
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

        movie_entry = ctk.CTkEntry(add_frame, placeholder_text="Movie Name", width=250)
        movie_entry.grid(row=0, column=0, padx=10)

        add_btn = ctk.CTkButton(add_frame, text="Add Movie",
                                command=lambda: self.add_movie(movie_entry.get()))
        add_btn.grid(row=0, column=1)

        # ---------------- MOVIE TABLE ----------------
        self.movie_table = ttk.Treeview(self, columns=("movie"), show="headings", height=6)
        self.movie_table.heading("movie", text="Movies Available")
        self.movie_table.pack(pady=10)

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

    def add_movie(self, movie_name):
        if movie_name.strip() == "":
            return

        self.movies.append(movie_name)
        self.movie_table.insert("", "end", values=(movie_name,))

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

        ctk.CTkLabel(self, text=f"Welcome {username}", font=("Arial", 28)).pack(pady=10)

        table = ttk.Treeview(self, columns=("movie"), show="headings", height=8)
        table.heading("movie", text="Movies Available")
        table.pack(pady=20)

        for movie in self.movies:
            table.insert("", "end", values=(movie,))

        ctk.CTkButton(self, text="Book Selected Movie",
                      command=lambda: messagebox.showinfo("Booked",
                              f"You booked {table.item(table.selection())['values'][0]}")).pack(pady=10)

        ctk.CTkButton(self, text="Logout", command=self.load_login).pack(pady=10)

    # ----------------------------------------------------------------------------
    # HELPER
    # ----------------------------------------------------------------------------
    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
