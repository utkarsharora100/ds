# 🎬 Distributed Movie Booking System

A production-ready distributed movie ticket booking system featuring a **FastAPI** backend, a 3-node **Raft consensus** cluster, and an **AI assistant** powered by **Qwen2.5-0.5B**. Deploy the entire stack with a single command.

## 📖 Overview

- **Raft Consensus**: 3-node cluster with automatic leader election and fault tolerance.
- **FastAPI Backend**: RESTful APIs for authentication, movie management, and ticket bookings.
- **AI Assistant**: Qwen2.5-0.5B LLM for intelligent FAQ and chat support.
- **SQLite Database**: Persistent storage with real-time seat tracking.
- **Multi-User GUI**: Supports concurrent clients with isolated bookings.
- **Docker-First**: Fully containerized with health monitoring and centralized logs.

## 🧩 Services and Ports

| Service         | Port   | Description                         |
|-----------------|--------|-------------------------------------|
| `app-server`    | `9000` | FastAPI backend for core operations |
| `raft-node1`    | `50051`| Raft consensus node 1               |
| `raft-node2`    | `50052`| Raft consensus node 2               |
| `raft-node3`    | `50053`| Raft consensus node 3               |
| `llm-server`    | `8500` | Qwen2.5-0.5B AI assistant server   |

## 🧰 Prerequisites

- **Docker**: Version 20.10+ ([Install Guide](https://docs.docker.com/get-docker/)).
- **Docker Compose**: Version 2.0+ (use `docker compose` or `docker-compose`).
- **Python**: 3.10+ (for GUI and testing).
- **System**: 6GB RAM (for LLM), 10GB free disk space.

## 🚀 Quick Start

### Step 1: Clone and Navigate

```bash
git clone https://github.com/utkarsharora100/ds.git
cd ds
```

### Step 2: Start Services

**Option A: Combined Setup (Recommended - Frontend + Backend)**
```bash
docker compose -f docker-compose.combined.yml up -d --build
```

**Option B: Standard Setup**
```bash
docker compose up -d --build
```

*First run takes ~10 minutes due to Docker image builds and LLM model download (~1GB).*

### Step 3: Verify Services

```bash
# Check container status
docker compose ps

# Check backend health
curl http://localhost:9000/health
```

### Step 4: Access the Application

**Web UI (Recommended):**
- **Combined Setup**: http://localhost:3000
- **Standard Setup**: http://localhost:8080 (after running `cd web && python3 -m http.server 8080`)

**Desktop GUI:**
```bash
# Single-window GUI
python3 app.py

# Multi-window GUI (3 clients + 1 admin)
python3 app_multi.py
```

### Step 5: Login

- **Admin**: `admin` / `123`
- **User**: `utkarsh` / `password123`

## 📚 Documentation

All documentation is organized in the `docs/` folder. Start here:

### 🎯 Getting Started
- **[QUICKSTART.md](docs/QUICKSTART.md)** - 2-minute setup guide
- **[HOW_TO_RUN.md](docs/HOW_TO_RUN.md)** - Detailed step-by-step run instructions
- **[COMBINED_SETUP.md](docs/COMBINED_SETUP.md)** - Combined frontend + backend setup guide

### 🐳 Docker & Deployment
- **[DOCKER.md](docs/DOCKER.md)** - Docker setup and configuration
- **[DOCKER_STEPS.md](docs/DOCKER_STEPS.md)** - Complete Docker commands reference

### 🏗️ Architecture & Development
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and architecture
- **[CLIENT_VIEW.md](docs/CLIENT_VIEW.md)** - API reference and GUI guide

### 🧪 Testing & Troubleshooting
- **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Command and port cheat sheet
- **[FIXES_SUMMARY.md](docs/FIXES_SUMMARY.md)** - Recent fixes and improvements

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

### Test Booking
```bash
# Login and get token
TOKEN=$(curl -s -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

# Book a ticket
curl -X POST http://localhost:9000/business \
  -H "Content-Type: application/json" \
  -d "{\"requestId\":\"booking-$(date +%s)\",\"payload\":{\"type\":\"book_seat\",\"data\":{\"movie\":\"Inception\",\"city\":\"Delhi\",\"seats\":2}},\"context\":{\"token\":\"$TOKEN\"}}"
```

## 🔌 API Endpoints

### Application Server (`:9000`)

| Method | Endpoint         | Description            | Auth Required      |
|--------|------------------|------------------------|--------------------|
| GET    | `/health`        | Health check           | No                 |
| POST   | `/register`      | Register new user      | No                 |
| POST   | `/login`         | User login             | No                 |
| GET    | `/data/{type}`   | Get movies/bookings    | Yes (token)        |
| POST   | `/business`      | Book tickets           | Yes (token)        |
| POST   | `/add_movie`     | Add movie              | Yes (admin token)  |
| POST   | `/admin/load_sample_data` | Load sample movies | Yes (admin token)  |
| POST   | `/admin/clear_database`   | Clear all data     | Yes (admin token)  |
| GET    | `/admin/health/all` | Check all services | No |

### Raft Nodes (`:50051-50053`)

| Method | Endpoint             | Description               | Auth Required |
|--------|----------------------|---------------------------|---------------|
| GET    | `/status`            | Node status & leader info | No            |
| POST   | `/trigger-election`  | Trigger leader election   | No            |

### LLM Server (`:8500`)

| Method | Endpoint   | Description            | Auth Required |
|--------|------------|------------------------|---------------|
| GET    | `/health`  | Health & model status  | No            |
| POST   | `/ask`     | Quick FAQ question     | No            |
| POST   | `/chat`    | Conversational AI      | No            |

## 🛠️ Utility Scripts

Located in `scripts/`:

| Script                     | Purpose                                    | Usage                              |
|----------------------------|--------------------------------------------|------------------------------------|
| `quickstart.sh`            | Complete setup and testing                 | `./quickstart.sh`                 |
| `check_health.sh`          | Verify service health and Raft leader       | `./scripts/check_health.sh`       |
| `reset_database.sh`        | Clear movies and bookings                  | `./scripts/reset_database.sh --force` |
| `load_sample_data.sh`      | Load 15 sample movies                      | `./scripts/load_sample_data.sh --force` |

**Make scripts executable** (one-time):
```bash
chmod +x scripts/*.sh
```

## 📁 Project Structure

```
ds/
├── README.md                    # This file - main documentation entry point
├── docker-compose.yml           # Standard service orchestration
├── docker-compose.combined.yml # Combined frontend + backend setup
├── requirements.txt            # Python dependencies
├── main.py                     # Raft node entry point
├── app.py                      # Single-window GUI
├── app_multi.py                # Multi-window GUI
├── start_combined.py           # Combined frontend + backend startup
├── Dockerfile.app              # Application server image
├── Dockerfile.raft             # Raft node image
├── Dockerfile.llm              # LLM server image
├── Dockerfile.combined         # Combined frontend + backend image
├── Application_server/         # FastAPI backend
│   └── Application_server.py
├── raft/                       # Raft consensus
│   ├── raft_node.py
│   └── raft_state.py
├── llm/                        # AI assistant
│   ├── llm_server.py
│   └── storage.py
├── web/                        # Web frontend
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── client/                     # Client simulator
│   └── client.py
├── proto/                      # gRPC definitions
│   └── raft.proto
├── tests/                      # Test suite
│   ├── test_complete_system.py
│   ├── test_client_view.py
│   ├── test_llm.py
│   ├── test_booking.py
│   └── test_raft.py
├── scripts/                    # Utility scripts
│   ├── quickstart.sh
│   ├── check_health.sh
│   ├── reset_database.sh
│   └── load_sample_data.sh
└── docs/                       # Documentation
    ├── QUICKSTART.md
    ├── HOW_TO_RUN.md
    ├── COMBINED_SETUP.md
    ├── DOCKER.md
    ├── DOCKER_STEPS.md
    ├── ARCHITECTURE.md
    ├── CLIENT_VIEW.md
    ├── QUICK_REFERENCE.md
    └── FIXES_SUMMARY.md
```

## 🐳 Docker Commands

### Quick Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f [service-name]

# Restart service
docker compose restart [service-name]

# Rebuild service
docker compose build [service-name] --no-cache
```

### Combined Setup

```bash
# Start combined frontend + backend
docker compose -f docker-compose.combined.yml up -d --build

# Access at http://localhost:3000
```

**Without LLM (Lower Resources)**:
```bash
docker compose up -d app-server raft-node1 raft-node2 raft-node3
```

See [DOCKER_STEPS.md](docs/DOCKER_STEPS.md) for complete Docker reference.

## ⚙️ Configuration

### Environment Variables

Create `.env` file (optional):

```bash
# Application Server
APP_SERVER_HOST=0.0.0.0
APP_SERVER_PORT=9000

# LLM Configuration
LLM_MODEL=Qwen/Qwen2.5-0.5B
LLM_MAX_NEW_TOKENS=512
LLM_TEMPERATURE=0.7

# Docker Mode
DOCKER_ENV=true
```

## 🧪 Testing

### Automated Tests

```bash
# Full system test
python tests/test_complete_system.py

# Specific tests
python tests/test_raft.py          # Raft consensus
python tests/test_booking.py       # Booking flow
python tests/test_llm.py           # LLM functionality
python tests/test_client_view.py   # Client features
```

### Manual Testing

```bash
# Health checks
./scripts/check_health.sh

# Raft cluster
for PORT in 50051 50052 50053; do curl http://localhost:$PORT/status; done

# LLM server
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the booking process?"}'
```

## 🩺 Troubleshooting

### Services Not Starting
```bash
# Check logs
docker compose logs [service] --tail=50

# Rebuild
docker compose build [service] --no-cache
docker compose up -d [service]
```

### Port Already in Use
```bash
# Find process (Linux/Mac)
sudo lsof -i :9000

# Find process (Windows)
netstat -ano | findstr :9000

# Kill process (replace PID)
taskkill /PID <PID> /F  # Windows
sudo kill -9 <PID>      # Linux/Mac
```

### LLM Server Issues
- **Out of Memory**: Increase Docker memory to 6GB+ or skip LLM
- **Slow First Call**: Model download (~1GB) takes 5-10 minutes initially
- **Check Logs**: `docker compose logs llm-server --tail=50`

### GUI Display Issues
- **Windows**: Use Web UI at http://localhost:3000
- **Linux/Mac**: Install `python3-tk` or use Web UI
- **Remote Access**: Use Web UI or SSH with X11 forwarding

See [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) for more troubleshooting tips.

## ✨ Key Features

- **Database Persistence**: SQLite with auto-save, survives restarts
- **Seat Management**: Real-time tracking, auto-decrement, overbooking prevention
- **Raft Consensus**: 3-node cluster, automatic leader election, fault tolerance
- **Multi-User Support**: Isolated bookings, admin visibility, concurrent access
- **AI Assistant**: Qwen2.5-0.5B for intelligent responses
- **GUI Application**: Single/multi-window modes with real-time updates
- **Health Monitoring**: Status endpoints for all services
- **RESTful APIs**: Comprehensive, documented endpoints

## 🔐 Security Notes

**⚠️ Development Mode**

For production:
- Enable HTTPS/TLS certificates
- Implement strong password hashing
- Use JWT authentication
- Add rate limiting and input validation
- Restrict CORS
- Manage secrets securely

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

## 🎯 Common Tasks

### Load Sample Data
```bash
./scripts/load_sample_data.sh --force
```

### Clear Database
```bash
./scripts/reset_database.sh --force
```

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

## 🆘 Getting Help

- **Logs**: `docker compose logs [service] --tail=50`
- **Health**: `./scripts/check_health.sh`
- **Tests**: `python tests/test_complete_system.py`
- **Docs**: See `docs/` folder for detailed documentation
- **Issues**: Check [Troubleshooting](#-troubleshooting) section above

## 📚 References

- [Raft Consensus Algorithm](https://raft.github.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Guide](https://docs.docker.com/compose/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)

## 🤝 Contributing

Add features like:
- Persistent storage (PostgreSQL/MySQL)
- Payment gateway integration
- Real-time seat availability
- Email notifications
- Mobile client app

## 📝 License

Educational project for distributed systems learning.

## 👥 Authors

Aniket & Team  
Repository: [utkarsharora100/ds](https://github.com/utkarsharora100/ds)

---

## 🎉 Ready to Start!

**Quick Start:**
```bash
docker compose -f docker-compose.combined.yml up -d --build
```

**Then access:** http://localhost:3000

**For detailed instructions, see:**
- [HOW_TO_RUN.md](docs/HOW_TO_RUN.md) - Step-by-step run guide
- [QUICKSTART.md](docs/QUICKSTART.md) - 2-minute setup
- [COMBINED_SETUP.md](docs/COMBINED_SETUP.md) - Combined setup details
