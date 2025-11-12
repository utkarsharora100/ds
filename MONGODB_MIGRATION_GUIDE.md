# MongoDB Migration Guide - Complete Implementation

## 🎯 Overview

**Date:** 2025-11-13
**Migration:** In-Memory Storage → MongoDB
**Status:** ✅ Complete

This guide documents the complete migration from in-memory storage to MongoDB for persistent, reliable data storage.

---

## ✅ What Was Changed

### 1. Storage Layer (`mongodb_storage.py`)

Created a new MongoDB storage module that handles:
- ✅ User management (registration, authentication)
- ✅ Session management (login tokens)
- ✅ Movie management (add, list, update seats)
- ✅ Booking management (create, list by user/admin)
- ✅ Sample data loading

**File:** [Application_server/mongodb_storage.py](Application_server/mongodb_storage.py)

**Key Features:**
- Automatic indexes for performance
- Default admin user creation
- Atomic seat updates
- Role-based data access

### 2. Application Server (`Application_server.py`)

Completely rewritten to use MongoDB:
- ✅ Removed in-memory dictionaries
- ✅ All data now stored in MongoDB
- ✅ Sessions persist across restarts
- ✅ Bookings persist across restarts
- ✅ Better error handling

**File:** [Application_server/Application_server.py](Application_server/Application_server.py)

### 3. Dependencies (`requirements-base.txt`)

Added MongoDB drivers:
```
pymongo==4.6.1
dnspython==2.4.2
```

### 4. Docker Compose Files

**Both files updated:**
- [docker-compose.yml](docker-compose.yml) - Desktop GUI setup
- [docker-compose.combined.yml](docker-compose.combined.yml) - Web UI setup

**Changes:**
- ✅ Added MongoDB service (mongo:7.0)
- ✅ Added persistent volume for MongoDB data
- ✅ Added `MONGODB_URL` environment variable
- ✅ Added health checks for MongoDB
- ✅ Updated dependencies

---

## 🚀 How to Use the New System

### Step 1: Stop Existing Containers

```bash
cd "/Users/aniketsaxena/Desktop/untitled folder/SOFTWARE SYSTEM/Semester 1/AOS/project/v2/ds"

# For Web UI:
docker-compose -f docker-compose.combined.yml down

# For Desktop GUI:
docker-compose down
```

### Step 2: Pull MongoDB Image

```bash
docker pull mongo:7.0
```

### Step 3: Build and Start Services

**For Web UI:**
```bash
# Build with no cache to ensure fresh dependencies
docker-compose -f docker-compose.combined.yml build --no-cache movie-booking-app

# Start all services
docker-compose -f docker-compose.combined.yml up -d

# Check status
docker-compose -f docker-compose.combined.yml ps
```

**For Desktop GUI:**
```bash
# Build with no cache
docker-compose build --no-cache app-server

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Step 4: Verify MongoDB is Running

```bash
# Check MongoDB health
docker exec movie-booking-mongodb mongosh --eval "db.adminCommand('ping')"

# Expected output:
# { ok: 1 }
```

### Step 5: Verify Application Server

```bash
# Check app server health
curl http://localhost:9000/health

# Expected output:
# {"status":"healthy","service":"application-server","database":"mongodb"}
```

### Step 6: Test Login

**Open browser:**
```
http://localhost:3000  # For Web UI
or
python app.py          # For Desktop GUI
```

**Test credentials:**
- Username: `admin`
- Password: `123`

**Or register a new user!**

---

## 🔥 Key Improvements

### Before (In-Memory)
❌ Data lost on restart
❌ No persistence
❌ Limited scalability
❌ Sessions lost on restart
❌ Bookings lost on restart

### After (MongoDB)
✅ Data persists across restarts
✅ Professional database
✅ Scalable architecture
✅ Sessions persist
✅ Bookings persist
✅ Indexed queries (fast)
✅ Atomic operations
✅ Transaction support

---

## 📊 MongoDB Collections

The system uses 4 collections:

### 1. `users` Collection
```javascript
{
  username: "alice",
  password: "password123",  // Note: In production, use bcrypt!
  created_at: 1731501234.567
}
```

**Indexes:**
- `username` (unique)

### 2. `sessions` Collection
```javascript
{
  token: "uuid-token-here",
  username: "alice",
  created_at: 1731501234.567
}
```

**Indexes:**
- `token` (unique)

### 3. `movies` Collection
```javascript
{
  movie: "Inception",
  city: "New York",
  seats: 50,
  created_at: 1731501234.567
}
```

**Indexes:**
- `(movie, city)` (unique composite)

### 4. `bookings` Collection
```javascript
{
  id: "uuid-booking-id",
  requestId: "req-1731501234-abc",
  data: {
    user: "alice",
    username: "alice",
    movie: "Inception",
    city: "New York",
    seats: 2,
    timestamp: 1731501234.567
  },
  created_at: 1731501234.567
}
```

**Indexes:**
- `data.user`
- `requestId`

---

## 🧪 Testing Guide

### Test 1: User Registration
```bash
curl -X POST http://localhost:9000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'

# Expected:
# {"status":"success","message":"User created"}
```

### Test 2: User Login
```bash
curl -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}'

# Expected:
# {"status":"success","token":"some-uuid-token","user":"admin"}
```

### Test 3: Add Movie (as admin)
```bash
# First login to get token
TOKEN="your-admin-token-here"

curl -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$TOKEN\",\"movie\":\"Test Movie\",\"city\":\"Test City\",\"seats\":100}"

# Expected:
# {"status":"success"}
```

### Test 4: Load Sample Movies
```bash
curl -X POST http://localhost:9000/admin/load_sample_data \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$TOKEN\"}"

# Expected:
# {"status":"success","message":"Sample data loaded successfully","loaded":{"movies":15}}
```

### Test 5: Book Tickets
```bash
# Login as regular user first
curl -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'

# Get token, then book
USER_TOKEN="user-token-here"

curl -X POST http://localhost:9000/business \
  -H "Content-Type: application/json" \
  -d "{
    \"requestId\":\"req-test-123\",
    \"payload\":{
      \"type\":\"book_seat\",
      \"data\":{\"movie\":\"Inception\",\"city\":\"New York\",\"seats\":2}
    },
    \"context\":{\"token\":\"$USER_TOKEN\"}
  }"

# Expected:
# {"status":"success","booking_id":"some-uuid","requestId":"req-test-123"}
```

### Test 6: Verify Persistence

```bash
# 1. Make some bookings
# 2. Restart containers
docker-compose restart movie-booking-app

# 3. Check bookings are still there
curl "http://localhost:9000/data/bookings?token=$TOKEN"

# Bookings should still be there! ✅
```

---

## 🔍 MongoDB Commands

### Connect to MongoDB Shell
```bash
docker exec -it movie-booking-mongodb mongosh
```

### View All Databases
```javascript
show dbs
```

### Switch to Movie Booking Database
```javascript
use movie_booking
```

### View Collections
```javascript
show collections
```

### Count Users
```javascript
db.users.countDocuments()
```

### List All Users
```javascript
db.users.find().pretty()
```

### List All Movies
```javascript
db.movies.find().pretty()
```

### List All Bookings
```javascript
db.bookings.find().pretty()
```

### Find Bookings for Specific User
```javascript
db.bookings.find({"data.user": "alice"}).pretty()
```

### Clear All Bookings
```javascript
db.bookings.deleteMany({})
```

### Clear All Movies
```javascript
db.movies.deleteMany({})
```

---

## 🛠️ Troubleshooting

### Issue: MongoDB Container Not Starting

**Check logs:**
```bash
docker logs movie-booking-mongodb
```

**Solution:**
```bash
# Remove old container and volume
docker-compose down -v
docker volume rm ds_mongodb-data

# Start fresh
docker-compose up -d mongodb
```

### Issue: App Server Can't Connect to MongoDB

**Error:** `Failed to initialize MongoDB: ...`

**Check:**
1. Is MongoDB running?
   ```bash
   docker ps | grep mongodb
   ```

2. Can app-server reach MongoDB?
   ```bash
   docker exec movie-app-server ping -c 1 mongodb
   ```

**Solution:**
```bash
# Restart in correct order
docker-compose restart mongodb
sleep 10
docker-compose restart movie-booking-app
```

### Issue: "Module 'pymongo' not found"

**Cause:** Container built before requirements were updated

**Solution:**
```bash
# Rebuild with no cache
docker-compose build --no-cache movie-booking-app
docker-compose up -d
```

### Issue: Login Still Not Working

**Check:**
1. Frontend JavaScript fixed? (app.js line 605)
2. Browser cache cleared? (`Ctrl+Shift+R`)
3. Backend running?
   ```bash
   curl http://localhost:9000/health
   ```

4. Check backend logs:
   ```bash
   docker logs movie-booking-combined --tail=50
   ```

---

## 📝 Default Credentials

The system automatically creates these users:

| Username | Password | Role |
|----------|----------|------|
| admin | 123 | Admin |
| utkarsh | password123 | Regular User |

You can register additional users through the UI or API.

---

## 🔒 Security Notes

**⚠️ IMPORTANT FOR PRODUCTION:**

1. **Passwords:** Currently stored as plain text. For production:
   ```python
   from passlib.hash import bcrypt
   hashed = bcrypt.hash(password)
   ```

2. **MongoDB Authentication:** Enable authentication:
   ```yaml
   mongodb:
     environment:
       - MONGO_INITDB_ROOT_USERNAME=admin
       - MONGO_INITDB_ROOT_PASSWORD=strongpassword
   ```

3. **Session Expiry:** Add TTL index:
   ```python
   db.sessions.create_index("created_at", expireAfterSeconds=86400)
   ```

4. **Rate Limiting:** Add rate limiting for login attempts

5. **Input Validation:** Already using Pydantic, but add more checks

---

## 📦 Backup and Restore

### Backup MongoDB Data
```bash
# Create backup
docker exec movie-booking-mongodb mongodump --out=/backup

# Copy to host
docker cp movie-booking-mongodb:/backup ./mongodb-backup
```

### Restore MongoDB Data
```bash
# Copy backup to container
docker cp ./mongodb-backup movie-booking-mongodb:/backup

# Restore
docker exec movie-booking-mongodb mongorestore /backup
```

---

## 🎉 Summary

### Files Created:
1. ✅ [Application_server/mongodb_storage.py](Application_server/mongodb_storage.py) - MongoDB storage module
2. ✅ [Application_server/Application_server_mongodb.py](Application_server/Application_server_mongodb.py) - Backup of new version
3. ✅ [MONGODB_MIGRATION_GUIDE.md](MONGODB_MIGRATION_GUIDE.md) - This file

### Files Modified:
1. ✅ [Application_server/Application_server.py](Application_server/Application_server.py) - Now uses MongoDB
2. ✅ [requirements-base.txt](requirements-base.txt) - Added pymongo
3. ✅ [docker-compose.yml](docker-compose.yml) - Added MongoDB service
4. ✅ [docker-compose.combined.yml](docker-compose.combined.yml) - Added MongoDB service
5. ✅ [web/app.js](web/app.js) - Fixed JavaScript syntax error (line 605)

### Benefits:
- ✅ **Persistent Storage:** Data survives restarts
- ✅ **Professional Database:** MongoDB is production-grade
- ✅ **Better Performance:** Indexed queries
- ✅ **Scalable:** Can handle high load
- ✅ **Reliable:** ACID-compliant operations
- ✅ **Login Fixed:** JavaScript syntax error resolved

---

## 🚀 Quick Start Commands

**Start everything:**
```bash
cd "/Users/aniketsaxena/Desktop/untitled folder/SOFTWARE SYSTEM/Semester 1/AOS/project/v2/ds"

# Web UI
docker-compose -f docker-compose.combined.yml up -d --build

# Desktop GUI
docker-compose up -d --build
python app.py
```

**Access:**
- Web UI: http://localhost:3000
- Backend API: http://localhost:9000
- MongoDB: mongodb://localhost:27017

**Login:**
- Username: `admin`
- Password: `123`

---

**Migration Complete!** 🎉
**All data now persists in MongoDB!**
**Login functionality restored!**

Last Updated: 2025-11-13
Version: 2.0 (MongoDB)
