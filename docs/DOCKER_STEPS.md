# 🐳 Docker Setup - Step by Step Guide

Complete guide to run all Docker services for the Distributed Movie Booking System.

## 📋 Prerequisites Check

**Step 1: Verify Docker Installation**
```bash
docker --version
docker compose version
```

**Step 2: Ensure you're in the project directory**
```bash
cd /path/to/ds
# Or: cd "C:\Users\utkarsh\Desktop\New folder (3)\ds"
```

---

## 🎯 Two Usage Methods

This system supports two Docker setups:

| Method | Docker File | Interface | Use Case |
|--------|-------------|-----------|----------|
| **Method 1** | `docker-compose.yml` | Desktop GUI (CustomTkinter) | Local development |
| **Method 2** | `docker-compose.combined.yml` | Web UI (Browser) | Production, remote access |

---

## 📱 Method 1: Standard Docker (for Desktop GUI)

### Quick Start

```bash
# Start backend services
docker compose up -d --build

# Then launch GUI locally
pip install -r requirements-app.txt
python app.py              # Single window
python app_multi.py        # Multi window
```

---

## 🌐 Method 2: Combined Docker (for Web UI)

### Quick Start

```bash
# Start all services including web frontend
docker compose -f docker-compose.combined.yml up -d --build

# Access at http://localhost:3000
```

---

## 🛠️ Manual Step-by-Step (Both Methods)

### Method 1: Standard Docker (Desktop GUI)

**Step 1: Build Docker Images**
```bash
docker compose build
```

**Step 2: Start Backend Services**
```bash
docker compose up -d
```

**Step 3: Launch Desktop GUI (locally)**
```bash
pip install -r requirements-app.txt
python app.py              # Single window
python app_multi.py        # Multi window
```

### Method 2: Combined Docker (Web UI)

**Step 1: Build Combined Image**
```bash
docker compose -f docker-compose.combined.yml build
```

**Step 2: Start All Services**
```bash
docker compose -f docker-compose.combined.yml up -d
```

**Step 3: Access Web UI**
```
Open browser: http://localhost:3000
```

### Start Specific Services Only

**Method 1 (without LLM):**
```bash
docker compose up -d app-server raft-node1 raft-node2 raft-node3
```

**Method 2 (without LLM):**
```bash
docker compose -f docker-compose.combined.yml up -d movie-booking-app raft-node1 raft-node2 raft-node3
```

### Step 3: Verify Services Are Running

**Method 1: Check container status**
```bash
docker compose ps
```

**Method 2: Check container status**
```bash
docker compose -f docker-compose.combined.yml ps
```

**Expected output (Method 1):**
```
NAME                STATUS          PORTS
movie-app-server    Up X minutes     0.0.0.0:9000->9000/tcp
raft-node1          Up X minutes    0.0.0.0:50051->50051/tcp
raft-node2          Up X minutes    0.0.0.0:50052->50052/tcp
raft-node3          Up X minutes    0.0.0.0:50053->50053/tcp
movie-llm-server    Up X minutes    0.0.0.0:8500->8500/tcp
```

**Expected output (Method 2):**
```
NAME                    STATUS          PORTS
movie-booking-combined  Up X minutes    0.0.0.0:9000->9000/tcp, 0.0.0.0:3000->3000/tcp
raft-node1              Up X minutes    0.0.0.0:50051->50051/tcp
raft-node2              Up X minutes    0.0.0.0:50052->50052/tcp
raft-node3              Up X minutes    0.0.0.0:50053->50053/tcp
movie-llm-server        Up X minutes    0.0.0.0:8500->8500/tcp
```

**Check resource usage:**
```bash
sudo docker stats
```

**Run health check script:**
```bash
./scripts/check_health.sh
```

### Step 4: View Logs

**Method 1: View logs**
```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f app-server
docker compose logs -f raft-node1
docker compose logs -f llm-server

# View last 50 lines
docker compose logs --tail=50 [service-name]
```

**Method 2: View logs**
```bash
# View all logs
docker compose -f docker-compose.combined.yml logs -f

# View combined app logs (frontend + backend)
docker compose -f docker-compose.combined.yml logs -f movie-booking-app

# View last 50 lines
docker compose -f docker-compose.combined.yml logs --tail=50 movie-booking-app
```

---

## 🔍 Service Verification

### Step 1: Test Application Server (Port 9000)

```bash
# Health check
curl http://localhost:9000/health

# Test login
curl -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}'
```

### Step 2: Test Frontend (Method 2 Only)

```bash
# Check web frontend
curl http://localhost:3000

# Or open in browser: http://localhost:3000
```

### Step 3: Test Raft Nodes (Ports 50051-50053)

```bash
# Check node 1 status
curl http://localhost:50051/status

# Check node 2 status
curl http://localhost:50052/status

# Check node 3 status
curl http://localhost:50053/status

# Check all at once
for PORT in 50051 50052 50053; do 
  echo "=== Node on port $PORT ==="
  curl http://localhost:$PORT/status
  echo ""
done
```

### Step 4: Test LLM Server (Port 8500)

```bash
# Health check
curl http://localhost:8500/health

# Test FAQ
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I book a ticket?"}'
```

---

## 🛑 Stopping Services

### Method 1: Standard Docker

```bash
# Stop all services
docker compose down

# Stop specific service
docker compose stop app-server
docker compose stop llm-server

# Stop and remove containers (keeps images)
docker compose down

# Stop and remove everything (containers + volumes)
docker compose down -v
```

### Method 2: Combined Docker

```bash
# Stop all services
docker compose -f docker-compose.combined.yml down

# Stop specific service
docker compose -f docker-compose.combined.yml stop movie-booking-app

# Stop and remove containers (keeps images)
docker compose -f docker-compose.combined.yml down

# Stop and remove everything (containers + volumes)
docker compose -f docker-compose.combined.yml down -v
```

---

## 🔄 Restarting Services

### Method 1: Standard Docker

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart app-server
docker compose restart raft-node1

# Rebuild and restart (after code changes)
docker compose build app-server --no-cache
docker compose up -d app-server
```

### Method 2: Combined Docker

```bash
# Restart all services
docker compose -f docker-compose.combined.yml restart

# Restart specific service
docker compose -f docker-compose.combined.yml restart movie-booking-app

# Rebuild and restart (after code changes)
docker compose -f docker-compose.combined.yml build --no-cache movie-booking-app
docker compose -f docker-compose.combined.yml up -d movie-booking-app
```

---

## 🧹 Cleanup Commands

### Method 1: Standard Docker

```bash
# Remove all containers and volumes
docker compose down -v

# Remove all images
docker compose down --rmi all

# Complete cleanup (containers + volumes + images)
docker compose down -v --rmi all
```

### Method 2: Combined Docker

```bash
# Remove all containers and volumes
docker compose -f docker-compose.combined.yml down -v

# Remove all images
docker compose -f docker-compose.combined.yml down --rmi all

# Complete cleanup (containers + volumes + images)
docker compose -f docker-compose.combined.yml down -v --rmi all
```

### System Prune (removes unused Docker resources)
```bash
docker system prune -a
```

---

## 🔧 Troubleshooting Commands

### Method 1: Standard Docker

```bash
# Check service status
docker compose ps

# View recent logs
docker compose logs --tail=50 [service-name]

# Rebuild without cache
docker compose build --no-cache [service-name]
docker compose up -d [service-name]
```

### Method 2: Combined Docker

```bash
# Check service status
docker compose -f docker-compose.combined.yml ps

# View recent logs
docker compose -f docker-compose.combined.yml logs --tail=50 movie-booking-app

# Rebuild without cache
docker compose -f docker-compose.combined.yml build --no-cache movie-booking-app
docker compose -f docker-compose.combined.yml up -d movie-booking-app
```

### Check Port Usage
```bash
# Linux/Mac
sudo lsof -i :9000
sudo lsof -i :8500

# Windows PowerShell
netstat -ano | findstr :9000
```

### Kill Process Using Port (Linux/Mac)
```bash
sudo kill -9 <PID>
```

### Restart Docker Service (if needed)
```bash
# Linux
sudo systemctl restart docker

# Mac
# Restart Docker Desktop from Applications
```

---

## 📊 Service Ports Reference

| Service      | Container Name      | Port  | Health Check                    |
|--------------|---------------------|-------|---------------------------------|
| app-server   | movie-app-server    | 9000  | http://localhost:9000/health    |
| raft-node1   | raft-node1          | 50051 | http://localhost:50051/status  |
| raft-node2   | raft-node2          | 50052 | http://localhost:50052/status  |
| raft-node3   | raft-node3          | 50053 | http://localhost:50053/status  |
| llm-server  | movie-llm-server    | 8500  | http://localhost:8500/health    |

---

## 🎯 Common Workflows

### Method 1: First Time Setup (Desktop GUI)

```bash
# 1. Build images
docker compose build

# 2. Start backend services
docker compose up -d

# 3. Install GUI dependencies
pip install -r requirements-app.txt

# 4. Launch GUI
python app.py              # Single window
python app_multi.py        # Multi window

# 5. Check status
docker compose ps
```

### Method 2: First Time Setup (Web UI)

```bash
# 1. Build images
docker compose -f docker-compose.combined.yml build

# 2. Start all services
docker compose -f docker-compose.combined.yml up -d

# 3. Wait for services (especially LLM - takes 30-60s)
sleep 10

# 4. Check status
docker compose -f docker-compose.combined.yml ps

# 5. Access web UI
# Open browser: http://localhost:3000
```

### After Code Changes

**Method 1:**
```bash
# Rebuild and restart backend
docker compose build app-server --no-cache
docker compose up -d app-server

# Check logs
docker compose logs -f app-server
```

**Method 2:**
```bash
# Rebuild and restart combined app
docker compose -f docker-compose.combined.yml build --no-cache movie-booking-app
docker compose -f docker-compose.combined.yml up -d movie-booking-app

# Check logs
docker compose -f docker-compose.combined.yml logs -f movie-booking-app
```

### Daily Development

**Method 1:**
```bash
# Start backend
docker compose up -d

# Launch GUI
python app.py

# Stop when done
docker compose down
```

**Method 2:**
```bash
# Start everything
docker compose -f docker-compose.combined.yml up -d

# Access at http://localhost:3000

# Stop when done
docker compose -f docker-compose.combined.yml down
```

### Production Deployment

**Method 1:**
```bash
git pull
docker compose build
docker compose up -d
./scripts/check_health.sh
```

**Method 2:**
```bash
git pull
docker compose -f docker-compose.combined.yml build
docker compose -f docker-compose.combined.yml up -d
curl http://localhost:9000/health
curl http://localhost:3000
```

---

## ⚠️ Important Notes

1. **First Run**: LLM server takes 30-60 seconds to download and load the model (~1GB)
2. **Memory**: LLM server requires 2-4GB RAM. Skip it if low on resources:
   - **Method 1**: `docker compose up -d app-server raft-node1 raft-node2 raft-node3`
   - **Method 2**: `docker compose -f docker-compose.combined.yml up -d movie-booking-app raft-node1 raft-node2 raft-node3`
3. **Ports**: 
   - **Method 1**: Ensure ports 9000, 50051-50053, 8500 are not in use
   - **Method 2**: Ensure ports 3000, 9000, 50051-50053, 8500 are not in use
4. **Permissions**: On Linux, you may need `sudo` for Docker commands
5. **Networks**: All services communicate via `movie-booking-network` bridge network
6. **Method 1** requires Python and GUI dependencies installed locally
7. **Method 2** only requires Docker - frontend runs in container

---

## ✅ Quick Verification Checklist

### Method 1: Desktop GUI

After starting services, verify:

- [ ] All containers are running: `docker compose ps`
- [ ] App server responds: `curl http://localhost:9000/health`
- [ ] Raft nodes respond: `curl http://localhost:50051/status`
- [ ] LLM server responds: `curl http://localhost:8500/health` (if running)
- [ ] GUI launches: `python app.py` or `python app_multi.py`

### Method 2: Web UI

After starting services, verify:

- [ ] All containers are running: `docker compose -f docker-compose.combined.yml ps`
- [ ] App server responds: `curl http://localhost:9000/health`
- [ ] Web frontend responds: `curl http://localhost:3000`
- [ ] Raft nodes respond: `curl http://localhost:50051/status`
- [ ] LLM server responds: `curl http://localhost:8500/health` (if running)
- [ ] Web UI loads in browser: http://localhost:3000

---

## 🆘 If Something Goes Wrong

1. **Check logs**: `sudo docker compose logs [service-name]`
2. **Restart service**: `sudo docker compose restart [service-name]`
3. **Rebuild service**: `sudo docker compose build --no-cache [service-name]`
4. **Clean restart**: `sudo docker compose down -v && sudo docker compose up -d`
5. **Check Docker**: `sudo docker ps -a` and `sudo docker images`

---

**Ready to use!** Once services are running, access:
- **Web UI**: `http://localhost:8080` (after running `cd web && python3 -m http.server 8080`)
- **API**: `http://localhost:9000`
- **LLM**: `http://localhost:8500`


