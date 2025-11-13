# 🚀 How to Run the Movie Booking System

Complete step-by-step guide for both usage methods.

## 📋 Prerequisites

- **Docker**: Version 20.10+ installed and running
- **Docker Compose**: Version 2.0+
- **Python**: 3.10+ (for Method 1 only)
- **System**: 6GB RAM (for LLM), 10GB free disk space

---

## 🎯 Choose Your Method

This system supports **two different usage methods**:

| Method | Interface | Best For |
|--------|-----------|----------|
| **Method 1** | CustomTkinter Desktop GUI | Local development, GUI testing |
| **Method 2** | Web Browser UI | Production, remote access |

---

## 📱 Method 1: CustomTkinter Desktop GUI + Standard Docker

**Best for:** Desktop applications, local development, GUI testing

### Step 1: Navigate to Project Directory

```bash
cd "C:\Users\utkarsh\Desktop\New folder (3)\ds"
# OR on Linux/Mac:
cd /path/to/ds
```

### Step 2: Start Backend Services (Docker)

```bash
# Start backend services (app-server, raft nodes, LLM)
docker compose up -d --build
```

**Without LLM (Lower Resources):**
```bash
docker compose up -d app-server raft-node1 raft-node2 raft-node3
```

### Step 3: Verify Services

Wait 10-30 seconds for services to initialize, then check:

```bash
# Check container status
docker compose ps

# Check backend health
curl http://localhost:9000/health
```

Expected output:
```json
{"status":"healthy","service":"application-server"}
```

### Step 4: Install GUI Dependencies

```bash
# Install Python dependencies for GUI
pip install -r requirements/requirements-app.txt

# OR install manually
pip install customtkinter requests
```

### Step 5: Launch Desktop GUI

**Option A: Single-Window GUI**
```bash
python app.py
```

**Option B: Multi-Window GUI (3 clients + 1 admin)**
```bash
python app_multi.py
```

This will launch:
- 1 Admin window (left side)
- 3 Client windows: alice, bob, charlie (right side)

### Step 6: Login

- **Admin**: `admin` / `123`
- **User**: `utkarsh` / `password123`

### Access Points

- **Backend API**: http://localhost:9000
- **Desktop GUI**: Launched via Python scripts

---

## 🌐 Method 2: Web UI + Combined Docker (Frontend + Backend)

**Best for:** Web applications, remote access, production deployment

### Step 1: Navigate to Project Directory

```bash
cd "C:\Users\utkarsh\Desktop\New folder (3)\ds"
# OR on Linux/Mac:
cd /path/to/ds
```

### Step 2: Start Combined Services (Docker)

```bash
# Start all services including web frontend
docker compose -f docker-compose.combined.yml up -d --build
```

This starts:
- ✅ Backend API (port 9000)
- ✅ Web Frontend (port 3000)
- ✅ Raft Nodes (ports 50051-50053)
- ✅ LLM Server (port 8500, optional)

**Without LLM (Lower Resources):**
```bash
docker compose -f docker-compose.combined.yml up -d movie-booking-app raft-node1 raft-node2 raft-node3
```

### Step 3: Wait for Services to Start

Wait about 10-30 seconds for services to initialize. Check status:

```bash
docker compose -f docker-compose.combined.yml ps
```

You should see all services with status "Up".

### Step 4: Verify Services

```bash
# Check backend health
curl http://localhost:9000/health

# Check frontend
curl http://localhost:3000
```

### Step 5: Access Web Application

Open your web browser and go to:

```
http://localhost:3000
```

### Step 6: Login

- **Admin**: `admin` / `123`
- **User**: `utkarsh` / `password123`

### Access Points

- **Web UI**: http://localhost:3000
- **Backend API**: http://localhost:9000

---

## 📊 Quick Comparison

| Feature | Method 1: Desktop GUI | Method 2: Web UI |
|---------|----------------------|------------------|
| **Interface** | CustomTkinter Desktop App | Web Browser |
| **Docker File** | `docker-compose.yml` | `docker-compose.combined.yml` |
| **Frontend** | Runs locally (Python) | Runs in Docker (port 3000) |
| **Backend** | Docker (port 9000) | Docker (port 9000) |
| **Remote Access** | Requires X11/SSH forwarding | Works over network |
| **Dependencies** | Python + customtkinter | Just Docker + Browser |
| **Best For** | Local development, GUI testing | Production, remote access |

---

## 🔧 Common Commands

### Method 1: Standard Docker

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f app-server

# Restart service
docker compose restart app-server

# Rebuild service
docker compose build app-server --no-cache
```

### Method 2: Combined Docker

```bash
# Start services
docker compose -f docker-compose.combined.yml up -d --build

# Stop services
docker compose -f docker-compose.combined.yml down

# View logs
docker compose -f docker-compose.combined.yml logs -f movie-booking-app

# Restart service
docker compose -f docker-compose.combined.yml restart movie-booking-app

# Rebuild service
docker compose -f docker-compose.combined.yml build --no-cache movie-booking-app
```

---

## ✅ Verify Everything Works

### Method 1 Verification

1. **Check backend**: `curl http://localhost:9000/health`
2. **Launch GUI**: `python app.py` or `python app_multi.py`
3. **Login** as admin or user
4. **Test features**: Add movies, book tickets, view bookings

### Method 2 Verification

1. **Check backend**: `curl http://localhost:9000/health`
2. **Check frontend**: Open http://localhost:3000 in browser
3. **Login** as admin or user
4. **Test features**: 
   - Load Sample Movies
   - Clear Database
   - Test LLM Service
   - Check System Health

---

## 🩺 Troubleshooting

### Services Not Starting

```bash
# Check logs
docker compose logs [service-name] --tail=50

# Rebuild
docker compose build [service-name] --no-cache
docker compose up -d [service-name]
```

### Port Already in Use

**Windows:**
```powershell
netstat -ano | findstr :9000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
sudo lsof -i :9000
sudo kill -9 <PID>
```

### GUI Not Launching (Method 1)

- **Windows**: Install Python and customtkinter
- **Linux**: Install `python3-tk`: `sudo apt-get install python3-tk`
- **Mac**: Install XQuartz or use Web UI instead

### Web UI Not Loading (Method 2)

1. Verify backend is running: `curl http://localhost:9000/health`
2. Check browser console (F12) for errors
3. Verify port 3000 is accessible: `curl http://localhost:3000`
4. Check logs: `docker compose -f docker-compose.combined.yml logs movie-booking-app`

---

## 📝 Notes

- **First run** takes ~10 minutes due to Docker image builds and LLM model download (~1GB)
- **Keep Docker running** while using the application
- **Method 1** requires Python and GUI dependencies
- **Method 2** only requires Docker and a web browser
- Both methods use the same backend services

---

## 🎯 Next Steps

- See [QUICKSTART.md](QUICKSTART.md) for 2-minute setup
- See [COMBINED_SETUP.md](COMBINED_SETUP.md) for Method 2 details
- See [DOCKER_STEPS.md](DOCKER_STEPS.md) for complete Docker reference
- See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for command cheat sheet

---

**Ready to go!** Choose your method and follow the steps above. 🚀
