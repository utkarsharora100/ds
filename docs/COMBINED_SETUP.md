# 🐳 Method 2: Combined Frontend + Backend Docker Setup

**This is Method 2: Web UI + Combined Docker**

This setup combines the frontend and backend into a single Docker container for easier deployment. The web frontend runs inside Docker and is accessible via browser.

**For Desktop GUI setup, see [HOW_TO_RUN.md](HOW_TO_RUN.md) - Method 1.**

## ✅ What's Fixed

1. **Load Sample Movies** - Now works with proper error handling
2. **Clear Database** - Fixed with better error handling and response checking
3. **Test LLM & Health Check** - Uses proxy endpoints to avoid CORS issues

## 🚀 Quick Start

### Step 1: Build and Start

```bash
# Build and start all services
docker compose -f docker-compose.combined.yml up -d --build

# Or without LLM (lower resources)
docker compose -f docker-compose.combined.yml up -d --build movie-booking-app raft-node1 raft-node2 raft-node3
```

### Step 2: Access the Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:9000
- **LLM Server**: http://localhost:8500 (if running)

### Step 3: Login

- **Admin**: `admin` / `123`
- **User**: `utkarsh` / `password123`

## 📋 Services

| Service | Port | Description |
|---------|------|-------------|
| `movie-booking-app` | 9000, 3000 | Combined frontend + backend |
| `raft-node1` | 50051 | Raft consensus node 1 |
| `raft-node2` | 50052 | Raft consensus node 2 |
| `raft-node3` | 50053 | Raft consensus node 3 |
| `llm-server` | 8500 | LLM AI assistant (optional) |

## 🔧 What Changed

### Backend (`Application_server/Application_server.py`)

1. **Added `httpx` import** for async HTTP requests
2. **Added proxy endpoints**:
   - `/proxy/llm/health` - LLM health check proxy
   - `/proxy/llm/ask` - LLM question proxy
   - `/proxy/raft/{node_id}/status` - Raft status proxy
   - `/admin/health/all` - Combined health check for all services
3. **Improved error handling** in `load_sample_data` and `clear_database`

### Frontend (`web/app.js`)

1. **Fixed `loadSampleMovies()`**:
   - Added response status checking
   - Better error messages
   - Auto-refresh after loading

2. **Fixed `clearDatabase()`**:
   - Added response status checking
   - Better error messages
   - Auto-refresh after clearing

3. **Fixed `testLLM()`**:
   - Uses proxy endpoint `/proxy/llm/health` and `/proxy/llm/ask`
   - Better error handling
   - Shows detailed status

4. **Fixed `checkHealth()`**:
   - Uses combined endpoint `/admin/health/all`
   - Checks all services through backend proxy
   - Better error messages

## 🛠️ Manual Testing

### Test Load Sample Movies

1. Login as admin
2. Click "Load Sample Movies"
3. Should see: "Loaded 15 sample movies!"
4. Movies table should refresh automatically

### Test Clear Database

1. Login as admin
2. Click "Clear Database"
3. Confirm the action
4. Should see: "Cleared X movies and Y bookings"
5. Tables should refresh automatically

### Test LLM Service

1. Login as admin
2. Click "Test LLM Service"
3. Should see:
   - ✓ Status: OK
   - ✓ Model: Qwen/Qwen2.5-0.5B
   - ✓ Model Loaded: Yes
   - ✓ Response: [LLM answer]

### Test System Health

1. Login as admin
2. Click "Check System Health"
3. Should see status for:
   - ✓ App Server: OK
   - ✓ LLM Server: OK (if running)
   - ✓ Raft Node 1: OK
   - ✓ Raft Node 2: OK
   - ✓ Raft Node 3: OK

## 📝 Files Created

- `Dockerfile.combined` - Combined frontend + backend Docker image
- `docker-compose.combined.yml` - Docker Compose for combined setup
- `start_combined.py` - Python script to run both services
- `COMBINED_SETUP.md` - This documentation

## 🔍 Troubleshooting

### Services Not Starting

```bash
# Check logs
docker compose -f docker-compose.combined.yml logs movie-booking-app

# Rebuild
docker compose -f docker-compose.combined.yml build --no-cache movie-booking-app
docker compose -f docker-compose.combined.yml up -d movie-booking-app
```

### Frontend Not Loading

1. Check if port 3000 is accessible: `curl http://localhost:3000`
2. Check browser console for errors
3. Verify backend is running: `curl http://localhost:9000/health`

### API Calls Failing

1. Check backend logs: `docker compose -f docker-compose.combined.yml logs movie-booking-app`
2. Verify CORS is enabled (should be automatic)
3. Check network connectivity between services

### LLM/Health Checks Failing

1. Verify LLM server is running: `docker compose -f docker-compose.combined.yml ps llm-server`
2. Check if services are on the same network
3. Verify proxy endpoints: `curl http://localhost:9000/proxy/llm/health`

## 🎯 Benefits of Combined Setup

1. **Simpler Deployment** - One container for frontend + backend
2. **No CORS Issues** - All requests go through backend
3. **Easier Development** - Single service to manage
4. **Better Error Handling** - Centralized error management
5. **Health Checks** - Combined health endpoint

## 📚 Next Steps

1. Test all features in the web UI
2. Verify bookings work correctly
3. Test with multiple users
4. Monitor logs for any issues

---

**Ready to use!** Access the application at http://localhost:3000

