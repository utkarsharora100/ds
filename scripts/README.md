# Scripts Documentation

All utility scripts for the Distributed Movie Booking System.

## 🚀 Quick Start Scripts

### `quickstart.sh`
**Purpose:** Complete automated setup and testing
**Usage:**
```bash
./scripts/quickstart.sh
```
**What it does:**
- Checks prerequisites (Docker, Python)
- Builds all containers
- Starts all services
- Loads sample data
- Runs health checks
- Provides access URLs

---

### `quickstart-optimized.sh`
**Purpose:** Optimized quick start with build caching
**Usage:**
```bash
./scripts/quickstart-optimized.sh
```
**What it does:**
- Same as quickstart.sh but with optimized build
- Uses Docker layer caching
- Faster subsequent builds

---

## 🔧 Fix & Maintenance Scripts

### `fix-raft-leader.sh`
**Purpose:** Fix Raft leader election bug
**Usage:**
```bash
./scripts/fix-raft-leader.sh
```
**What it does:**
- Stops Raft nodes
- Rebuilds with fixed election code
- Starts nodes
- Verifies only ONE leader elected

**When to use:** When multiple Raft nodes show as "leader"

---

### `fix-import-error.sh`
**Purpose:** Fix MongoDB import error in backend
**Usage:**
```bash
./scripts/fix-import-error.sh
```
**What it does:**
- Stops backend container
- Rebuilds with import path fix
- Starts backend
- Verifies MongoDB connection

**When to use:** When backend crashes with "ModuleNotFoundError: No module named 'mongodb_storage'"

---

### `start-with-mongodb.sh`
**Purpose:** Start entire system with MongoDB persistence
**Usage:**
```bash
./scripts/start-with-mongodb.sh
```
**What it does:**
- Starts MongoDB container
- Starts backend with MongoDB storage
- Starts Raft nodes
- Starts LLM server (optional)
- Verifies all services

---

### `apply-all-fixes.sh`
**Purpose:** Apply all known fixes at once
**Usage:**
```bash
./scripts/apply-all-fixes.sh
```
**What it does:**
- Applies MongoDB import fix
- Applies Raft leader election fix
- Rebuilds all containers
- Verifies system health

**When to use:** After pulling latest code changes

---

### `rebuild-with-fixes.sh`
**Purpose:** Complete rebuild with all fixes
**Usage:**
```bash
./scripts/rebuild-with-fixes.sh
```
**What it does:**
- Stops all containers
- Removes old containers and images
- Rebuilds everything from scratch
- Starts all services

**When to use:** When experiencing persistent issues

---

## 🩺 Health Check & Monitoring Scripts

### `check_health.sh`
**Purpose:** Comprehensive health check of all services
**Usage:**
```bash
./scripts/check_health.sh
```
**What it does:**
- Checks backend API health
- Checks MongoDB connection
- Checks Raft node status (identifies leader)
- Checks LLM server status
- Reports overall system health

**Output:**
```
✓ App Server: OK
✓ MongoDB: Connected
✓ Raft Node 1: Follower
✓ Raft Node 2: Leader  ← Only one!
✓ Raft Node 3: Follower
⚠ LLM Server: Starting up...
```

---

## 🗄️ Database Management Scripts

### `load_sample_data.sh`
**Purpose:** Load sample movies into the database
**Usage:**
```bash
./scripts/load_sample_data.sh --force
```
**What it does:**
- Logs in as admin
- Adds 15 sample movies across 3 cities
- Verifies data was loaded

**Options:**
- `--force` - Skip confirmation prompt

---

### `reset_database.sh`
**Purpose:** Clear all movies and bookings
**Usage:**
```bash
./scripts/reset_database.sh --force
```
**What it does:**
- Logs in as admin
- Clears all movies
- Clears all bookings
- Keeps user accounts intact

**Options:**
- `--force` - Skip confirmation prompt

---

## 🧪 Testing Scripts

### `test_llm_viability.sh`
**Purpose:** Test LLM service functionality
**Usage:**
```bash
./scripts/test_llm_viability.sh
```
**What it does:**
- Checks LLM server health
- Tests FAQ endpoint
- Tests chat endpoint
- Reports response times and quality

---

### `verify-code.sh`
**Purpose:** Verify code syntax and structure
**Usage:**
```bash
./scripts/verify-code.sh
```
**What it does:**
- Checks Python syntax
- Checks JavaScript syntax
- Verifies file structure
- Reports any issues

---

## 🔄 Project Management Scripts

### `reorganize-project.sh`
**Purpose:** Reorganize project structure
**Usage:**
```bash
./scripts/reorganize-project.sh
```
**What it does:**
- Moves all docs to docs/ folder
- Moves all scripts to scripts/ folder
- Creates documentation index
- Updates README.md

---

### `quick-fix.sh`
**Purpose:** Quick fix for common issues
**Usage:**
```bash
./scripts/quick-fix.sh
```
**What it does:**
- Restarts all services
- Clears Docker cache if needed
- Runs health checks
- Provides troubleshooting tips

---

## 📋 Script Usage Examples

### Complete Fresh Setup
```bash
# Clone repository
git clone https://github.com/utkarsharora100/ds.git
cd ds

# Run quickstart
./scripts/quickstart.sh

# Access web UI
# Open http://localhost:3000 in browser
```

### Fix Specific Issues
```bash
# Fix Raft leader election
./scripts/fix-raft-leader.sh

# Fix MongoDB import error
./scripts/fix-import-error.sh

# Check if everything is healthy
./scripts/check_health.sh
```

### Database Management
```bash
# Load sample movies
./scripts/load_sample_data.sh --force

# Reset database
./scripts/reset_database.sh --force

# Verify data
curl http://localhost:9000/data/movies
```

### Development Workflow
```bash
# Make code changes
vim Application_server/Application_server.py

# Rebuild affected service
docker compose build app-server

# Restart service
docker compose up -d app-server

# Check health
./scripts/check_health.sh
```

---

## 🎯 Common Workflows

### First Time Setup
```bash
./scripts/quickstart.sh
```

### Daily Development
```bash
# Start services
docker compose -f docker-compose.combined.yml up -d

# Check health
./scripts/check_health.sh

# Load test data
./scripts/load_sample_data.sh --force
```

### Troubleshooting
```bash
# Check what's wrong
./scripts/check_health.sh

# Apply all fixes
./scripts/apply-all-fixes.sh

# If still broken, complete rebuild
./scripts/rebuild-with-fixes.sh
```

### Testing
```bash
# Test LLM
./scripts/test_llm_viability.sh

# Verify code
./scripts/verify-code.sh

# Health check
./scripts/check_health.sh
```

---

## ⚙️ Making Scripts Executable

If scripts are not executable, run:
```bash
chmod +x scripts/*.sh
```

---

## 📝 Script Naming Convention

- `*.sh` - All scripts use bash
- `fix-*.sh` - Scripts that fix specific issues
- `*_*.sh` - Scripts for ongoing operations
- `check_*.sh` - Health check scripts
- `test_*.sh` - Testing scripts

---

## 🚨 Important Notes

1. **Always run scripts from project root**
   ```bash
   cd /path/to/ds
   ./scripts/scriptname.sh
   ```

2. **Check script output** - Most scripts provide detailed logs

3. **Use `--force` flag** - Some scripts require confirmation without this flag

4. **Check prerequisites** - quickstart.sh checks Docker, Python, etc.

5. **View logs** - If script fails, check:
   ```bash
   docker compose logs [service-name]
   ```

---

**Last Updated:** 2025-11-13
**Total Scripts:** 13
