# 🚀 Quick Reference - Docker & LLM Commands

## Docker Commands

### Start & Stop
```bash
# Start all services
docker-compose up -d

# Start without LLM (faster, less memory)
docker-compose up -d app-server raft-node1 raft-node2 raft-node3

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart specific service
docker-compose restart llm-server
```

### Logs & Monitoring
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f llm-server

# Check service status
docker-compose ps

# Check resource usage
docker stats
```

### Troubleshooting
```bash
# Rebuild service
docker-compose build llm-server

# Rebuild without cache
docker-compose build --no-cache

# Enter container shell
docker-compose exec app-server bash

# Remove all stopped containers
docker system prune -a
```

---

### Health Checks

```bash
# Quick health check script
./scripts/check_health.sh

# Manual health checks
curl http://localhost:9000/health     # App Server
curl http://localhost:50051/status    # Raft Node 1
curl http://localhost:50052/status    # Raft Node 2
curl http://localhost:50053/status    # Raft Node 3
curl http://localhost:8500/health     # LLM Server
```

---

## LLM Server Commands

### Test Endpoints
```bash
# Health check
curl http://localhost:8500/health

# Simple FAQ question
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I book a ticket?"}'

# Chat conversation
curl -X POST http://localhost:8500/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I need help"}
    ]
  }'

# Run automated tests
./scripts/test_llm_viability.sh
```

---

## Application Server Commands

### User Management
```bash
# Register user
curl -X POST http://localhost:9000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "password": "pass123"}'

# Login
curl -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123"}'

# Save token for later use
TOKEN=$(curl -s -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123"}' | \
  grep -o '"token":"[^"]*"' | cut -d'"' -f4)
```

### Movie Management
```bash
# Add movie (admin only)
curl -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$TOKEN\", \"movie\": \"Inception\", \"city\": \"Delhi\"}"

# Get all movies
curl "http://localhost:9000/data/movies?token=$TOKEN"

# Get bookings
curl "http://localhost:9000/data/bookings?token=$TOKEN"
```

### Booking Tickets
```bash
# Book a ticket
curl -X POST http://localhost:9000/business \
  -H "Content-Type: application/json" \
  -d "{
    \"requestId\":\"booking-$(date +%s)\",
    \"payload\":{
      \"type\":\"book_seat\",
      \"data\":{
        \"movie\":\"Inception\",
        \"city\":\"Delhi\",
        \"seats\":2
      }
    },
    \"context\":{\"token\":\"$TOKEN\"}
  }"
```

---

## Client View Commands

### GUI Application
```bash
# Install dependencies
pip install customtkinter requests

# Run GUI (requires display server)
export DISPLAY=:0
python app.py

# Or use venv
source venv/bin/activate
python app.py
```

### CLI Demo
```bash
# Run complete system setup and testing
./quickstart.sh

# Make executable if needed
chmod +x quickstart.sh scripts/*.sh
```

### Complete Test Flow
```bash
# 1. Register
curl -X POST http://localhost:9000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}' | \
  grep -o '"token":"[^"]*"' | cut -d'"' -f4)

# 3. View movies
curl "http://localhost:9000/data/movies?token=$TOKEN"

# 4. Book ticket
curl -X POST http://localhost:9000/business \
  -H "Content-Type: application/json" \
  -d "{
    \"requestId\":\"test-$(date +%s)\",
    \"payload\":{
      \"type\":\"book_seat\",
      \"data\":{\"movie\":\"Inception\",\"city\":\"Delhi\",\"seats\":1}
    },
    \"context\":{\"token\":\"$TOKEN\"}
  }"

# 5. Check bookings
curl "http://localhost:9000/data/bookings?token=$TOKEN"
```

---

## Raft Commands

```bash
# Check node status
curl http://localhost:50051/status | jq
curl http://localhost:50052/status | jq
curl http://localhost:50053/status | jq

# Trigger manual election (for testing)
curl -X POST http://localhost:50051/trigger-election
```

---

## Environment Variables

### Set Before Starting

```bash
# In .env file or export
export LLM_MODEL=Qwen/Qwen2.5-0.5B
export LLM_MAX_NEW_TOKENS=512
export LLM_TEMPERATURE=0.7
export DOCKER_ENV=true
```

---

## Common Workflows

### Fresh Start
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
./check_health.sh
```

### Update Code & Restart
```bash
# After changing Python code
docker-compose build app-server
docker-compose up -d app-server
docker-compose logs -f app-server
```

### Debug Mode
```bash
# Enter container
docker-compose exec llm-server bash

# Check Python version
python --version

# Test imports
python -c "import transformers; print(transformers.__version__)"

# Check environment
env | grep LLM
```

---

## Ports Reference

| Service | Port | URL |
|---------|------|-----|
| App Server | 9000 | http://localhost:9000 |
| Raft Node 1 | 50051 | http://localhost:50051 |
| Raft Node 2 | 50052 | http://localhost:50052 |
| Raft Node 3 | 50053 | http://localhost:50053 |
| LLM Server | 8500 | http://localhost:8500 |

---

## API Endpoints Quick Reference

### Application Server (Port 9000)
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/health` | GET | No | Server health check |
| `/register` | POST | No | Create new user |
| `/login` | POST | No | User authentication |
| `/data/movies` | GET | Yes | List all movies |
| `/data/bookings` | GET | Yes | User's bookings |
| `/business` | POST | Yes | Book tickets |
| `/add_movie` | POST | Admin | Add new movie |

### Raft Nodes (Ports 50051-50053)
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/status` | GET | No | Node & cluster status |
| `/trigger-election` | POST | No | Manual election trigger |

### LLM Server (Port 8500)
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/health` | GET | No | LLM server & model status |
| `/ask` | POST | No | FAQ-style questions |
| `/chat` | POST | No | Conversational AI |

---

## File Locations

### Utility Scripts
- `quickstart.sh` - Complete setup and testing
- `scripts/check_health.sh` - Health check all services
- `scripts/load_sample_data.sh` - Load 15 sample movies
- `scripts/reset_database.sh` - Clear all data
- `scripts/test_llm_viability.sh` - Test LLM endpoints

### Configuration
- `docker-compose.yml` - Service orchestration
- `.env` - Environment variables (optional)
- `requirements.txt` - Python dependencies

### Dockerfiles
- `Dockerfile.app` - Application server
- `Dockerfile.raft` - Raft nodes
- `Dockerfile.llm` - LLM server

### Code
- `Application_server/Application_server.py` - Main app server
- `llm/llm_server.py` - LLM server with Qwen2.5
- `raft/raft_node.py` - Raft implementation
- `app.py` - Single-window GUI
- `app_multi.py` - Multi-window GUI

### Documentation (in `docs/`)
- `QUICKSTART.md` - 2-minute setup guide
- `ARCHITECTURE.md` - System design
- `DOCKER.md` - Docker deployment guide
- `CLIENT_VIEW.md` - API reference and GUI
- `QUICK_REFERENCE.md` - This file

---

## Keyboard Shortcuts

```bash
# View logs and follow (Ctrl+C to exit)
docker-compose logs -f

# Stop services (Ctrl+C if running in foreground)
docker-compose down

# Force stop container
docker kill <container_id>
```

---

## Emergency Commands

```bash
# Kill all Docker containers
docker kill $(docker ps -q)

# Remove all containers
docker rm $(docker ps -a -q)

# Remove all images
docker rmi $(docker images -q)

# Nuclear option - clean everything
docker system prune -a --volumes

# Kill processes on specific port
lsof -ti:8500 | xargs kill -9
```

---

## Performance Tips

1. **Limit LLM memory:**
   Edit docker-compose.yml, set memory: 2G

2. **Use shorter responses:**
   Set LLM_MAX_NEW_TOKENS=256

3. **Reduce temperature:**
   Set LLM_TEMPERATURE=0.3

4. **Skip LLM entirely:**
   `docker-compose up -d app-server raft-node{1,2,3}`

---

## Default Credentials

```
Username: admin
Password: 123

Username: utkarsh
Password: password123
```

---

## Quick Copy-Paste Commands

### Complete Setup
```bash
./quickstart.sh
```

### Test Everything
```bash
curl http://localhost:9000/health && \
curl http://localhost:50051/status && \
curl http://localhost:8500/health && \
echo "All services OK!"
```

### View All Logs
```bash
docker-compose logs -f --tail=50
```

### Load Sample Data
```bash
./scripts/load_sample_data.sh
```

### Clear All Data
```bash
./scripts/reset_database.sh --force
```

---

**💡 Tip:** Keep this file open while working with the system!
