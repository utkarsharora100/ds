
# 🎬 Distributed Movie Booking System

A distributed movie ticket booking system featuring a **FastAPI** backend, a 3-node **Raft consensus** cluster, and an **AI assistant** powered by **Qwen2.5-0.5B**. The entire stack runs with a single Docker command.

## 📖 Overview

- **Raft Consensus**: 3-node cluster with automatic leader election and status endpoints.
- **FastAPI Backend**: Handles user authentication, movie management, and ticket bookings.
- **AI Assistant**: Qwen2.5-0.5B LLM for FAQ and chat assistance.
- **Docker-First**: Fully containerized with health checks and centralized logs.

## 🧩 Services and Ports

| Service         | Port       | Description                          |
|-----------------|------------|--------------------------------------|
| `app-server`    | `9000`     | FastAPI backend for core operations  |
| `raft-node1`    | `50051`    | Raft consensus node 1                |
| `raft-node2`    | `50052`    | Raft consensus node 2                |
| `raft-node3`    | `50053`    | Raft consensus node 3                |
| `llm-server`    | `8500`     | Qwen2.5-0.5B AI assistant server     |

## 🧰 Prerequisites

- **Docker**: Version 20.10+ installed and running.
- **Docker Compose**: Version 2.0+ (use `docker compose` or fallback to `docker-compose`).
- **System Requirements**: 6GB RAM (for LLM), ~10GB free disk space.
- **Optional**: For Arch Linux, see [INSTALL_DOCKER.md](docs/INSTALL_DOCKER.md).

## 🚀 Quick Start

1. **Start all services**:
   ```bash
   docker compose up -d
   ```
   *Note*: Use `docker-compose up -d` if Compose V1 is installed. First run may take 30–60 seconds due to LLM model download.

2. **Verify health**:
   ```bash
   ./check_health.sh
   ```
   Or check individually:
   ```bash
   curl http://localhost:9000/health
   curl http://localhost:8500/health
   curl http://localhost:50051/status
   ```

3. **Default test users**:
   - `admin` / `123`
   - `utkarsh` / `password123`

## 🧪 Try It Out

### Test Login
```bash
curl -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}'
```

### Test AI Assistant
```bash
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I book a ticket?"}'
```

### View Logs
```bash
docker compose logs -f
```

## 📚 Documentation

- [QUICKSTART.md](docs/QUICKSTART.md): 2-minute setup guide.
- [DOCKER.md](docs/DOCKER.md): Complete Docker deployment instructions.
- [LLM_TESTING.md](docs/LLM_TESTING.md): AI assistant endpoints and examples.
- [ARCHITECTURE.md](docs/ARCHITECTURE.md): System and Docker architecture.
- [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md): Command and port cheat sheet.
- [CLIENT_VIEW.md](docs/CLIENT_VIEW.md): Enhanced client view documentation and testing guide.

## 🩺 Troubleshooting

- **"command not found: docker-compose"**: Use `docker compose` or install Compose V2.
- **Ports in use**: Free ports `9000`, `8500`, `50051-50053` or edit `docker-compose.yml`.
- **LLM slow on first call**: Model loads on first request; subsequent calls are faster.
- **Low memory**: Start without LLM:
  ```bash
  docker compose up -d app-server raft-node1 raft-node2 raft-node3
  ```

## 📁 Project Structure

```
ds/
├── docker-compose.yml          # Service orchestration
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
├── Dockerfile.app             # Application server image
├── Dockerfile.raft            # Raft node image
├── Dockerfile.llm             # LLM server image
├── Application_server/        # FastAPI backend
│   └── Application_server.py
├── raft/                      # Raft consensus implementation
│   ├── raft_node.py
│   └── raft_state.py
├── llm/                       # AI assistant server
│   ├── llm_server.py         # Qwen2.5-0.5B integration
│   └── storage.py            # Database functions
├── client/                    # Client simulator
│   └── client.py
├── proto/                     # gRPC definitions
│   └── raft.proto
├── test_llm.py               # LLM test suite
├── check_health.sh           # Health check script
└── docs/                     # Documentation
    ├── QUICKSTART.md
    ├── DOCKER.md
    ├── LLM_TESTING.md
    └── ARCHITECTURE.md
```

## 🔌 API Endpoints

### Application Server (`:9000`)

| Method | Endpoint         | Description            |
|--------|------------------|------------------------|
| GET    | `/health`        | Health check           |
| POST   | `/register`      | Register new user      |
| POST   | `/login`         | User login             |
| GET    | `/data/{type}`   | Get movies/bookings    |
| POST   | `/business`      | Book tickets           |
| POST   | `/add_movie`     | Add movie (admin only) |

### Raft Nodes (`:50051-50053`)

| Method | Endpoint             | Description                     |
|--------|----------------------|---------------------------------|
| GET    | `/status`            | Node status & leader info       |
| POST   | `/trigger-election`  | Trigger leader election         |

### LLM Server (`:8500`)

| Method | Endpoint   | Description            |
|--------|------------|------------------------|
| GET    | `/health`  | Health & model status  |
| POST   | `/ask`     | Quick FAQ question     |
| POST   | `/chat`    | Conversational AI      |

## ⚙️ Configuration

### Environment Variables (`.env`)

```bash
# Application Server
APP_SERVER_HOST=0.0.0.0
APP_SERVER_PORT=9000

# LLM Configuration
LLM_MODEL=Qwen/Qwen2.5-0.5B
LLM_MAX_NEW_TOKENS=512
LLM_TEMPERATURE=0.7

# Raft Nodes
RAFT_NODE1_PORT=50051
RAFT_NODE2_PORT=50052
RAFT_NODE3_PORT=50053

# Docker Mode
DOCKER_ENV=true
```

### Customize LLM Behavior

Edit `.env`:
```bash
# Use a different model
LLM_MODEL=Qwen/Qwen2.5-1.5B

# Shorter responses
LLM_MAX_NEW_TOKENS=256

# More focused (less creative)
LLM_TEMPERATURE=0.3
```

## 🔍 Monitoring & Logs

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f llm-server

# Last 100 lines
docker compose logs --tail=100
```

### Resource Usage
```bash
# Real-time stats
docker stats

# Service status
docker compose ps
```

### Health Checks
```bash
# Check all services
./check_health.sh

# Manual checks
curl http://localhost:9000/health
curl http://localhost:8500/health
curl http://localhost:50051/status
```

## 🐳 Docker Commands

### Basic Operations
```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart specific service
docker compose restart llm-server

# Rebuild service
docker compose build --no-cache llm-server

# Clean restart
docker compose down -v && docker compose up -d
```

### Without LLM (Lower Resource Usage)
```bash
docker compose up -d app-server raft-node1 raft-node2 raft-node3
```

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────┐
│               Docker Network                         │
│           (movie-booking-net)                        │
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐         ┌──────────────┐         │
│  │  app-server  │         │  llm-server  │         │
│  │  Port: 9000  │         │  Port: 8500  │         │
│  │   FastAPI    │         │  Qwen2.5-0.5B│         │
│  └──────────────┘         └──────────────┘         │
│                                                      │
│  ┌────────┐     ┌────────┐     ┌────────┐         │
│  │ raft-  │◄───►│ raft-  │◄───►│ raft-  │         │
│  │ node1  │     │ node2  │     │ node3  │         │
│  │ :50051 │     │ :50052 │     │ :50053 │         │
│  └────────┘     └────────┘     └────────┘         │
│       Leader Election & Consensus                   │
└─────────────────────────────────────────────────────┘
```

## 🧪 Manual Execution (Without Docker)

### Step 1: Start Application Server
```bash
cd /home/aniket/study/ds
python Application_server/Application_server.py
```
**Expected Output**:
```
[SERVER] ✅ Application Server initialized.
INFO:     Uvicorn running on http://127.0.0.1:9000
```

### Step 2: Start Raft Nodes
Open three separate terminals:

**Terminal 1 - Node 1**:
```bash
cd /home/aniket/study/ds
python main.py node1
```

**Terminal 2 - Node 2**:
```bash
cd /home/aniket/study/ds
python main.py node2
```

**Terminal 3 - Node 3**:
```bash
cd /home/aniket/study/ds
python main.py node3
```

**Expected Output** (from one node):
```
[node2] 🏆 is the LEADER now (term 1)
INFO:     Uvicorn running on http://0.0.0.0:50052
```

### Step 3: Start LLM Server (Optional)
```bash
cd /home/aniket/study/ds
python -m uvicorn llm.llm_server:app --host 0.0.0.0 --port 8500
```
**Note**: First run downloads the model (~500MB), taking ~30 seconds.

**Expected Output**:
```
Loading local LLM model... (this may take ~30 seconds the first time)
INFO:     Uvicorn running on http://0.0.0.0:8500
```

### Step 4: Run Client Simulation
```bash
cd /home/aniket/study/ds
python client/client.py
```
**Expected Output**:
```
[CLIENT-user_1234] ✅ Logged in. Token = abc123...
[CLIENT-user_1234] Booking result → {'status': 'success', 'booking_id': '...'}
```

### Step 5: Launch GUI Application
```bash
cd /home/aniket/study/ds
python app.py
```
**Expected Result**:
- A dark-themed GUI window titled **"Distributed Movie Booking System"** opens.
- Login page displays with options to start Raft nodes.

### Step 6: Start Raft Nodes from GUI
1. Click **"Start Node 1"** → Indicator turns 🟢 (green).
2. Click **"Start Node 2"** → Indicator turns 🟢.
3. Click **"Start Node 3"** → Indicator turns 🟢.

**What happens**:
- Each click spawns a terminal running a Raft node.
- Nodes elect a leader within 5-8 seconds.
- Check node terminals for leader election logs.

### Step 7: Login and Use Admin Dashboard
- **Credentials**: `admin` / `123`
- Click **"Login"**.

**Features**:
1. **Add Movies**: Enter movie name and click "Add Movie".
2. **Simulate Clients**: Click "Simulate Multiple Clients (5 users booking)" to spawn 5 concurrent booking requests.
3. **Test Consistency**: Click "Test Database Consistency (Raft Verification)" to verify Raft leader and system health.

## 🧪 Testing

### Test Raft Node Status
```bash
curl http://localhost:50051/status
curl http://localhost:50052/status
curl http://localhost:50053/status
```
**Example Response**:
```json
{
  "node_id": "node2",
  "state": "leader",
  "term": 1,
  "leader_id": "node2",
  "peers": ["node1", "node3"]
}
```

### Test Application Server
**Register a User**:
```bash
curl -X POST http://localhost:9000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "pass123"}'
```

**Login**:
```bash
curl -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "pass123"}'
```
**Response**:
```json
{
  "status": "success",
  "token": "a1b2c3d4...",
  "user": "testuser"
}
```

**Add a Movie (Admin)**:
```bash
curl -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d '{"token": "<your_token>", "movie": "Inception", "city": "Mumbai"}'
```

### Test LLM Server
```bash
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I cancel my booking?"}'
```
**Response**:
```json
{
  "answer": "Cancellations are allowed up to one hour before the showtime",
  "confidence": 0.89
}
```

### Run Automated Tests
```bash
python test_llm.py
./check_health.sh
```

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker compose logs

# Rebuild images
docker compose build --no-cache

# Clean start
docker compose down -v
docker system prune -a
docker compose up -d
```

### Port Already in Use
```bash
# Find process using port
lsof -i :9000

# Kill process
kill -9 <PID>
```
*Alternatively*: Edit ports in `docker-compose.yml`.

### LLM Server Out of Memory
- **Option 1**: Increase Docker memory to 6GB+.
- **Option 2**: Run without LLM:
  ```bash
  docker compose up -d app-server raft-node1 raft-node2 raft-node3
  ```

### Slow LLM Responses
Normal on CPU (2-5 seconds). To improve:
```bash
# Edit .env
LLM_MAX_NEW_TOKENS=256  # Shorter responses
LLM_TEMPERATURE=0.3     # More focused
```

### Raft Leader Not Elected
```bash
# Restart Raft nodes
docker compose restart raft-node1 raft-node2 raft-node3

# Wait 5-8 seconds
sleep 8

# Check leader
curl http://localhost:50051/status | grep leader
```

### GUI Not Opening
- Ensure a display server (e.g., X11) is running.
- Install `tkinter`:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-tk

  # Fedora
  sudo dnf install python3-tkinter
  ```

### LLM Model Download Fails
- Verify internet connection.
- Manually download model:
  ```python
  from transformers import pipeline
  pipeline("question-answering", model="deepset/roberta-base-squad2")
  ```

### Module Not Found Errors
```bash
# Ensure project root
cd /home/aniket/study/ds

# Install missing packages
pip install <package-name>
```

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

## 🎓 Key Features

1. **Distributed Consensus**: Raft algorithm with leader election.
2. **Fault Tolerance**: System operates if a minority of nodes fail.
3. **RESTful APIs**: FastAPI for async HTTP endpoints.
4. **gRPC Communication**: Inter-node communication via Protocol Buffers.
5. **Client-Server Architecture**: Modular design with separation of concerns.
6. **GUI Development**: Modern desktop app with CustomTkinter.
7. **Machine Learning**: Local LLM for FAQ assistance.
8. **Database Management**: SQLite for user sessions and bookings.

## 🔐 Security Notes

**⚠️ Current Setup: Development Mode**

For production, implement:
- HTTPS/TLS certificates
- Strong password hashing
- JWT authentication
- Rate limiting
- Input validation
- CORS restrictions
- Environment secrets management

## 📈 Performance

### Resource Requirements
| Service        | Memory    | CPU   | Startup Time |
|----------------|-----------|-------|--------------|
| App Server     | 200MB     | Low   | 5s           |
| Raft Node (×3) | 100MB ea. | Low   | 5s           |
| LLM Server     | 2-4GB     | Medium| 30-60s       |

### Response Times
| Operation       | Expected Time |
|-----------------|---------------|
| Login/Register  | <50ms         |
| Book Ticket     | <200ms        |
| Raft Status     | <100ms        |
| LLM FAQ         | 2-5s (CPU)    |
| LLM Chat        | 3-7s (CPU)    |

## 🎯 Common Use Cases

### Development Workflow
```bash
# Edit code
vim Application_server/Application_server.py

# Rebuild and restart
docker compose build app-server
docker compose up -d app-server

# Check logs
docker compose logs -f app-server
```

### Testing Workflow
```bash
# Start services
docker compose up -d

# Run tests
python test_llm.py
./check_health.sh

# Stop services
docker compose down
```

### Production Deployment
```bash
# Pull latest code
git pull

# Build images
docker compose build

# Start with restart policy
docker compose up -d

# Monitor
docker compose logs -f
```

## 🆘 Getting Help

### Quick Diagnostics
```bash
# Check Docker
docker info

# Check services
docker compose ps

# View logs
docker compose logs --tail=50

# Run health check
./check_health.sh
```

### Common Issues
1. **Port already in use**: Kill process or change port.
2. **Out of memory**: Increase Docker memory or skip LLM.
3. **Connection refused**: Verify service is running.
4. **Model not loading**: Check LLM server logs.

## 📚 References

- [Raft Consensus Algorithm](https://raft.github.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [gRPC Python Guide](https://grpc.io/docs/languages/python/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Docker Compose Guide](https://docs.docker.com/compose/)

## 🤝 Contributing

Extend the project with:
- Persistent storage (PostgreSQL/MySQL)
- Payment gateway integration
- Real-time seat availability
- Email notifications
- Mobile client app

## 📝 License

This is an educational project for distributed systems learning.

## 👥 Authors

Aniket & Team  
Repository: [utkarsharora100/ds](https://github.com/utkarsharora100/ds)

---

**🎉 Ready to go! Run**:
```bash
docker compose up -d
```

