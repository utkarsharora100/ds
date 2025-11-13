# 🎬 Distributed Movie Booking System

A production-ready distributed movie ticket booking system featuring a **FastAPI** backend, a 3-node **Raft consensus** cluster, and an **AI assistant** powered by **DistilGPT-2** (ultra-fast 2-3 second responses). Deploy the entire stack with a single command.

## 📖 Overview

- **Raft Consensus**: 3-node cluster with automatic leader election and fault tolerance.
- **FastAPI Backend**: RESTful APIs for authentication, movie management, and ticket bookings.
- **AI Assistant** *(Optional)*: DistilGPT-2 LLM (82M params) for ultra-fast FAQ and chat support (2-3 second responses).
- **SQLite Database**: Persistent storage with real-time seat tracking.
- **Multi-User GUI**: Supports concurrent clients with isolated bookings.
- **Docker-First**: Fully containerized with health monitoring and centralized logs.

## 🧩 Services and Ports

| Service         | Port   | Description                         | Required |
|-----------------|--------|-------------------------------------|----------|
| `app-server`    | `9000` | FastAPI backend for core operations | ✅ Yes   |
| `raft-node1`    | `50051`| Raft consensus node 1               | ✅ Yes   |
| `raft-node2`    | `50052`| Raft consensus node 2               | ✅ Yes   |
| `raft-node3`    | `50053`| Raft consensus node 3               | ✅ Yes   |
| `llm-server`    | `8500` | DistilGPT-2 AI assistant (2-3s responses) | ⚠️ Optional |

## 🧰 Prerequisites

**Minimum (without LLM):**
- **Docker**: Version 20.10+ ([Install Guide](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0+ (use `docker compose` or `docker-compose`)
- **Python**: 3.10+ (for GUI and testing)
- **System**: 2GB RAM, 5GB free disk space

**With LLM (Optional):**
- **System**: 4GB RAM, 8GB free disk space
- **Note**: LLM server (DistilGPT-2) is lightweight and fast. Uses only 2GB RAM with 2-3 second responses

## 🚀 Quick Start

### Step 1: Clone and Navigate

```bash
git clone https://github.com/utkarsharora100/ds.git
cd ds
```

### Step 2: Choose Your Usage Method

This system supports **two different usage methods**. Choose the one that fits your needs:

---

## 📱 Method 1: CustomTkinter Desktop GUI + Standard Docker

**Best for:** Desktop applications, local development, GUI testing

### Setup Steps:

**2.1: Start Backend Services (Docker)**
```bash
# Start backend services (app-server, raft nodes, LLM)
docker compose up -d --build
```

**2.2: Verify Services**
```bash
# Check container status
docker compose ps

# Check backend health
curl http://localhost:9000/health
```

**2.3: Install GUI Dependencies**
```bash
# Install Python dependencies for GUI
pip install -r requirements/requirements-app.txt
# OR
pip install customtkinter requests
```

**2.4: Launch Desktop GUI**

**Single-Window GUI:**
```bash
python app.py
```

**Multi-Window GUI (3 clients + 1 admin):**
```bash
python app_multi.py
```

**2.5: Login**
- **Admin**: `admin` / `123`
- **User**: `utkarsh` / `password123`

**Access Points:**
- Backend API: http://localhost:9000
- Desktop GUI: Launched via Python scripts

---

## 🌐 Method 2: Web UI + Combined Docker (Frontend + Backend)

**Best for:** Web applications, remote access, production deployment

### Setup Steps:

**2.1: Start Combined Services (Docker)**
```bash
# Start all services including web frontend
docker compose -f docker-compose.combined.yml up -d --build
```

This starts:
- ✅ Backend API (port 9000)
- ✅ Web Frontend (port 3000)
- ✅ Raft Nodes (ports 50051-50053)
- ✅ LLM Server (port 8500, optional)

**2.2: Verify Services**
```bash
# Check container status
docker compose -f docker-compose.combined.yml ps

# Check backend health
curl http://localhost:9000/health

# Check frontend
curl http://localhost:3000
```

**2.3: Access Web Application**
```
Open in browser: http://localhost:3000
```

**2.4: Login**
- **Admin**: `admin` / `123`
- **User**: `utkarsh` / `password123`

**Access Points:**
- Web UI: http://localhost:3000
- Backend API: http://localhost:9000

---

## 📊 Comparison: Method 1 vs Method 2

| Feature | Method 1: Desktop GUI | Method 2: Web UI |
|---------|----------------------|------------------|
| **Interface** | CustomTkinter Desktop App | Web Browser |
| **Docker Setup** | Standard (`docker-compose.yml`) | Combined (`docker-compose.combined.yml`) |
| **Frontend** | Runs locally (Python) | Runs in Docker (port 3000) |
| **Backend** | Docker (port 9000) | Docker (port 9000) |
| **Remote Access** | Requires X11/SSH forwarding | Works over network |
| **Best For** | Local development, GUI testing | Production, remote access |
| **Dependencies** | Python + customtkinter | Just Docker + Browser |

---

## ⚡ Quick Commands Summary

### Method 1: Desktop GUI
```bash
# Start backend
docker compose up -d

# Run GUI
python app.py              # Single window
python app_multi.py        # Multi window (3 clients + admin)
```

### Method 2: Web UI
```bash
# Start everything (including web frontend)
docker compose -f docker-compose.combined.yml up -d --build

# Access at http://localhost:3000
```

*First run takes ~10 minutes due to Docker image builds and LLM model download (~1GB).*

## 📚 Documentation

All documentation is organized in the `docs/` folder. See **[docs/INDEX.md](docs/INDEX.md)** for complete documentation index.

### 🎯 Getting Started
- **[QUICKSTART.md](docs/QUICKSTART.md)** - 2-minute setup guide
- **[HOW_TO_RUN.md](docs/HOW_TO_RUN.md)** - Detailed step-by-step run instructions
- **[COMBINED_SETUP.md](docs/COMBINED_SETUP.md)** - Combined frontend + backend setup guide

### 🐳 Docker & Deployment
- **[DOCKER.md](docs/DOCKER.md)** - Docker setup and configuration
- **[DOCKER_STEPS.md](docs/DOCKER_STEPS.md)** - Complete Docker commands reference
- **[DOCKER_OPTIMIZATION.md](docs/DOCKER_OPTIMIZATION.md)** - Build time optimizations

### 🏗️ Architecture & Development
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and architecture
- **[CLIENT_VIEW.md](docs/CLIENT_VIEW.md)** - API reference and GUI guide

### 🔧 Recent Fixes & Changes
- **[COMPREHENSIVE_CHANGES_SUMMARY.md](docs/COMPREHENSIVE_CHANGES_SUMMARY.md)** - Complete overview of all recent fixes
- **[RAFT_FIX_BEFORE_AFTER.md](docs/RAFT_FIX_BEFORE_AFTER.md)** - Raft leader election fix explained
- **[MONGODB_MIGRATION_GUIDE.md](docs/MONGODB_MIGRATION_GUIDE.md)** - MongoDB migration details
- **[IMPORT_ERROR_FIX.md](docs/IMPORT_ERROR_FIX.md)** - MongoDB import error fix

### 🧪 Testing & Troubleshooting
- **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Command and port cheat sheet
- **[FIXES_SUMMARY.md](docs/FIXES_SUMMARY.md)** - Summary of all known fixes

### 📖 Complete Documentation Index
See **[docs/INDEX.md](docs/INDEX.md)** for the complete documentation index with all 20+ documentation files organized by topic.

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

All scripts are located in the `scripts/` directory. See [scripts/README.md](scripts/README.md) for complete documentation.

### 🚀 Quick Start & Setup Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| **quickstart.sh** | Complete automated setup and testing | `./scripts/quickstart.sh` |
| **quickstart-optimized.sh** | Optimized setup with build caching | `./scripts/quickstart-optimized.sh` |
| **start-with-mongodb.sh** | Start system with MongoDB persistence | `./scripts/start-with-mongodb.sh` |

### 🔧 Fix & Maintenance Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| **fix-raft-leader.sh** | Fix Raft leader election bug | Multiple nodes showing as "leader" |
| **fix-import-error.sh** | Fix MongoDB import error | Backend crashes with ModuleNotFoundError |
| **apply-all-fixes.sh** | Apply all known fixes at once | After pulling latest code |
| **rebuild-with-fixes.sh** | Complete rebuild with all fixes | Persistent issues |

### 🩺 Health Check & Monitoring Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| **check_health.sh** | Comprehensive health check of all services | `./scripts/check_health.sh` |

**Example Output:**
```
✓ App Server: OK
✓ MongoDB: Connected
✓ Raft Node 1: Follower
✓ Raft Node 2: Leader  ← Only one!
✓ Raft Node 3: Follower
⚠ LLM Server: Starting up...
```

### 🗄️ Database Management Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| **load_sample_data.sh** | Load 15 sample movies | `./scripts/load_sample_data.sh --force` |
| **reset_database.sh** | Clear all movies and bookings | `./scripts/reset_database.sh --force` |

### 🧪 Testing & Verification Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| **test_llm_viability.sh** | Test LLM service functionality | `./scripts/test_llm_viability.sh` |
| **verify-code.sh** | Verify code syntax and structure | `./scripts/verify-code.sh` |

### 🔄 Project Management Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| **reorganize-project.sh** | Reorganize project structure | `./scripts/reorganize-project.sh` |
| **quick-fix.sh** | Quick fix for common issues | `./scripts/quick-fix.sh` |

### 📋 Common Script Workflows

**First Time Setup:**
```bash
./scripts/quickstart.sh
```

**Fix Specific Issues:**
```bash
# Fix Raft leader election
./scripts/fix-raft-leader.sh

# Fix MongoDB import error
./scripts/fix-import-error.sh

# Check system health
./scripts/check_health.sh
```

**Database Management:**
```bash
# Load sample movies
./scripts/load_sample_data.sh --force

# Reset database
./scripts/reset_database.sh --force
```

**Complete Documentation:** See [scripts/README.md](scripts/README.md) for detailed documentation of all scripts.

**Make scripts executable** (one-time):
```bash
chmod +x scripts/*.sh
```

## 📁 Project Structure

```
ds/
├── README.md                    # This file - main documentation entry point
├── docker-compose.yml           # Method 1: Standard setup (for Desktop GUI)
├── docker-compose.combined.yml # Method 2: Combined setup (for Web UI)
├── requirements/
│   ├── requirements.txt        # Full Python dependencies (includes LLM)
│   ├── requirements-app.txt    # GUI dependencies only (for Method 1)
│   ├── requirements-raft.txt   # Raft node dependencies
│   ├── requirements-llm.txt    # LLM server dependencies
│   └── requirements-base.txt   # Base dependencies
├── docker/
│   ├── Dockerfile.app          # Application server image
│   ├── Dockerfile.raft         # Raft node image
│   ├── Dockerfile.llm          # LLM server image
│   └── Dockerfile.combined     # Method 2: Combined frontend + backend image
├── main.py                     # Raft node entry point
├── app.py                      # Method 1: Single-window GUI
├── app_multi.py                # Method 1: Multi-window GUI
├── start_combined.py           # Method 2: Combined frontend + backend startup
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

### Method 1: Standard Docker (for Desktop GUI)

```bash
# Start backend services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f [service-name]

# Restart service
docker compose restart [service-name]

# Rebuild service
docker compose build [service-name] --no-cache
```

### Method 2: Combined Docker (for Web UI)

```bash
# Start all services (including web frontend)
docker compose -f docker-compose.combined.yml up -d --build

# Stop services
docker compose -f docker-compose.combined.yml down

# View logs
docker compose -f docker-compose.combined.yml logs -f movie-booking-app

# Rebuild
docker compose -f docker-compose.combined.yml build --no-cache movie-booking-app
```

### Without LLM (Lower Resources)

**Method 1:**
```bash
docker compose up -d app-server raft-node1 raft-node2 raft-node3
```

**Method 2:**
```bash
docker compose -f docker-compose.combined.yml up -d movie-booking-app raft-node1 raft-node2 raft-node3
```

See [DOCKER_STEPS.md](docs/DOCKER_STEPS.md) for complete Docker reference.

## ⚙️ Configuration

### Environment Variables

Create `.env` file (optional):

```bash
# Application Server
APP_SERVER_HOST=0.0.0.0
APP_SERVER_PORT=9000

# LLM Configuration (DistilGPT-2 - Ultra-Fast)
LLM_MODEL=distilgpt2
LLM_MAX_NEW_TOKENS=128
LLM_TEMPERATURE=0.8
LLM_TOP_P=0.95

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
- **AI Assistant**: DistilGPT-2 (82M params) for ultra-fast responses (2-3 seconds)
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
