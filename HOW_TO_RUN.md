# 🚀 How to Run the Movie Booking System

## Quick Start Guide

### Step 1: Navigate to Project Directory

```powershell
cd "C:\Users\utkarsh\Desktop\New folder (3)\ds"
```

### Step 2: Build and Start Services

**Option A: Full Setup (with LLM)**
```powershell
docker compose -f docker-compose.combined.yml up -d --build
```

**Option B: Without LLM (Lower Resources)**
```powershell
docker compose -f docker-compose.combined.yml up -d --build movie-booking-app raft-node1 raft-node2 raft-node3
```

### Step 3: Wait for Services to Start

Wait about 10-30 seconds for services to initialize. Check status:

```powershell
docker compose -f docker-compose.combined.yml ps
```

You should see all services with status "Up".

### Step 4: Access the Application

Open your web browser and go to:

**Frontend (Web UI):**
```
http://localhost:3000
```

**Backend API (for testing):**
```
http://localhost:9000/health
```

### Step 5: Login

**Admin Account:**
- Username: `admin`
- Password: `123`

**User Account:**
- Username: `utkarsh`
- Password: `password123`

---

## Detailed Commands

### Check Service Status

```powershell
# View running containers
docker compose -f docker-compose.combined.yml ps

# View logs
docker compose -f docker-compose.combined.yml logs -f movie-booking-app

# View all logs
docker compose -f docker-compose.combined.yml logs -f
```

### Stop Services

```powershell
# Stop all services
docker compose -f docker-compose.combined.yml stop

# Stop and remove containers
docker compose -f docker-compose.combined.yml down
```

### Restart Services

```powershell
# Restart all services
docker compose -f docker-compose.combined.yml restart

# Restart specific service
docker compose -f docker-compose.combined.yml restart movie-booking-app
```

### Rebuild After Code Changes

```powershell
# Rebuild and restart
docker compose -f docker-compose.combined.yml build --no-cache movie-booking-app
docker compose -f docker-compose.combined.yml up -d movie-booking-app
```

---

## Verify Everything Works

### 1. Check Backend Health

```powershell
curl http://localhost:9000/health
```

Expected response:
```json
{"status":"healthy","service":"application-server"}
```

### 2. Check Frontend

Open browser: `http://localhost:3000`

You should see the login page.

### 3. Test Admin Features

1. Login as `admin` / `123`
2. Click "Load Sample Movies" - should load 15 movies
3. Click "Clear Database" - should clear all data
4. Click "Test LLM Service" - should show LLM status
5. Click "Check System Health" - should show all services

---

## Troubleshooting

### Port Already in Use

If you get port conflict errors:

```powershell
# Check what's using the ports
netstat -ano | findstr ":3000"
netstat -ano | findstr ":9000"

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

### Services Not Starting

```powershell
# Check logs for errors
docker compose -f docker-compose.combined.yml logs movie-booking-app

# Rebuild from scratch
docker compose -f docker-compose.combined.yml down
docker compose -f docker-compose.combined.yml build --no-cache
docker compose -f docker-compose.combined.yml up -d
```

### Frontend Not Loading

1. Verify backend is running: `curl http://localhost:9000/health`
2. Check browser console (F12) for errors
3. Verify port 3000 is accessible: `curl http://localhost:3000`

### Database Issues

If movies/bookings aren't working:

1. Login as admin
2. Click "Clear Database"
3. Click "Load Sample Movies"
4. Refresh the page

---

## Service Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 9000 | http://localhost:9000 |
| LLM Server | 8500 | http://localhost:8500 |
| Raft Node 1 | 50051 | http://localhost:50051 |
| Raft Node 2 | 50052 | http://localhost:50052 |
| Raft Node 3 | 50053 | http://localhost:50053 |

---

## Quick Reference

### Start Everything
```powershell
docker compose -f docker-compose.combined.yml up -d
```

### Stop Everything
```powershell
docker compose -f docker-compose.combined.yml down
```

### View Logs
```powershell
docker compose -f docker-compose.combined.yml logs -f
```

### Rebuild
```powershell
docker compose -f docker-compose.combined.yml build --no-cache
docker compose -f docker-compose.combined.yml up -d
```

---

## First Time Setup

1. **Make sure Docker is running**
   - Check Docker Desktop is open (Windows)
   - Or Docker daemon is running (Linux)

2. **Build images** (first time only, takes 5-10 minutes):
   ```powershell
   docker compose -f docker-compose.combined.yml build
   ```

3. **Start services**:
   ```powershell
   docker compose -f docker-compose.combined.yml up -d
   ```

4. **Wait for initialization** (30-60 seconds)

5. **Access application**: http://localhost:3000

---

## Success Indicators

✅ **Services Running:**
- All containers show "Up" status
- No error messages in logs

✅ **Backend Working:**
- `curl http://localhost:9000/health` returns success
- Can login via web UI

✅ **Frontend Working:**
- Login page loads at http://localhost:3000
- Can login and see dashboard

✅ **Features Working:**
- Load Sample Movies works
- Clear Database works
- Test LLM works (if LLM server running)
- Health Check works

---

**Ready to go!** 🎬

