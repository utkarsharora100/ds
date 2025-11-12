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

## 🚀 Method 1: Quick Start (Recommended)

**Step 1: Make scripts executable (one-time, Linux/Mac)**
```bash
chmod +x quickstart.sh
chmod +x scripts/*.sh
```

**Step 2: Run the quickstart script**
```bash
./quickstart.sh
```

This script will:
- Build all Docker images
- Start all services
- Run health checks
- Display status

*Note: First run takes ~10 minutes due to image builds and LLM model download (~1GB)*

---

## 🛠️ Method 2: Manual Step-by-Step

### Step 1: Build Docker Images

Build all services:
```bash
sudo docker compose build
```

Or build individual services:
```bash
sudo docker compose build app-server
sudo docker compose build raft-node1
sudo docker compose build raft-node2
sudo docker compose build raft-node3
sudo docker compose build llm-server
```

### Step 2: Start All Services

**Start all services in detached mode:**
```bash
sudo docker compose up -d
```

**Start with logs visible:**
```bash
sudo docker compose up
```
(Press `Ctrl+C` to stop, but containers will keep running)

**Start specific services only:**
```bash
# Without LLM (lower resource usage)
sudo docker compose up -d app-server raft-node1 raft-node2 raft-node3

# Only application server
sudo docker compose up -d app-server

# Only Raft nodes
sudo docker compose up -d raft-node1 raft-node2 raft-node3
```

### Step 3: Verify Services Are Running

**Check container status:**
```bash
sudo docker compose ps
```

**Expected output:**
```
NAME                STATUS          PORTS
movie-app-server    Up X minutes     0.0.0.0:9000->9000/tcp
raft-node1          Up X minutes    0.0.0.0:50051->50051/tcp
raft-node2          Up X minutes    0.0.0.0:50052->50052/tcp
raft-node3          Up X minutes    0.0.0.0:50053->50053/tcp
movie-llm-server    Up X minutes    0.0.0.0:8500->8500/tcp
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

**View all logs:**
```bash
sudo docker compose logs -f
```

**View specific service logs:**
```bash
sudo docker compose logs -f app-server
sudo docker compose logs -f raft-node1
sudo docker compose logs -f raft-node2
sudo docker compose logs -f raft-node3
sudo docker compose logs -f llm-server
```

**View last 50 lines:**
```bash
sudo docker compose logs --tail=50 [service-name]
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

### Step 2: Test Raft Nodes (Ports 50051-50053)

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

### Step 3: Test LLM Server (Port 8500)

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

### Stop All Services
```bash
sudo docker compose down
```

### Stop Specific Service
```bash
sudo docker compose stop app-server
sudo docker compose stop llm-server
```

### Stop and Remove Containers (keeps images)
```bash
sudo docker compose down
```

### Stop and Remove Everything (containers + volumes)
```bash
sudo docker compose down -v
```

---

## 🔄 Restarting Services

### Restart All Services
```bash
sudo docker compose restart
```

### Restart Specific Service
```bash
sudo docker compose restart app-server
sudo docker compose restart raft-node1
sudo docker compose restart llm-server
```

### Rebuild and Restart (after code changes)
```bash
sudo docker compose build app-server
sudo docker compose up -d app-server
```

---

## 🧹 Cleanup Commands

### Remove All Containers and Volumes
```bash
sudo docker compose down -v
```

### Remove All Images
```bash
sudo docker compose down --rmi all
```

### Complete Cleanup (containers + volumes + images)
```bash
sudo docker compose down -v --rmi all
```

### System Prune (removes unused Docker resources)
```bash
sudo docker system prune -a
```

---

## 🔧 Troubleshooting Commands

### Check Service Status
```bash
sudo docker compose ps
```

### View Recent Logs
```bash
sudo docker compose logs --tail=50 [service-name]
```

### Rebuild Without Cache
```bash
sudo docker compose build --no-cache [service-name]
sudo docker compose up -d [service-name]
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

### First Time Setup
```bash
# 1. Build images
sudo docker compose build

# 2. Start services
sudo docker compose up -d

# 3. Wait for services to be ready (especially LLM - takes 30-60s)
sleep 10

# 4. Check status
sudo docker compose ps
./scripts/check_health.sh
```

### After Code Changes
```bash
# 1. Rebuild the changed service
sudo docker compose build app-server

# 2. Restart the service
sudo docker compose up -d app-server

# 3. Check logs
sudo docker compose logs -f app-server
```

### Daily Development
```bash
# Start services
sudo docker compose up -d

# View logs in real-time
sudo docker compose logs -f

# Stop when done
sudo docker compose down
```

### Production Deployment
```bash
# 1. Pull latest code
git pull

# 2. Rebuild all images
sudo docker compose build

# 3. Restart services
sudo docker compose up -d

# 4. Verify health
./scripts/check_health.sh
```

---

## ⚠️ Important Notes

1. **First Run**: LLM server takes 30-60 seconds to download and load the model (~1GB)
2. **Memory**: LLM server requires 2-4GB RAM. Skip it if low on resources:
   ```bash
   sudo docker compose up -d app-server raft-node1 raft-node2 raft-node3
   ```
3. **Ports**: Ensure ports 9000, 50051, 50052, 50053, and 8500 are not in use
4. **Permissions**: On Linux, you may need `sudo` for Docker commands
5. **Networks**: All services communicate via `movie-booking-network` bridge network

---

## ✅ Quick Verification Checklist

After starting services, verify:

- [ ] All containers are running: `sudo docker compose ps`
- [ ] App server responds: `curl http://localhost:9000/health`
- [ ] Raft nodes respond: `curl http://localhost:50051/status`
- [ ] LLM server responds: `curl http://localhost:8500/health`
- [ ] Health check script passes: `./scripts/check_health.sh`

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

