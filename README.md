# 🎬 Distributed Movie Booking System

# 🎬 Distributed Movie Booking System

A production-ready distributed movie ticket booking system featuring **FastAPI** backend, **3-node Raft consensus** cluster, and **Qwen2.5-0.5B AI assistant**. Complete setup in one command.

A distributed movie ticket booking system featuring a **FastAPI** backend, a 3-node **Raft consensus** cluster, and an **AI assistant** powered by **Qwen2.5-0.5B**. The entire stack runs with a single Docker command.

## 📖 Overview

## 📖 Overview

- **Raft Consensus**: 3-node cluster with automatic leader election and fault tolerance

- **FastAPI Backend**: RESTful API with authentication, bookings, and seat management- **Raft Consensus**: 3-node cluster with automatic leader election and status endpoints.

- **AI Assistant**: Qwen2.5-0.5B LLM for intelligent chat support- **FastAPI Backend**: Handles user authentication, movie management, and ticket bookings.

- **SQLite Database**: Persistent storage with real-time seat tracking- **AI Assistant**: Qwen2.5-0.5B LLM for FAQ and chat assistance.

- **Multi-User GUI**: Concurrent client support with isolated bookings- **Docker-First**: Fully containerized with health checks and centralized logs.

- **Docker-First**: Fully containerized with health monitoring

## 🧩 Services and Ports

## 🧩 Services and Ports

| Service         | Port       | Description                          |

| Service       | Port    | Description                          ||-----------------|------------|--------------------------------------|

|---------------|---------|--------------------------------------|| `app-server`    | `9000`     | FastAPI backend for core operations  |

| `app-server`  | `9000`  | FastAPI backend for core operations  || `raft-node1`    | `50051`    | Raft consensus node 1                |

| `llm-server`  | `8500`  | Qwen2.5-0.5B AI assistant            || `raft-node2`    | `50052`    | Raft consensus node 2                |

| `raft-node1`  | `50051` | Raft consensus node 1 (leader)       || `raft-node3`    | `50053`    | Raft consensus node 3                |

| `raft-node2`  | `50052` | Raft consensus node 2                || `llm-server`    | `8500`     | Qwen2.5-0.5B AI assistant server     |

| `raft-node3`  | `50053` | Raft consensus node 3                |

## 🧰 Prerequisites

## 🚀 Quick Start - One Command

- **Docker**: Version 20.10+ installed and running.

```bash- **Docker Compose**: Version 2.0+ (use `docker compose` or fallback to `docker-compose`).

./quickstart.sh- **System Requirements**: 6GB RAM (for LLM), ~10GB free disk space.

```- **Optional**: For Arch Linux, see [INSTALL_DOCKER.md](docs/INSTALL_DOCKER.md).



**That's it!** This single command will:## 📚 Documentation

1. ✅ Check prerequisites (Docker, Python, venv)

2. ✅ Build all Docker images (~10 min first time)### Essential Documentation

3. ✅ Start 5 services simultaneously- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design

4. ✅ Run health checks on all endpoints- **[QUICKSTART.md](docs/QUICKSTART.md)** - Getting started guide

5. ✅ Test Raft consensus & leader election- **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Command reference and API table

6. ✅ Test authentication & booking APIs- **[DOCKER.md](docs/DOCKER.md)** - Docker setup and configuration

7. ✅ Optionally load 15 sample movies- **[CLIENT_VIEW.md](docs/CLIENT_VIEW.md)** - Complete API documentation and GUI guide

8. ✅ Display all available options

## 🛠️ Utility Scripts

---

All scripts are located in the `scripts/` folder:

## 🧪 Testing Guide

| Script | Description |

### Option 1: Backend Only (API Testing via CLI)|--------|-------------|

| `start.sh` | Start all Docker services with health check |

Perfect for headless servers, SSH sessions, or CI/CD:| `check_health.sh` | Verify all services are healthy and Raft leader is elected |

| `reset_database.sh` | Clear all movies and bookings from database |

```bash| `load_sample_data.sh` | Load 10+ sample movies for testing |

# 1. Ensure services are running| `test_llm_viability.sh` | Test LLM server endpoints (/health, /ask, /chat) |

sudo docker compose ps| `demo_complete_system.sh` | **Comprehensive demo** of all features |



# 2. Check health### Running Scripts

./scripts/check_health.sh

```bash

# 3. Test authentication# Make scripts executable (one-time setup)

curl -X POST http://localhost:9000/register \chmod +x scripts/*.sh

  -H "Content-Type: application/json" \

  -d '{"username":"demo","password":"demo123"}'# Run complete system demo

./scripts/demo_complete_system.sh

# 4. Login and get token

TOKEN=$(curl -s -X POST http://localhost:9000/login \# Or run individual scripts

  -H "Content-Type: application/json" \./scripts/check_health.sh

  -d '{"username":"demo","password":"demo123"}' | \./scripts/load_sample_data.sh

  python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")./scripts/test_llm_viability.sh

```

echo "Token: $TOKEN"

- **[check_health.sh](scripts/check_health.sh)** - Check health of all services

# 5. Get available movies- **[start.sh](scripts/start.sh)** - Start all Docker services

curl -s "http://localhost:9000/data/movies?token=$TOKEN" | python3 -m json.tool- **[demo_client_view.sh](scripts/demo_client_view.sh)** - Demonstrate client view functionality

- **[demo_gui_features.sh](scripts/demo_gui_features.sh)** - GUI feature demonstration via CLI

# 6. Book a ticket- **[test_database_integration.sh](scripts/test_database_integration.sh)** - Test database integration

curl -X POST http://localhost:9000/business \

  -H "Content-Type: application/json" \## 🚀 Quick Start

  -d '{

    "requestId": "test-001",### Step 1: Start Docker Services

    "payload": {

      "type": "book_seat",```bash

      "data": {"movie": "Inception", "city": "New York", "seats": 2}# Start all services (app-server, llm-server, raft nodes)

    },sudo docker compose up -d

    "context": {"token": "'$TOKEN'"}

  }'# Wait for services to initialize (30-60 seconds for first run)

sleep 5

# 7. Check bookings

curl -s "http://localhost:9000/data/bookings?token=$TOKEN" | python3 -m json.tool# Check if services are running

```sudo docker compose ps

```

### Option 2: Frontend (GUI Testing)

**Expected Output:**

If you have a graphical display:```

NAME                IMAGE           STATUS

```bashmovie-app-server    ds-app-server   Up (healthy)

# Single window (switch between admin/client)movie-llm-server    ds-llm-server   Up

python3 app.pyraft-node1          ds-raft-node1   Up

raft-node2          ds-raft-node2   Up

# Multi-window (3 clients + 1 admin simultaneously)raft-node3          ds-raft-node3   Up

python3 app_multi.py```

```

### Step 2: Verify Services Health

**Default Credentials:**

- **Admin**: username=`admin`, password=`123````bash

- **User**: username=`utkarsh`, password=`password123`# Quick health check

curl http://localhost:9000/health

**Admin Dashboard Features:**curl http://localhost:50051/status

- ✅ Add movies with custom seat counts

- ✅ Load 15 sample movies (one click)# Or use the health check script

- ✅ Clear database (with confirmation)./scripts/check_health.sh

- ✅ View all bookings from all users```

- ✅ Test Raft consistency

- ✅ Simulate concurrent bookings### Step 3: Open the GUI Application



**Client Dashboard Features:****Option A: With X11 Forwarding (Remote Access from Mac/Linux)**

- ✅ Register new accounts

- ✅ Browse movies with real-time seat availability1. **On your Mac**, install XQuartz:

- ✅ Book multiple tickets   ```bash

- ✅ View personal bookings (isolated per user)   brew install --cask xquartz

- ✅ Real-time data refresh   # Log out and back in after installation

   ```

### Option 3: Raft Consensus Testing

2. **Update SSH config** on Mac (`~/.ssh/config`):

```bash   ```ssh_config

# Check cluster status   Host archlinux

./scripts/check_health.sh     HostName <your-host-ip>

     User <your-username>

# Detailed Raft node status     ForwardX11 yes

for PORT in 50051 50052 50053; do     ForwardX11Trusted yes

  echo "=== Node on port $PORT ==="   ```

  curl -s http://localhost:$PORT/status | python3 -m json.tool

  echo ""3. **Connect with X11 forwarding**:

done   ```bash

   ssh -X archlinux

# Test leader election (simulate failure)   ```

# 1. Find current leader

LEADER=$(curl -s http://localhost:50051/status | \4. **Run the GUI**:

  python3 -c "import sys, json; print(json.load(sys.stdin)['currentLeader'])")   ```bash

echo "Current leader: $LEADER"   cd /home/aniket/study/ds

   ./venv/bin/python app.py

# 2. Stop the leader   ```

LEADER_NODE=$(echo $LEADER | sed 's/.*node/node/')

sudo docker compose stop raft-$LEADER_NODE**Option B: Local Desktop Access**



# 3. Wait for new election (typically 2-5 seconds)If you have physical access or VNC/RDP:

echo "Waiting for new leader election..."

sleep 5```bash

cd /home/aniket/study/ds

# 4. Verify new leader elected./venv/bin/python app.py

./scripts/check_health.sh```



# 5. Restart stopped node**Option C: CLI Testing (No GUI Required)**

sudo docker compose start raft-$LEADER_NODE

Test all functionality without graphical display:

# 6. Verify cluster health restored

sleep 3```bash

./scripts/check_health.sh# Run comprehensive system demo (recommended)

```./scripts/demo_complete_system.sh



### Option 4: LLM AI Assistant Testing# Or run tests programmatically

./venv/bin/python tests/test_complete_system.py

```bash```

# Run comprehensive LLM tests

./scripts/test_llm_viability.sh### Step 4: Use the Application



# Or test manually#### Multi-Window Demo (Recommended)

# 1. Health check

curl http://localhost:8500/health | python3 -m json.toolLaunch 3 clients + 1 admin simultaneously to see Raft consistency:



# 2. Ask a question```bash

curl -X POST http://localhost:8500/ask \python3 app_multi.py

  -H "Content-Type: application/json" \```

  -d '{"question": "How do I book a movie ticket?"}' | \

  python3 -m json.toolThis opens:

- **1 Admin window**: Add movies, view all bookings

# 3. Chat conversation- **3 Client windows**: Register users, book movies independently

curl -X POST http://localhost:8500/chat \- Each user sees only their own bookings (data isolation)

  -H "Content-Type: application/json" \- Admin sees all bookings from all users (full visibility)

  -d '{

    "messages": [#### Single Window Mode

      {"role": "user", "content": "What movies are available?"}

    ]```bash

  }' | python3 -m json.toolpython3 app.py

``````



### Option 5: Full Integration Test Suite**Admin Dashboard Features:**

- Add movies with custom seat counts

```bash- Load sample data with one click

# Run all Python tests- View all movies with real-time seat availability

./venv/bin/python tests/test_complete_system.py- See all user bookings

- Default login: `admin` / `123`

# Or individual test modules

./venv/bin/python tests/test_raft.py          # Raft consensus**Client Dashboard Features:**

./venv/bin/python tests/test_booking.py       # Booking flow- Browse available movies with city and seat information

./venv/bin/python tests/test_llm.py           # LLM functionality- Book tickets with custom quantity

./venv/bin/python tests/test_client_view.py   # Client features- View personal booking history (isolated per user)

```- Register new accounts with validation

- Real-time data refresh

---

### Key Features

## 📋 Utility Scripts

✨ **Database Integration**

All scripts in `scripts/` folder:- Movies persist in SQLite database

- Seat counts stored and managed automatically

| Script | Purpose | Usage |- Data survives server restarts

|--------|---------|-------|

| **quickstart.sh** | Complete setup & testing | `./quickstart.sh` |✨ **Seat Management**

| **check_health.sh** | Health check all services | `./scripts/check_health.sh` |- Admin sets initial seat count when adding movies (default: 50)

| **reset_database.sh** | Clear all data | `./scripts/reset_database.sh --force` |- Seats decrement automatically on booking

| **load_sample_data.sh** | Load 15 test movies | `./scripts/load_sample_data.sh --force` |- Validation prevents overbooking

| **test_llm_viability.sh** | Test LLM endpoints | `./scripts/test_llm_viability.sh` |- Real-time seat availability display



---✨ **Raft Consensus**

- 3-node cluster with automatic leader election

## 🎯 Common Tasks- Health monitoring via `/status` endpoints

- Fault tolerance and data consistency

### Load Sample Data

```bash✨ **Multi-User Support**

./scripts/load_sample_data.sh --force- Isolated bookings per user

```- Admin full visibility

Loads 15 movies across 8 cities with varying seat counts (70-200 seats)- Concurrent booking support



### Clear Database### Default Test Users

```bash

./scripts/reset_database.sh --force| Username  | Password      | Role   |

```|-----------|---------------|--------|

Removes all movies and bookings (requires confirmation without `--force`)| `admin`   | `123`         | Admin  |

| `utkarsh` | `password123` | User   |

### View Logs

```bash## 🧪 Try It Out

# All services

sudo docker compose logs### Test Login

```bash

# Specific servicecurl -X POST http://localhost:9000/login \

sudo docker compose logs app-server  -H "Content-Type: application/json" \

sudo docker compose logs raft-node1  -d '{"username":"admin","password":"123"}'

sudo docker compose logs llm-server```



# Follow logs in real-time### Test AI Assistant

sudo docker compose logs -f app-server```bash

```curl -X POST http://localhost:8500/ask \

  -H "Content-Type: application/json" \

### Restart Service  -d '{"question":"How do I book a ticket?"}'

```bash```

# Restart specific service

sudo docker compose restart app-server### Test Client View (GUI or CLI)

```bash

# Restart all# CLI Demo (no GUI needed)

sudo docker compose restart./demo_client_view.sh



# Stop all# GUI Application (requires display)

sudo docker compose downpip install customtkinter requests

export DISPLAY=:0

# Start allpython app.py

sudo docker compose up -d```

```

### View Logs

---```bash

docker compose logs -f

## 🔌 API Endpoints Reference```



### Authentication## 🎨 Client View Features

```bash

POST /register  # Register new userThe enhanced client view provides a complete user interface for movie booking:

POST /login     # Login and get token

```**Features:**

- ✅ User registration and authentication

### User Operations- ✅ Dual-panel dashboard (movies & bookings)

```bash- ✅ Real-time movie browsing with city and seat info

GET  /data/movies?token=TOKEN       # List all movies- ✅ Interactive ticket booking with validation

GET  /data/bookings?token=TOKEN     # User's bookings- ✅ Personal booking history

POST /business                       # Book tickets- ✅ Manual refresh from server

```- ✅ Token-based security



### Admin Operations (requires admin token)**Quick Test:**

```bash```bash

POST /add_movie                      # Add movie with seats# Register a user

POST /admin/load_sample_data         # Load 15 sample moviescurl -X POST http://localhost:9000/register \

POST /admin/clear_database           # Clear all data  -H "Content-Type: application/json" \

```  -d '{"username":"john","password":"pass123"}'



### Raft Cluster# Login and get token

```bashTOKEN=$(curl -s -X POST http://localhost:9000/login \

GET /status  # Node status, term, leader (ports 50051-50053)  -H "Content-Type: application/json" \

```  -d '{"username":"john","password":"pass123"}' | \

  grep -o '"token":"[^"]*"' | cut -d'"' -f4)

### LLM Assistant

```bash# View movies

GET  /health  # LLM server healthcurl "http://localhost:9000/data/movies?token=$TOKEN"

POST /ask     # Quick FAQ question

POST /chat    # Conversational AI# Book a ticket

```curl -X POST http://localhost:9000/business \

  -H "Content-Type: application/json" \

**Full API documentation:** See [CLIENT_VIEW.md](docs/CLIENT_VIEW.md)  -d "{

    \"requestId\":\"booking-$(date +%s)\",

---    \"payload\":{

      \"type\":\"book_seat\",

## 📚 Documentation      \"data\":{\"movie\":\"Inception\",\"city\":\"Delhi\",\"seats\":2}

    },

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design & architecture    \"context\":{\"token\":\"$TOKEN\"}

- **[CLIENT_VIEW.md](docs/CLIENT_VIEW.md)** - Complete API reference with examples  }"

- **[DOCKER.md](docs/DOCKER.md)** - Docker setup & configuration```

- **[QUICKSTART.md](docs/QUICKSTART.md)** - Detailed setup guide

- **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Command cheat sheetSee [CLIENT_VIEW.md](docs/CLIENT_VIEW.md) for complete documentation.



---## 🧪 Testing



## 🏗️ Project Structure### Automated Tests



```All test files are located in the `tests/` folder:

├── Application_server/        # FastAPI backend

│   └── Application_server.py  # REST API with database```bash

├── raft/                       # Raft consensus implementation# Complete system test (Python) - Tests database, seats, booking, Raft

│   ├── raft_node.py           # Node with leader election./venv/bin/python tests/test_complete_system.py

│   └── raft_state.py          # State management

├── llm/                        # AI assistant# Client view test

│   ├── llm_server.py          # Qwen2.5-0.5B integration./venv/bin/python tests/test_client_view.py

│   └── storage.py             # SQLite database functions

├── client/                     # Client simulator# LLM server test

├── proto/                      # gRPC protocol definitions./venv/bin/python tests/test_llm.py

├── tests/                      # Test suite (5 files)

├── scripts/                    # Utility scripts (5 files)# Database integration test (Shell)

├── docs/                       # Documentation (5 files)./scripts/test_database_integration.sh

├── app.py                      # Single-window GUI

├── app_multi.py                # Multi-window GUI (3 clients + admin)# Client view demonstration (Shell)

├── docker-compose.yml          # Service orchestration./scripts/demo_client_view.sh

├── Dockerfile.app              # App server image

├── Dockerfile.raft             # Raft node image# GUI features demonstration (Shell)

├── Dockerfile.llm              # LLM server image./scripts/demo_gui_features.sh

└── quickstart.sh               # One-command setup```

```

**Expected Test Results:**

---```

✅ Health Check: Passed

## 🛠️ Manual Setup (Alternative to Quickstart)✅ Database Integration: Movies stored and retrieved

✅ Seat Management: Counts display correctly (not "N/A")

If you prefer step-by-step setup:✅ Booking Logic: Seats decrement (100 → 85 → 70)

✅ Validation: Insufficient seats rejected

```bash✅ Raft Cluster: All 3 nodes healthy, leader election working

# 1. Build images```

sudo docker compose build

### Manual Testing

# 2. Start services

sudo docker compose up -dTest individual components:



# 3. Wait for initialization```bash

sleep 30# Health checks

./scripts/check_health.sh

# 4. Check health

./scripts/check_health.sh# Test Raft cluster

curl http://localhost:50051/status

# 5. Load datacurl http://localhost:50052/status

./scripts/load_sample_data.sh --forcecurl http://localhost:50053/status



# 6. Test# Test LLM server

python3 app.py  # or app_multi.pycurl -X POST http://localhost:8500/ask \

```  -H "Content-Type: application/json" \

  -d '{"question":"What is the booking process?"}'

---```



## ✨ Key FeaturesSee [CLIENT_VIEW_TESTING.md](docs/CLIENT_VIEW_TESTING.md) and [RAFT_TESTING.md](docs/RAFT_TESTING.md) for detailed testing procedures.



- ✅ **Database Persistence** - SQLite with auto-save## 📚 Documentation

- ✅ **Seat Management** - Real-time tracking, validation, auto-decrement

- ✅ **Raft Consensus** - 3-node cluster, automatic leader election- [QUICKSTART.md](docs/QUICKSTART.md): 2-minute setup guide.

- ✅ **Multi-User Support** - Isolated bookings per user- [DOCKER.md](docs/DOCKER.md): Complete Docker deployment instructions.

- ✅ **Admin Controls** - Full CRUD operations- [LLM_TESTING.md](docs/LLM_TESTING.md): AI assistant endpoints and examples.

- ✅ **AI Assistant** - Qwen2.5-0.5B for intelligent responses- [ARCHITECTURE.md](docs/ARCHITECTURE.md): System and Docker architecture.

- ✅ **Health Monitoring** - Status endpoints for all services- [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md): Command and port cheat sheet.

- ✅ **Fault Tolerance** - Automatic failover and recovery- [CLIENT_VIEW.md](docs/CLIENT_VIEW.md): Enhanced client view documentation and testing guide.

- ✅ **RESTful API** - Complete documentation with examples

- ✅ **GUI Application** - Single & multi-window modes## 🩺 Troubleshooting



---### Common Issues



## 🐳 Docker Commands- **"command not found: docker-compose"**: Use `docker compose` or install Compose V2.

- **Ports in use**: Free ports `9000`, `8500`, `50051-50053` or edit `docker-compose.yml`.

```bash- **LLM slow on first call**: Model loads on first request; subsequent calls are faster.

# View running containers- **Low memory**: Start without LLM:

sudo docker compose ps  ```bash

  docker compose up -d app-server raft-node1 raft-node2 raft-node3

# Check resource usage  ```

sudo docker stats

### GUI Display Issues

# View logs

sudo docker compose logs -f [service-name]**Error: `_tkinter.TclError: no display name and no $DISPLAY environment variable`**



# Restart serviceThis means you're in a terminal-only session. Solutions:

sudo docker compose restart [service-name]

1. **Use X11 Forwarding** (see "Step 3: Open the GUI Application" above)

# Rebuild after code changes2. **Use CLI Testing** instead:

sudo docker compose build [service-name] --no-cache   ```bash

sudo docker compose up -d [service-name]   ./venv/bin/python tests/test_complete_system.py

   ```

# Stop all

sudo docker compose downSee [CLIENT_VIEW_GUIDE.md](docs/CLIENT_VIEW_GUIDE.md) for detailed GUI troubleshooting.



# Remove all containers and volumes## 📁 Project Structure

sudo docker compose down -v

``````

ds/

---├── docker-compose.yml          # Service orchestration

├── .env                       # Environment variables

## 🧰 Prerequisites├── requirements.txt           # Python dependencies

├── Dockerfile.app             # Application server image

- **Docker**: v20.10+ ([Install Guide](https://docs.docker.com/get-docker/))├── Dockerfile.raft            # Raft node image

- **Docker Compose**: v2.0+├── Dockerfile.llm             # LLM server image

- **Python**: 3.10+ (for GUI and testing)├── app.py                     # GUI application (single window)

- **System**: 6GB RAM minimum, 10GB free disk├── app_multi.py               # Multi-window GUI (3 clients + admin)

├── main.py                    # Main entry point

---├── Application_server/        # FastAPI backend

│   └── Application_server.py  # REST API with database integration

## 🚨 Troubleshooting├── raft/                      # Raft consensus implementation

│   ├── raft_node.py          # Raft node with leader election

### GUI Not Working?│   └── raft_state.py         # Raft state management

You're likely in a TTY/SSH session without graphical display.├── llm/                       # AI assistant server

│   ├── llm_server.py         # Qwen2.5-0.5B integration

**Solutions:**│   └── storage.py            # Database functions (SQLite)

1. Use CLI testing (see "Option 1: Backend Only" above)├── client/                    # Client simulator

2. Connect with X11 forwarding: `ssh -X user@host`│   └── client.py

3. Use VNC/RDP for graphical access├── proto/                     # gRPC definitions

│   └── raft.proto

### Services Not Starting?├── tests/                     # Test files

```bash│   ├── test_complete_system.py    # Full system test

# Check logs│   ├── test_client_view.py        # Client view tests

sudo docker compose logs app-server --tail=50│   ├── test_llm.py               # LLM server tests

sudo docker compose logs raft-node1 --tail=50│   ├── test_booking.py           # Booking tests

│   └── test_raft.py              # Raft tests

# Restart service├── scripts/                   # Shell scripts

sudo docker compose restart app-server│   ├── check_health.sh       # Health check script

│   ├── start.sh              # Start Docker services

# Rebuild if code changed│   ├── reset_database.sh     # Clear database

sudo docker compose build app-server --no-cache│   ├── load_sample_data.sh   # Load test movies

sudo docker compose up -d app-server│   ├── test_llm_viability.sh # Test LLM endpoints

```│   └── demo_complete_system.sh # Comprehensive demo

└── docs/                      # Documentation

### LLM Server Failing?    ├── ARCHITECTURE.md        # System design

LLM requires significant resources. Check:    ├── QUICKSTART.md          # Quick start guide

```bash    ├── QUICK_REFERENCE.md     # Command reference

sudo docker compose logs llm-server --tail=50    ├── DOCKER.md              # Docker setup

```    └── CLIENT_VIEW.md         # API & GUI guide

First run downloads ~1GB model. Can take 5-10 minutes.```



### Port Already in Use?## 🔌 API Endpoints

```bash

# Find process using port### Application Server (`:9000`)

sudo lsof -i :9000

| Method | Endpoint         | Description            | Auth Required |

# Kill process|--------|------------------|------------------------|---------------|

sudo kill -9 <PID>| GET    | `/health`        | Health check           | No            |

| POST   | `/register`      | Register new user      | No            |

# Or change port in docker-compose.yml| POST   | `/login`         | User login             | No            |

```| GET    | `/data/{type}`   | Get movies/bookings    | Yes (token)   |

| POST   | `/business`      | Book tickets           | Yes (token)   |

---| POST   | `/add_movie`     | Add movie (admin only) | Yes (admin)   |



## 📞 Support & Resources**Example - Book a Ticket:**

```bash

- **Issues**: Check logs with `sudo docker compose logs [service]`curl -X POST http://localhost:9000/business \

- **Health**: Run `./scripts/check_health.sh`  -H "Content-Type: application/json" \

- **Documentation**: See `docs/` folder  -d '{

- **Tests**: Run `./venv/bin/python tests/test_complete_system.py`    "requestId":"booking-123",

    "payload":{

---      "type":"book_seat",

      "data":{"movie":"Inception","city":"Delhi","seats":2}

## 🎬 You're Ready!    },

    "context":{"token":"your-auth-token"}

Your distributed movie booking system is production-ready with:  }'

- ✓ Persistent database```

- ✓ Fault-tolerant Raft cluster  

- ✓ AI-powered assistant### Raft Nodes (`:50051-50053`)

- ✓ Multi-user support

- ✓ Complete test coverage| Method | Endpoint             | Description                     | Auth Required |

- ✓ One-command deployment|--------|----------------------|---------------------------------|---------------|

| GET    | `/status`            | Node status & leader info       | No            |

**Start now:** `./quickstart.sh`| POST   | `/trigger-election`  | Trigger leader election         | No            |



---**Example - Check Cluster Status:**

```bash

*Built with FastAPI, Raft Consensus, Qwen2.5-0.5B, Docker, and ❤️*curl http://localhost:50051/status

# Response: {"node_id":"node1","state":"leader","term":2,...}
```

### LLM Server (`:8500`)

| Method | Endpoint   | Description            | Auth Required |
|--------|------------|------------------------|---------------|
| GET    | `/health`  | Health & model status  | No            |
| POST   | `/ask`     | Quick FAQ question     | No            |
| POST   | `/chat`    | Conversational AI      | No            |

**Example - Ask FAQ:**
```bash
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I book a ticket?"}'
```

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
./scripts/check_health.sh
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

