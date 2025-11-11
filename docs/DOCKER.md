# 🐳 Docker Deployment Guide

This guide explains how to run the Distributed Movie Booking System using Docker and Docker Compose.

## 📋 Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **System Requirements**: 
  - 4GB RAM minimum (6GB recommended for LLM server)
  - 10GB free disk space

### Check Installation

```bash
docker --version
docker-compose --version
```

---

## 🚀 Quick Start (Recommended)

### Option 1: Full System with LLM

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

**Services Started:**
- ✅ Application Server (port 9000)
- ✅ Raft Node 1 (port 50051)
- ✅ Raft Node 2 (port 50052)
- ✅ Raft Node 3 (port 50053)
- ✅ LLM Server (port 8500)

---

### Option 2: Without LLM Server (Faster)

```bash
# Start without LLM to save resources
docker-compose up -d app-server raft-node1 raft-node2 raft-node3

# View logs
docker-compose logs -f app-server raft-node1 raft-node2 raft-node3
```

---

## 📊 Service Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Docker Network                          │
│               (movie-booking-net)                         │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────┐         ┌──────────────────┐       │
│  │  app-server     │         │   llm-server     │       │
│  │  Port: 9000     │         │   Port: 8500     │       │
│  │  FastAPI        │         │   Qwen2.5-0.5B   │       │
│  └─────────────────┘         └──────────────────┘       │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ raft-node1   │  │ raft-node2   │  │ raft-node3   │  │
│  │ Port: 50051  │  │ Port: 50052  │  │ Port: 50053  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
└──────────────────────────────────────────────────────────┘
         │              │              │             │
         └──────────────┴──────────────┴─────────────┘
                    Host Machine Ports
```

**LLM Model:** Qwen/Qwen2.5-0.5B
- **Type:** Generative Chat Model
- **Size:** ~500MB
- **Parameters:** 500M
- **Features:** Chat, FAQ, Multi-turn conversations
- **Performance:** 2-5s response time (CPU), 0.5-1s (GPU)

---

## 🔧 Docker Commands Reference

### Building

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build app-server

# Build without cache (fresh build)
docker-compose build --no-cache
```

---

### Starting Services

```bash
# Start all services in background
docker-compose up -d

# Start specific services
docker-compose up -d app-server raft-node1

# Start with live logs
docker-compose up

# Start with rebuild
docker-compose up -d --build
```

---

### Stopping Services

```bash
# Stop all services
docker-compose stop

# Stop specific service
docker-compose stop llm-server

# Stop and remove containers
docker-compose down

# Stop, remove containers and volumes
docker-compose down -v
```

---

### Viewing Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs -f app-server

# View last 100 lines
docker-compose logs --tail=100 raft-node1

# View logs with timestamps
docker-compose logs -t -f
```

---

### Service Management

```bash
# List running containers
docker-compose ps

# Restart specific service
docker-compose restart app-server

# Scale services (not applicable for our setup)
# docker-compose up -d --scale raft-node=5

# Execute command in running container
docker-compose exec app-server bash
docker-compose exec raft-node1 python -c "print('Hello')"
```

---

## 🧪 Testing the Docker Deployment

### 1. Check All Services Are Running

```bash
docker-compose ps
```

**Expected Output:**
```
NAME                  STATUS    PORTS
movie-app-server      Up        0.0.0.0:9000->9000/tcp
raft-node1            Up        0.0.0.0:50051->50051/tcp
raft-node2            Up        0.0.0.0:50052->50052/tcp
raft-node3            Up        Up        0.0.0.0:50053->50053/tcp
movie-llm-server      Up        0.0.0.0:8500->8500/tcp
```

---

### 2. Test Application Server

```bash
# Health check
curl http://localhost:9000/health

# Login test
curl -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123"}'
```

**Expected Response:**
```json
{
  "status": "success",
  "token": "...",
  "user": "admin"
}
```

---

### 3. Test Raft Nodes

```bash
# Check each node status
curl http://localhost:50051/status
curl http://localhost:50052/status
curl http://localhost:50053/status
```

**Expected:** One node should show `"state": "leader"`

---

### 4. Test LLM Server

```bash
# Health check
curl http://localhost:8500/health

# Ask a question (FAQ mode)
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I cancel my booking?"}'

# Chat mode (conversational)
curl -X POST http://localhost:8500/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I want to book a movie ticket"}
    ]
  }'
```

**Or use the test script:**

```bash
# Run comprehensive LLM tests
python test_llm.py
```

📖 **For detailed LLM testing, see [LLM_TESTING.md](LLM_TESTING.md)**

---

### 5. Monitor Leader Election

```bash
# Watch Raft logs for leader election
docker-compose logs -f raft-node1 raft-node2 raft-node3 | grep "LEADER"
```

**Expected:** Should see something like:
```
[node2] 🏆 is the LEADER now (term 1)
```

---

## 🔍 Troubleshooting

### Issue: Container Won't Start

```bash
# Check container logs
docker-compose logs <service-name>

# Check container status
docker-compose ps -a

# Inspect specific container
docker inspect movie-app-server
```

---

### Issue: Port Already in Use

**Error:** `Bind for 0.0.0.0:9000 failed: port is already allocated`

**Solution:**
```bash
# Find process using the port
lsof -i :9000

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
# ports:
#   - "9001:9000"  # Change host port to 9001
```

---

### Issue: Out of Memory (LLM Server)

**Error:** Container keeps restarting

**Solution:**
```bash
# 1. Check Docker memory limits
docker stats

# 2. Increase Docker Desktop memory (Settings > Resources)

# 3. Or run without LLM server
docker-compose up -d app-server raft-node1 raft-node2 raft-node3
```

---

### Issue: Network Issues Between Containers

```bash
# Check network
docker network inspect movie-booking-net

# Restart networking
docker-compose down
docker-compose up -d

# Test connectivity between containers
docker-compose exec app-server ping raft-node1
```

---

### Issue: Stale Images After Code Changes

```bash
# Rebuild without cache
docker-compose build --no-cache

# Remove old images
docker image prune -a

# Full cleanup
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

---

## 🔐 Security Considerations

### Development vs Production

**Current Setup:** Development mode
- All origins allowed (CORS)
- Default credentials
- No HTTPS
- No secrets management

**For Production:**
1. Use Docker secrets or environment variables for credentials
2. Enable HTTPS with certificates
3. Restrict CORS origins
4. Use Docker secrets:
   ```yaml
   secrets:
     db_password:
       file: ./secrets/db_password.txt
   ```
5. Scan images for vulnerabilities:
   ```bash
   docker scan movie-app-server
   ```

---

## 📈 Performance Optimization

### 1. Multi-Stage Builds

Update Dockerfiles to use multi-stage builds for smaller images.

### 2. Layer Caching

Order Dockerfile commands from least to most frequently changing:
```dockerfile
# Good order
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

### 3. Resource Limits

Add resource limits in docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

---

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build images
        run: docker-compose build
      - name: Start services
        run: docker-compose up -d
      - name: Run tests
        run: |
          sleep 10
          curl -f http://localhost:9000/health
          curl -f http://localhost:50051/status
```

---

## 📊 Monitoring

### View Resource Usage

```bash
# Real-time stats
docker stats

# Specific container
docker stats movie-app-server

# Export to CSV
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" > stats.csv
```

---

### Health Checks

Services have built-in health checks. View status:

```bash
# Check health
docker-compose ps

# View health check logs
docker inspect --format='{{json .State.Health}}' movie-app-server | jq
```

---

## 🗂️ Data Persistence (Optional)

To add persistent storage, uncomment volumes in docker-compose.yml:

```yaml
volumes:
  movie-db-data:
  raft-logs:

services:
  app-server:
    volumes:
      - movie-db-data:/app/data
```

---

## 🚀 Production Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml movie-booking

# Scale services
docker service scale movie-booking_raft-node=5

# Check status
docker stack services movie-booking
```

---

### Using Kubernetes

Convert docker-compose to Kubernetes:

```bash
# Install kompose
curl -L https://github.com/kubernetes/kompose/releases/download/v1.28.0/kompose-linux-amd64 -o kompose
chmod +x kompose
sudo mv kompose /usr/local/bin/

# Convert
kompose convert

# Deploy
kubectl apply -f .
```

---

## 📝 Environment Variables

Available environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_HOST` | 0.0.0.0 | Application server bind address |
| `APP_PORT` | 9000 | Application server port |
| `DOCKER_ENV` | false | Enable Docker networking mode |

**Usage:**
```yaml
services:
  app-server:
    environment:
      - APP_HOST=0.0.0.0
      - APP_PORT=9000
```

---

## 🎯 Common Workflows

### Development Workflow

```bash
# 1. Make code changes
vim Application_server/Application_server.py

# 2. Rebuild specific service
docker-compose build app-server

# 3. Restart service
docker-compose up -d app-server

# 4. View logs
docker-compose logs -f app-server
```

---

### Debugging Workflow

```bash
# 1. Enter container shell
docker-compose exec app-server bash

# 2. Run commands inside container
python -c "import uvicorn; print(uvicorn.__version__)"

# 3. Check environment
env | grep APP

# 4. Test network connectivity
ping raft-node1
curl http://raft-node1:50051/status
```

---

## 🧹 Cleanup

### Remove Everything

```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove images
docker rmi $(docker images -q movie-*)

# Clean system
docker system prune -a --volumes
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)

---

## 🆘 Getting Help

### Check Service Health

```bash
# Quick health check script
./check_health.sh
```

Create `check_health.sh`:
```bash
#!/bin/bash
echo "Checking services..."
curl -s http://localhost:9000/health && echo "✅ App Server OK" || echo "❌ App Server FAILED"
curl -s http://localhost:50051/status && echo "✅ Raft Node 1 OK" || echo "❌ Raft Node 1 FAILED"
curl -s http://localhost:50052/status && echo "✅ Raft Node 2 OK" || echo "❌ Raft Node 2 FAILED"
curl -s http://localhost:50053/status && echo "✅ Raft Node 3 OK" || echo "❌ Raft Node 3 FAILED"
curl -s http://localhost:8500/health && echo "✅ LLM Server OK" || echo "❌ LLM Server FAILED"
```

---

**Happy Dockerizing! 🐳**
