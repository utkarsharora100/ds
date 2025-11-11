# 🎬 Distributed Movie Booking System# Distributed Movie Booking System



A production-ready distributed movie ticket booking system with **Raft consensus**, **FastAPI backend**, and **AI-powered support** using Qwen2.5-0.5B.A distributed movie ticket booking system with **Raft consensus**, **FastAPI backend**, **Qwen2.5 AI assistant**, and complete **Docker orchestration**.



## ✨ Features## 🎯 Overview



- **🔄 Distributed Consensus**: Raft protocol with automatic leader electionProduction-ready distributed system demonstrating:

- **🤖 AI Assistant**: Qwen2.5-0.5B model for booking support and FAQs

- **🚀 Microservices**: FastAPI application server with RESTful APIs- **Raft Consensus Protocol**: 3-node cluster with automatic leader election and log replication

- **💾 Data Persistence**: SQLite with user sessions and booking management- **FastAPI Application Server**: RESTful API for user authentication, movie management, and bookings

- **🐳 Docker Ready**: One command deployment with docker-compose- **AI Assistant**: Qwen2.5-0.5B (500M parameters) for conversational support and FAQs

- **📊 Health Monitoring**: Built-in health checks for all services- **Docker Orchestration**: Complete containerized deployment with one command

- **Health Monitoring**: Built-in health checks and status endpoints for all services

---- **Distributed Architecture**: Microservices pattern with inter-service communication



## 🚀 Quick Start (3 Steps)## 📁 Project Structure



### Prerequisites```

- Docker & Docker Compose installedds/

- 6GB RAM minimum (for LLM server)├── 🐳 Docker Configuration

- 10GB free disk space│   ├── docker-compose.yml         # Service orchestration

│   ├── Dockerfile.app             # Application server image

### Start the System│   ├── Dockerfile.raft            # Raft nodes image

│   ├── Dockerfile.llm             # LLM server image

```bash│   └── .dockerignore              # Build optimization

# 1. Clone or navigate to the project│

cd /home/aniket/study/ds├── 🚀 Application Code

│   ├── Application_server/

# 2. Start all services│   │   └── Application_server.py  # FastAPI backend (port 9000)

docker-compose up -d│   ├── raft/

│   │   ├── raft_node.py           # Raft implementation

# 3. Wait 30-60 seconds, then check health│   │   └── raft_state.py          # State management

curl http://localhost:9000/health│   ├── llm/

curl http://localhost:8500/health│   │   ├── llm_server.py          # Qwen2.5 AI server (port 8500)

```│   │   └── storage.py             # SQLite functions

│   ├── proto/

**That's it!** 🎉 All services are now running.│   │   ├── raft.proto             # gRPC definitions

│   │   └── raft_pb2*.py           # Generated code

---│   └── main.py                    # Raft node launcher

│

## 📊 System Architecture├── 🧪 Testing & Scripts

│   ├── test_llm.py                # LLM test suite

```│   ├── check_health.sh            # Health check script

┌─────────────────────────────────────────────────┐│   └── client/client.py           # Load testing client

│           Docker Network (movie-booking-net)     ││

├─────────────────────────────────────────────────┤├── 📚 Documentation

│                                                  ││   ├── README.md                  # This file

│  ┌──────────────┐        ┌──────────────┐      ││   ├── QUICKSTART.md              # 2-minute setup

│  │ App Server   │        │ LLM Server   │      ││   ├── DOCKER.md                  # Complete Docker guide

│  │ Port: 9000   │        │ Port: 8500   │      ││   ├── LLM_TESTING.md             # AI assistant guide

│  │ (FastAPI)    │        │ (Qwen2.5)    │      ││   ├── QUICK_REFERENCE.md         # Command cheat sheet

│  └──────────────┘        └──────────────┘      ││   └── ARCHITECTURE.md            # System design

│                                                  ││

│  ┌────────┐  ┌────────┐  ┌────────┐           │└── ⚙️ Configuration

│  │ Raft-1 │  │ Raft-2 │  │ Raft-3 │           │    ├── requirements.txt           # Python dependencies

│  │ :50051 │  │ :50052 │  │ :50053 │           │    ├── .env                       # Environment variables

│  └────────┘  └────────┘  └────────┘           │    └── .env.example               # Config template

│                                                  │```

└─────────────────────────────────────────────────┘

```## 🛠️ Prerequisites



**Services:****Only Docker is required!**

- **Application Server** (9000): User auth, booking, movie management

- **Raft Nodes** (50051-53): Distributed consensus cluster- **Docker**: Version 20.10+

- **LLM Server** (8500): AI assistant with Qwen2.5-0.5B- **Docker Compose**: Version 2.0+

- **System Requirements**: 6GB RAM, 10GB disk space

---

### Check Installation

## 🧪 Testing the System

```bash

### Check All Servicesdocker --version

docker-compose --version

```bash```

# Application Server

curl http://localhost:9000/health### Install Docker (if needed)



# Raft Nodes (one will be leader)**Linux:**

curl http://localhost:50051/status```bash

curl http://localhost:50052/statuscurl -fsSL https://get.docker.com -o get-docker.sh

curl http://localhost:50053/statussudo sh get-docker.sh

```

# LLM Server

curl http://localhost:8500/health**macOS/Windows:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

```

## 🚀 Quick Start (2 Commands!)

### Test Login

### Start Everything

```bash

curl -X POST http://localhost:9000/login \```bash

  -H "Content-Type: application/json" \# 1. Start all services

  -d '{"username": "admin", "password": "123"}'docker-compose up -d

```

# 2. Check health (optional)

**Default Credentials:**./check_health.sh

- Username: `admin` / Password: `123````

- Username: `utkarsh` / Password: `password123`

**That's it!** All services are now running:

### Test AI Assistant- ✅ Application Server → http://localhost:9000

- ✅ Raft Nodes → http://localhost:50051-50053

```bash- ✅ AI Assistant → http://localhost:8500

# Ask a question

curl -X POST http://localhost:8500/ask \### Test the System

  -H "Content-Type: application/json" \

  -d '{"question": "How do I book a ticket?"}'```bash

# Test application server

# Chat modecurl http://localhost:9000/health

curl -X POST http://localhost:8500/chat \

  -H "Content-Type: application/json" \# Check Raft leader

  -d '{curl http://localhost:50051/status | grep leader

    "messages": [

      {"role": "user", "content": "I want to book a movie"}# Ask the AI a question

    ]curl -X POST http://localhost:8500/ask \

  }'  -H "Content-Type: application/json" \

```  -d '{"question": "How do I book a ticket?"}'

```

### Run Automated Tests

### View Logs

```bash

# Test LLM server```bash

python test_llm.py# All services

docker-compose logs -f

# Check all services health

./check_health.sh# Specific service

```docker-compose logs -f llm-server

```

---

### Stop Everything

## 🐳 Docker Commands

```bash

### Basic Operationsdocker-compose down

```

```bash

# Start all services---

docker-compose up -d

## 📊 System Architecture

# View logs

docker-compose logs -f```

┌─────────────────────────────────────────────────────┐

# Stop all services│               Docker Network                         │

docker-compose down│           (movie-booking-net)                        │

├─────────────────────────────────────────────────────┤

# Restart specific service│                                                      │

docker-compose restart llm-server│  ┌──────────────┐         ┌──────────────┐         │

│  │  app-server  │         │  llm-server  │         │

# Check service status│  │  Port: 9000  │         │  Port: 8500  │         │

docker-compose ps│  │   FastAPI    │         │  Qwen2.5-0.5B│         │

```│  └──────────────┘         └──────────────┘         │

│                                                      │

### Without LLM (Faster, Less Memory)│  ┌────────┐     ┌────────┐     ┌────────┐         │

│  │ raft-  │◄───►│ raft-  │◄───►│ raft-  │         │

```bash│  │ node1  │     │ node2  │     │ node3  │         │

# Start only core services│  │ :50051 │     │ :50052 │     │ :50053 │         │

docker-compose up -d app-server raft-node1 raft-node2 raft-node3│  └────────┘     └────────┘     └────────┘         │

```│       Leader Election & Consensus                   │

└─────────────────────────────────────────────────────┘

### Troubleshooting```



```bash---

# View logs for specific service

docker-compose logs -f app-server## 📋 API Endpoints



# Rebuild service### Application Server (port 9000)

docker-compose build --no-cache llm-server

#### Step 1: Start the Application Server

# Clean restart

docker-compose down -vOpen a **new terminal** and run:

docker-compose up -d

``````bash

cd /home/aniket/study/ds

---python Application_server/Application_server.py

```

## 📁 Project Structure

**Expected Output:**

``````

ds/[SERVER] ✅ Application Server initialized.

├── docker-compose.yml          # Service orchestrationINFO:     Started server process

├── .env                        # Environment variablesINFO:     Uvicorn running on http://127.0.0.1:9000

├── requirements.txt            # Python dependencies```

│

├── Dockerfile.app              # Application server image**Keep this terminal running.**

├── Dockerfile.raft             # Raft node image

├── Dockerfile.llm              # LLM server image---

│

├── Application_server/         # FastAPI backend#### Step 2: Launch the GUI Application

│   └── Application_server.py

├── raft/                       # Raft consensus implementationOpen **another terminal** and run:

│   ├── raft_node.py

│   └── raft_state.py```bash

├── llm/                        # AI assistant servercd /home/aniket/study/ds

│   ├── llm_server.py          # Qwen2.5-0.5B integrationpython app.py

│   └── storage.py             # Database functions```

├── client/                     # Client simulator

│   └── client.py**Expected Result:**

├── proto/                      # gRPC definitions- A dark-themed GUI window will open titled **"Distributed Movie Booking System"**

│   └── raft.proto- You'll see the login page with options to start Raft nodes

│

├── test_llm.py                # LLM test suite---

├── check_health.sh            # Health check script

│#### Step 3: Start Raft Nodes from GUI

└── docs/                      # Documentation

    ├── QUICKSTART.mdOn the login screen, you'll see three buttons:

    ├── DOCKER.md1. Click **"Start Node 1"** → Indicator turns 🟢 (green)

    ├── LLM_TESTING.md2. Click **"Start Node 2"** → Indicator turns 🟢

    └── ARCHITECTURE.md3. Click **"Start Node 3"** → Indicator turns 🟢

```

**What happens:**

---- Each click spawns a new terminal running a Raft node

- Nodes will elect a leader automatically within 5-8 seconds

## 🔌 API Endpoints- Check the node terminal windows to see leader election logs



### Application Server (`:9000`)---



| Method | Endpoint | Description |#### Step 4: Login to the System

|--------|----------|-------------|

| GET | `/health` | Health check |**Default Credentials:**

| POST | `/register` | Register new user |- **Username:** `admin`

| POST | `/login` | User login |- **Password:** `123`

| GET | `/data/{type}` | Get movies/bookings |

| POST | `/business` | Book tickets |Click **"Login"** button.

| POST | `/add_movie` | Add movie (admin) |

---

### Raft Nodes (`:50051-50053`)

#### Step 5: Admin Dashboard Features

| Method | Endpoint | Description |

|--------|----------|-------------|After login, you can:

| GET | `/status` | Node status & leader info |

| POST | `/trigger-election` | Trigger leader election |1. **Add Movies:**

   - Enter movie name in the text field

### LLM Server (`:8500`)   - Click "Add Movie"



| Method | Endpoint | Description |2. **Simulate Multiple Clients:**

|--------|----------|-------------|   - Click "Simulate Multiple Clients (5 users booking)"

| GET | `/health` | Health & model status |   - This spawns 5 concurrent booking requests

| POST | `/ask` | Quick FAQ question |

| POST | `/chat` | Conversational AI |3. **Test Database Consistency:**

   - Click "Test Database Consistency (Raft Verification)"

---   - Checks if Raft leader is elected and system is healthy



## ⚙️ Configuration---



Environment variables in `.env`:### **Option B: Manual Command-Line Execution**



```bash#### Step 1: Start Application Server

# Application Server

APP_SERVER_HOST=0.0.0.0```bash

APP_SERVER_PORT=9000cd /home/aniket/study/ds

python Application_server/Application_server.py

# LLM Configuration```

LLM_MODEL=Qwen/Qwen2.5-0.5B

LLM_MAX_NEW_TOKENS=512---

LLM_TEMPERATURE=0.7

#### Step 2: Start Raft Nodes (3 separate terminals)

# Raft Nodes

RAFT_NODE1_PORT=50051**Terminal 1 - Node 1:**

RAFT_NODE2_PORT=50052```bash

RAFT_NODE3_PORT=50053cd /home/aniket/study/ds

python main.py node1

# Docker Mode```

DOCKER_ENV=true

```**Terminal 2 - Node 2:**

```bash

### Customize LLM Behaviorcd /home/aniket/study/ds

python main.py node2

Edit `.env` file:```



```bash**Terminal 3 - Node 3:**

# Use different model```bash

LLM_MODEL=Qwen/Qwen2.5-1.5Bcd /home/aniket/study/ds

python main.py node3

# Shorter responses```

LLM_MAX_NEW_TOKENS=256

**Expected Output (from one of the nodes):**

# More focused (less creative)```

LLM_TEMPERATURE=0.3[node2] 🏆 is the LEADER now (term 1)

```INFO:     Uvicorn running on http://0.0.0.0:50052

```

---

---

## 🔍 Monitoring & Logs

#### Step 3: (Optional) Start LLM Server

### View Logs

```bash

```bashcd /home/aniket/study/ds

# All servicespython -m uvicorn llm.llm_server:app --host 0.0.0.0 --port 8500

docker-compose logs -f```



# Specific service**Note:** First run will download the model (~500MB). This may take a few minutes.

docker-compose logs -f llm-server

**Expected Output:**

# Last 100 lines```

docker-compose logs --tail=100Loading local LLM model... (this may take ~30 seconds the first time)

INFO:     Uvicorn running on http://0.0.0.0:8500

# With timestamps```

docker-compose logs -t

```---



### Resource Usage#### Step 4: Run Client Simulation



```bash```bash

# Real-time statscd /home/aniket/study/ds

docker statspython client/client.py

```

# Service status

docker-compose ps**Expected Output:**

``````

[CLIENT-user_1234] ✅ Logged in. Token = abc123...

### Health Checks[CLIENT-user_1234] Booking result → {'status': 'success', 'booking_id': '...'}

```

```bash

# Quick check all services---

./check_health.sh

## 🧪 Testing

# Manual checks

curl http://localhost:9000/health### Test Raft Node Status

curl http://localhost:8500/health

curl http://localhost:50051/statusCheck if nodes are running and identify the leader:

```

```bash

---# Check Node 1

curl http://0.0.0.0:50051/status

## 🐛 Troubleshooting

# Check Node 2

### Services Won't Startcurl http://0.0.0.0:50052/status



```bash# Check Node 3

# Check logscurl http://0.0.0.0:50053/status

docker-compose logs```



# Rebuild images**Example Response:**

docker-compose build --no-cache```json

{

# Clean start  "node_id": "node2",

docker-compose down -v  "state": "leader",

docker system prune -a  "term": 1,

docker-compose up -d  "leader_id": "node2",

```  "peers": ["node1", "node3"]

}

### Port Already in Use```



```bash---

# Find process using port

lsof -i :9000### Test Application Server Endpoints



# Kill process**Register a User:**

kill -9 <PID>```bash

curl -X POST http://127.0.0.1:9000/register \

# Or change port in docker-compose.yml  -H "Content-Type: application/json" \

```  -d '{"username": "testuser", "password": "pass123"}'

```

### LLM Server Out of Memory

**Login:**

```bash```bash

# Option 1: Increase Docker memory to 6GB+curl -X POST http://127.0.0.1:9000/login \

  -H "Content-Type: application/json" \

# Option 2: Run without LLM  -d '{"username": "testuser", "password": "pass123"}'

docker-compose up -d app-server raft-node1 raft-node2 raft-node3```

```

**Response:**

### Slow LLM Responses```json

{

This is normal on CPU (2-5 seconds). To improve:  "status": "success",

  "token": "a1b2c3d4...",

```bash  "user": "testuser"

# Edit .env}

LLM_MAX_NEW_TOKENS=256     # Shorter responses```

LLM_TEMPERATURE=0.3         # More focused

```**Add a Movie (Admin):**

```bash

### Raft Leader Not Electedcurl -X POST http://127.0.0.1:9000/add_movie \

  -H "Content-Type: application/json" \

```bash  -d '{"token": "<your_token>", "movie": "Inception", "city": "Mumbai"}'

# Restart Raft nodes```

docker-compose restart raft-node1 raft-node2 raft-node3

---

# Wait 5-8 seconds for election

sleep 8### Test LLM Server (if running)



# Check leader**Ask a Question:**

curl http://localhost:50051/status | grep leader```bash

```curl -X POST http://0.0.0.0:8500/ask \

  -H "Content-Type: application/json" \

---  -d '{"question": "How do I cancel my booking?"}'

```

## 📚 Documentation

**Response:**

| Document | Description |```json

|----------|-------------|{

| **[QUICKSTART.md](QUICKSTART.md)** | Fastest way to get started |  "answer": "Cancellations are allowed up to one hour before the showtime",

| **[DOCKER.md](DOCKER.md)** | Complete Docker guide |  "confidence": 0.89

| **[LLM_TESTING.md](LLM_TESTING.md)** | AI assistant testing guide |}

| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System design details |```

| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | Command cheat sheet |

---

---

## 🔧 Configuration

## 🎯 Common Use Cases

### Raft Node Ports

### Development Workflow

Defined in `main.py`:

```bash- **Node 1**: `localhost:50051`

# Make code changes- **Node 2**: `localhost:50052`

vim Application_server/Application_server.py- **Node 3**: `localhost:50053`



# Rebuild and restart### Application Server

docker-compose build app-server

docker-compose up -d app-server- **Host**: `127.0.0.1`

- **Port**: `9000`

# Check logs

docker-compose logs -f app-server### LLM Server

```

- **Host**: `0.0.0.0`

### Testing Workflow- **Port**: `8500`



```bash### Default Users

# Start services

docker-compose up -dDefined in `Application_server/Application_server.py`:

- **Username**: `admin`, **Password**: `123`

# Run tests- **Username**: `utkarsh`, **Password**: `password123`

python test_llm.py

---

# Check health

./check_health.sh## 🐛 Troubleshooting



# Stop services### Issue: "Module not found" errors

docker-compose down

```**Solution:**

```bash

### Production Deployment# Make sure you're in the project root

cd /home/aniket/study/ds

```bash

# Pull latest code# Install missing packages

git pullpip install <package-name>

```

# Build images

docker-compose build---



# Start with restart policy### Issue: Ports already in use

docker-compose up -d

**Solution:**

# Monitor```bash

docker-compose logs -f# Kill processes using ports

```lsof -ti:9000 | xargs kill -9   # Application server

lsof -ti:50051 | xargs kill -9  # Node 1

---lsof -ti:50052 | xargs kill -9  # Node 2

lsof -ti:50053 | xargs kill -9  # Node 3

## 🔐 Security Noteslsof -ti:8500 | xargs kill -9   # LLM server

```

**⚠️ Current Setup: Development Mode**

---

For production, implement:

- [ ] HTTPS/TLS certificates### Issue: GUI not opening

- [ ] Strong password hashing

- [ ] JWT authentication**Solution:**

- [ ] Rate limiting- Make sure you have a display server running (X11 on Linux, not WSL without X server)

- [ ] Input validation- Install tkinter if missing:

- [ ] CORS restrictions  ```bash

- [ ] Environment secrets management  # Ubuntu/Debian

  sudo apt-get install python3-tk

---  

  # Fedora

## 📈 Performance  sudo dnf install python3-tkinter

  ```

### Resource Requirements

---

| Service | Memory | CPU | Startup Time |

|---------|--------|-----|--------------|### Issue: LLM model download fails

| App Server | 200MB | Low | 5s |

| Raft Node (×3) | 100MB each | Low | 5s |**Solution:**

| LLM Server | 2-4GB | Medium | 30-60s |- Check internet connection

- Manually download model:

### Response Times  ```python

  from transformers import pipeline

| Operation | Expected Time |  pipeline("question-answering", model="deepset/roberta-base-squad2")

|-----------|---------------|  ```

| Login/Register | <50ms |

| Book Ticket | <200ms |---

| Raft Status | <100ms |

| LLM FAQ | 2-5s (CPU) |### Issue: Raft nodes not electing leader

| LLM Chat | 3-7s (CPU) |

**Solution:**

---- Ensure all 3 nodes are running

- Check node terminals for error messages

## 🆘 Getting Help- Restart all nodes simultaneously

- Election should occur within 5-8 seconds

### Quick Diagnostics

---

```bash

# Check if Docker is running## 📊 System Flow

docker info

```

# Check services┌─────────────┐

docker-compose ps│   GUI App   │ (app.py)

└──────┬──────┘

# View all logs       │

docker-compose logs --tail=50       ├─────→ Starts Raft Nodes (main.py)

       │       ├─ Node 1 (50051)

# Run health check       │       ├─ Node 2 (50052)

./check_health.sh       │       └─ Node 3 (50053)

```       │

       └─────→ Communicates with Application Server

### Common Issues               │

               ├─ User Authentication

1. **"Port already in use"** → Kill process or change port               ├─ Movie Management

2. **"Out of memory"** → Increase Docker memory or skip LLM               └─ Booking Operations

3. **"Connection refused"** → Check service is running                       │

4. **"Model not loading"** → Check LLM server logs                       └─→ Stores in SQLite (storage.py)

```

---

---

## 🎓 Learning Resources

## 🎓 Key Features Demonstrated

- [Raft Consensus Algorithm](https://raft.github.io/)

- [FastAPI Documentation](https://fastapi.tiangolo.com/)1. **Distributed Consensus**: Raft algorithm implementation with leader election

- [Docker Compose Guide](https://docs.docker.com/compose/)2. **Fault Tolerance**: System continues operating if minority of nodes fail

- [Qwen2.5 Model](https://huggingface.co/Qwen/Qwen2.5-0.5B)3. **RESTful APIs**: FastAPI for modern async HTTP endpoints

4. **gRPC Communication**: Inter-node communication using Protocol Buffers

---5. **Client-Server Architecture**: Separation of concerns with modular design

6. **GUI Development**: Modern desktop application with CustomTkinter

## 🚀 Quick Command Reference7. **Machine Learning Integration**: Local LLM for FAQ assistance

8. **Database Management**: SQLite with user sessions and booking state

```bash

# Start everything---

docker-compose up -d

## 📝 Notes

# Check health

./check_health.sh- **First-time LLM setup** may take time due to model download (~500MB)

- **Raft nodes** should be started before heavy client load

# Test LLM- **Admin operations** require proper authentication token

python test_llm.py- **Election timeout** is randomized between 5-8 seconds to avoid split votes

- **In-memory database** resets on application server restart

# View logs

docker-compose logs -f---



# Stop everything## 🤝 Contributing

docker-compose down

Feel free to extend this project with:

# Clean restart- Persistent storage (PostgreSQL/MySQL)

docker-compose down -v && docker-compose up -d- Payment gateway integration

```- Real-time seat availability updates

- Email notifications

---- Mobile client application



## 📝 License---



Educational project for distributed systems learning.## 📄 License



---This is an educational project for distributed systems learning.



## 👥 Authors---



Aniket & Team  ## 👨‍💻 Author

Repository: [utkarsharora100/ds](https://github.com/utkarsharora100/ds)

Aniket & Team

---Repository: utkarsharora100/ds



**🎉 Ready to go! Just run:** `docker-compose up -d`---


## 📚 References

- [Raft Consensus Algorithm](https://raft.github.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [gRPC Python Guide](https://grpc.io/docs/languages/python/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)

---

**Happy Coding! 🚀**
