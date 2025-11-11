# Distributed Movie Booking System

A distributed movie ticket booking system implemented with **Raft consensus algorithm**, **FastAPI application server**, **local LLM support**, and a **GUI client** built with CustomTkinter.

## 🎯 Overview

This project demonstrates a distributed system for movie ticket booking with the following key features:

- **Raft Consensus Protocol**: Ensures data consistency across multiple nodes with leader election and log replication
- **Application Server**: FastAPI-based server handling user authentication, movie management, and booking operations
- **Local LLM Server**: Transformer-based FAQ assistant for movie booking queries
- **Client Application**: Desktop GUI built with CustomTkinter for easy interaction
- **In-Memory Database**: SQLite-based storage for users, sessions, movies, showtimes, and seat bookings

## 📁 Project Structure

```
ds/
├── app.py                          # Main GUI application (CustomTkinter)
├── main.py                         # Raft node launcher
├── Application_server/
│   ├── __init__.py
│   └── Application_server.py      # FastAPI application server
├── client/
│   ├── __init__.py
│   └── client.py                  # Client simulation module
├── llm/
│   ├── __init__.py
│   ├── llm_server.py              # Local LLM FAQ server
│   └── storage.py                 # SQLite database functions
├── proto/
│   ├── __init__.py
│   ├── raft.proto                 # Protocol buffer definitions
│   ├── raft_pb2.py               # Generated protobuf code
│   └── raft_pb2_grpc.py          # Generated gRPC code
├── raft/
│   ├── __init__.py
│   ├── raft_config.json          # Raft configuration
│   ├── raft_node.py              # Raft node implementation
│   └── raft_state.py             # Raft state management
└── tests/
    ├── test_booking.py           # Booking system tests
    └── test_raft.py              # Raft protocol tests
```

## 🛠️ Prerequisites

- **Python**: 3.8 or higher
- **pip**: Python package manager
- **Operating System**: Linux, macOS, or Windows

## 📦 Installation

### Step 1: Clone or Navigate to the Project Directory

```bash
cd /home/aniket/study/ds
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Required Dependencies

```bash
pip install fastapi uvicorn requests customtkinter grpcio grpcio-tools transformers torch
```

**Dependency Breakdown:**
- `fastapi` - Web framework for Application and LLM servers
- `uvicorn` - ASGI server for FastAPI
- `requests` - HTTP client for communication
- `customtkinter` - Modern GUI framework
- `grpcio`, `grpcio-tools` - gRPC for Raft communication
- `transformers`, `torch` - Hugging Face transformers for LLM

### Step 4: Generate Protocol Buffer Code (if needed)

If you modify `raft.proto`, regenerate the Python code:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/raft.proto
```

## 🚀 Running the System

### Architecture Overview

The system consists of:
1. **3 Raft Nodes** (ports 50051, 50052, 50053) - Consensus layer
2. **Application Server** (port 9000) - Business logic
3. **LLM Server** (port 8500) - FAQ assistant (optional)
4. **GUI Client** (app.py) - User interface

### 🐳 Quick Start with Docker (Recommended)

The easiest way to run the entire system:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

**What this does:**
- ✅ Builds and starts Application Server (port 9000)
- ✅ Starts 3 Raft nodes (ports 50051-50053)
- ✅ Starts LLM server (port 8500)
- ✅ Automatic leader election
- ✅ Network isolation and health checks

**Test it works:**
```bash
curl http://localhost:9000/health
curl http://localhost:50051/status
```

📖 **For detailed Docker instructions, see [DOCKER.md](DOCKER.md)**

---

## 📋 Step-by-Step Execution Guide

### **Option A: Using the GUI (Recommended for Beginners)**

#### Step 1: Start the Application Server

Open a **new terminal** and run:

```bash
cd /home/aniket/study/ds
python Application_server/Application_server.py
```

**Expected Output:**
```
[SERVER] ✅ Application Server initialized.
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:9000
```

**Keep this terminal running.**

---

#### Step 2: Launch the GUI Application

Open **another terminal** and run:

```bash
cd /home/aniket/study/ds
python app.py
```

**Expected Result:**
- A dark-themed GUI window will open titled **"Distributed Movie Booking System"**
- You'll see the login page with options to start Raft nodes

---

#### Step 3: Start Raft Nodes from GUI

On the login screen, you'll see three buttons:
1. Click **"Start Node 1"** → Indicator turns 🟢 (green)
2. Click **"Start Node 2"** → Indicator turns 🟢
3. Click **"Start Node 3"** → Indicator turns 🟢

**What happens:**
- Each click spawns a new terminal running a Raft node
- Nodes will elect a leader automatically within 5-8 seconds
- Check the node terminal windows to see leader election logs

---

#### Step 4: Login to the System

**Default Credentials:**
- **Username:** `admin`
- **Password:** `123`

Click **"Login"** button.

---

#### Step 5: Admin Dashboard Features

After login, you can:

1. **Add Movies:**
   - Enter movie name in the text field
   - Click "Add Movie"

2. **Simulate Multiple Clients:**
   - Click "Simulate Multiple Clients (5 users booking)"
   - This spawns 5 concurrent booking requests

3. **Test Database Consistency:**
   - Click "Test Database Consistency (Raft Verification)"
   - Checks if Raft leader is elected and system is healthy

---

### **Option B: Manual Command-Line Execution**

#### Step 1: Start Application Server

```bash
cd /home/aniket/study/ds
python Application_server/Application_server.py
```

---

#### Step 2: Start Raft Nodes (3 separate terminals)

**Terminal 1 - Node 1:**
```bash
cd /home/aniket/study/ds
python main.py node1
```

**Terminal 2 - Node 2:**
```bash
cd /home/aniket/study/ds
python main.py node2
```

**Terminal 3 - Node 3:**
```bash
cd /home/aniket/study/ds
python main.py node3
```

**Expected Output (from one of the nodes):**
```
[node2] 🏆 is the LEADER now (term 1)
INFO:     Uvicorn running on http://0.0.0.0:50052
```

---

#### Step 3: (Optional) Start LLM Server

```bash
cd /home/aniket/study/ds
python -m uvicorn llm.llm_server:app --host 0.0.0.0 --port 8500
```

**Note:** First run will download the model (~500MB). This may take a few minutes.

**Expected Output:**
```
Loading local LLM model... (this may take ~30 seconds the first time)
INFO:     Uvicorn running on http://0.0.0.0:8500
```

---

#### Step 4: Run Client Simulation

```bash
cd /home/aniket/study/ds
python client/client.py
```

**Expected Output:**
```
[CLIENT-user_1234] ✅ Logged in. Token = abc123...
[CLIENT-user_1234] Booking result → {'status': 'success', 'booking_id': '...'}
```

---

## 🧪 Testing

### Test Raft Node Status

Check if nodes are running and identify the leader:

```bash
# Check Node 1
curl http://0.0.0.0:50051/status

# Check Node 2
curl http://0.0.0.0:50052/status

# Check Node 3
curl http://0.0.0.0:50053/status
```

**Example Response:**
```json
{
  "node_id": "node2",
  "state": "leader",
  "term": 1,
  "leader_id": "node2",
  "peers": ["node1", "node3"]
}
```

---

### Test Application Server Endpoints

**Register a User:**
```bash
curl -X POST http://127.0.0.1:9000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "pass123"}'
```

**Login:**
```bash
curl -X POST http://127.0.0.1:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "pass123"}'
```

**Response:**
```json
{
  "status": "success",
  "token": "a1b2c3d4...",
  "user": "testuser"
}
```

**Add a Movie (Admin):**
```bash
curl -X POST http://127.0.0.1:9000/add_movie \
  -H "Content-Type: application/json" \
  -d '{"token": "<your_token>", "movie": "Inception", "city": "Mumbai"}'
```

---

### Test LLM Server (if running)

**Ask a Question:**
```bash
curl -X POST http://0.0.0.0:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I cancel my booking?"}'
```

**Response:**
```json
{
  "answer": "Cancellations are allowed up to one hour before the showtime",
  "confidence": 0.89
}
```

---

## 🔧 Configuration

### Raft Node Ports

Defined in `main.py`:
- **Node 1**: `localhost:50051`
- **Node 2**: `localhost:50052`
- **Node 3**: `localhost:50053`

### Application Server

- **Host**: `127.0.0.1`
- **Port**: `9000`

### LLM Server

- **Host**: `0.0.0.0`
- **Port**: `8500`

### Default Users

Defined in `Application_server/Application_server.py`:
- **Username**: `admin`, **Password**: `123`
- **Username**: `utkarsh`, **Password**: `password123`

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure you're in the project root
cd /home/aniket/study/ds

# Install missing packages
pip install <package-name>
```

---

### Issue: Ports already in use

**Solution:**
```bash
# Kill processes using ports
lsof -ti:9000 | xargs kill -9   # Application server
lsof -ti:50051 | xargs kill -9  # Node 1
lsof -ti:50052 | xargs kill -9  # Node 2
lsof -ti:50053 | xargs kill -9  # Node 3
lsof -ti:8500 | xargs kill -9   # LLM server
```

---

### Issue: GUI not opening

**Solution:**
- Make sure you have a display server running (X11 on Linux, not WSL without X server)
- Install tkinter if missing:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-tk
  
  # Fedora
  sudo dnf install python3-tkinter
  ```

---

### Issue: LLM model download fails

**Solution:**
- Check internet connection
- Manually download model:
  ```python
  from transformers import pipeline
  pipeline("question-answering", model="deepset/roberta-base-squad2")
  ```

---

### Issue: Raft nodes not electing leader

**Solution:**
- Ensure all 3 nodes are running
- Check node terminals for error messages
- Restart all nodes simultaneously
- Election should occur within 5-8 seconds

---

## 📊 System Flow

```
┌─────────────┐
│   GUI App   │ (app.py)
└──────┬──────┘
       │
       ├─────→ Starts Raft Nodes (main.py)
       │       ├─ Node 1 (50051)
       │       ├─ Node 2 (50052)
       │       └─ Node 3 (50053)
       │
       └─────→ Communicates with Application Server
               │
               ├─ User Authentication
               ├─ Movie Management
               └─ Booking Operations
                       │
                       └─→ Stores in SQLite (storage.py)
```

---

## 🎓 Key Features Demonstrated

1. **Distributed Consensus**: Raft algorithm implementation with leader election
2. **Fault Tolerance**: System continues operating if minority of nodes fail
3. **RESTful APIs**: FastAPI for modern async HTTP endpoints
4. **gRPC Communication**: Inter-node communication using Protocol Buffers
5. **Client-Server Architecture**: Separation of concerns with modular design
6. **GUI Development**: Modern desktop application with CustomTkinter
7. **Machine Learning Integration**: Local LLM for FAQ assistance
8. **Database Management**: SQLite with user sessions and booking state

---

## 📝 Notes

- **First-time LLM setup** may take time due to model download (~500MB)
- **Raft nodes** should be started before heavy client load
- **Admin operations** require proper authentication token
- **Election timeout** is randomized between 5-8 seconds to avoid split votes
- **In-memory database** resets on application server restart

---

## 🤝 Contributing

Feel free to extend this project with:
- Persistent storage (PostgreSQL/MySQL)
- Payment gateway integration
- Real-time seat availability updates
- Email notifications
- Mobile client application

---

## 📄 License

This is an educational project for distributed systems learning.

---

## 👨‍💻 Author

Aniket & Team
Repository: utkarsharora100/ds

---

## 📚 References

- [Raft Consensus Algorithm](https://raft.github.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [gRPC Python Guide](https://grpc.io/docs/languages/python/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)

---

**Happy Coding! 🚀**
