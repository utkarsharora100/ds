# 🚀 Quick Start Guide

Get the system running in **under 2 minutes**!

## Prerequisites

```bash
docker --version      # Should be 20.10+
docker-compose --version  # Should be 2.0+
```

Need Docker? [Install Docker](https://docs.docker.com/get-docker/)

---

## 🎯 Choose Your Method

**Method 1: Desktop GUI** (CustomTkinter)  
**Method 2: Web UI** (Browser-based)

---

## 📱 Method 1: Desktop GUI (Quick Start)

### Step 1: Start Backend

```bash
docker compose up -d
```

### Step 2: Install GUI Dependencies

```bash
pip install -r requirements-app.txt
```

### Step 3: Launch GUI

```bash
```

**That's it!** ✅

---

## 🌐 Method 2: Web UI (Quick Start)

### Step 1: Start Everything

```bash
docker compose -f docker-compose.combined.yml up -d --build
```

### Step 2: Access Web UI

Open browser: **http://localhost:3000**

**That's it!** ✅

---

## What Just Happened?

### Method 1 Started:
- ✅ Application Server (port 9000)
- ✅ Raft Node 1 (port 50051)
- ✅ Raft Node 2 (port 50052)
- ✅ Raft Node 3 (port 50053)
- ✅ LLM Server with Qwen2.5 (port 8500)

### Method 2 Started:
- ✅ Application Server (port 9000)
- ✅ Web Frontend (port 3000)
- ✅ Raft Node 1 (port 50051)
- ✅ Raft Node 2 (port 50052)
- ✅ Raft Node 3 (port 50053)
- ✅ LLM Server with Qwen2.5 (port 8500)

---

## Wait 30-60 Seconds

The LLM model needs to load (~500MB download on first run).

Check progress:
```bash
docker-compose logs -f llm-server
```

Look for: `✅ Model loaded successfully`

Press `Ctrl+C` to exit logs.

---

## Verify Everything Works

### Quick Health Check

```bash
./scripts/check_health.sh
```

Expected output:
```
✅ Application Server OK
✅ Raft Node 1 OK
✅ Raft Node 2 OK
✅ Raft Node 3 OK
✅ LLM Server OK
✅ Leader elected: node2
```

### Manual Checks

```bash
# App Server
curl http://localhost:9000/health

# LLM Server
curl http://localhost:8500/health

# Raft Status
curl http://localhost:50051/status
```

---

## Test the APIs

### 1. Login

```bash
curl -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123"}'
```

You should get a token back.

### 2. Ask the AI

```bash
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I book a ticket?"}'
```

The AI will respond with booking instructions!

### 3. Run Full Test Suite

```bash
python test_llm.py
```

---

## View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app-server
```

---

## Stop Everything

```bash
docker-compose down
```

---

## Troubleshooting

### "Port already in use"

```bash
# Find and kill the process
lsof -ti:9000 | xargs kill -9

# Or change port in docker-compose.yml
```

### "Out of memory" (LLM Server)

Option 1: Increase Docker memory to 6GB+  
Settings → Resources → Memory

Option 2: Skip LLM server
```bash
docker-compose up -d app-server raft-node1 raft-node2 raft-node3
```

### Services won't start

```bash
# Check Docker is running
docker info

# Clean restart
docker-compose down -v
docker-compose up -d
```

### Model download is slow

First run downloads ~500MB. Be patient!

Check progress:
```bash
docker-compose logs -f llm-server
```

---

## Next Steps

Now that everything is running:

1. **Read the docs**: [README.md](../README.md) for full details
2. **Understand the system**: Read [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Docker deep dive**: Check [DOCKER.md](DOCKER.md)
4. **Test Raft consensus**: See [CLIENT_VIEW.md](CLIENT_VIEW.md) for API testing

---

## Common Commands

```bash
# Complete setup with tests
./quickstart.sh

# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Health check
./scripts/check_health.sh

# Load sample data
./scripts/load_sample_data.sh

# Reset database
./scripts/reset_database.sh --force

# Test LLM
./scripts/test_llm_viability.sh
```

---

## Default Credentials

**Login to test:**
- Username: `admin`
- Password: `123`

**Or:**
- Username: `utkarsh`
- Password: `password123`

---

## What's Running?

| Service | Port | What it does |
|---------|------|--------------|
| app-server | 9000 | Booking API |
| raft-node1 | 50051 | Consensus (1) |
| raft-node2 | 50052 | Consensus (2) |
| raft-node3 | 50053 | Consensus (3) |
| llm-server | 8500 | AI Assistant |

---

## Performance

**First start:** 2-3 minutes (model download)  
**Subsequent starts:** 30-60 seconds  
**LLM responses:** 2-5 seconds (CPU)

---

## Need Help?

Check [README.md](../README.md) for:
- Complete testing guide (5 options)
- API documentation
- Troubleshooting guide
- Advanced configuration
- Development workflows

## Available Utility Scripts

All scripts are located in `scripts/` folder:

| Script | Purpose |
|--------|---------|
| `quickstart.sh` | Complete setup with Raft & functionality tests |
| `check_health.sh` | Health check all services |
| `load_sample_data.sh` | Load 15 sample movies |
| `reset_database.sh` | Clear all data |
| `test_llm_viability.sh` | Test LLM endpoints |

---

**🎉 You're ready!** The system is now running.

Try this:
```bash
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this system?"}'
```
