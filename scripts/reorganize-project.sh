#!/bin/bash
# Project Reorganization Script
# Moves all documentation and scripts to their proper folders

echo "=================================================="
echo "📁 Reorganizing Project Structure"
echo "=================================================="
echo ""

cd "$(dirname "$0")/.."

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Moving documentation files to docs/ folder...${NC}"
echo ""

# Documentation files to move (excluding README.md)
DOCS_TO_MOVE=(
    "DOCKER_OPTIMIZATION.md"
    "FIXES_APPLIED.md"
    "BEFORE_AFTER_COMPARISON.md"
    "FIXES_SUMMARY_V2.md"
    "COMPLETE_FIX_GUIDE.md"
    "URGENT_FIX.md"
    "SYNTAX_ERROR_FIXED.md"
    "MONGODB_MIGRATION_GUIDE.md"
    "IMPORT_ERROR_FIX.md"
    "RAFT_FIX_BEFORE_AFTER.md"
    "COMPREHENSIVE_CHANGES_SUMMARY.md"
)

for doc in "${DOCS_TO_MOVE[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "${BLUE}Moving:${NC} $doc → docs/$doc"
        mv "$doc" "docs/$doc"
    else
        echo -e "${YELLOW}Skipped:${NC} $doc (not found)"
    fi
done

echo ""
echo -e "${YELLOW}Step 2: Moving script files to scripts/ folder...${NC}"
echo ""

# Script files to move
SCRIPTS_TO_MOVE=(
    "quickstart-optimized.sh"
    "rebuild-with-fixes.sh"
    "apply-all-fixes.sh"
    "verify-code.sh"
    "quick-fix.sh"
    "start-with-mongodb.sh"
    "fix-import-error.sh"
    "fix-raft-leader.sh"
)

for script in "${SCRIPTS_TO_MOVE[@]}"; do
    if [ -f "$script" ]; then
        echo -e "${BLUE}Moving:${NC} $script → scripts/$script"
        mv "$script" "scripts/$script"
        chmod +x "scripts/$script"
    else
        echo -e "${YELLOW}Skipped:${NC} $script (not found)"
    fi
done

echo ""
echo -e "${YELLOW}Step 3: Creating documentation index...${NC}"
echo ""

# Create docs/INDEX.md
cat > docs/INDEX.md <<'EOF'
# Documentation Index

Complete guide to all documentation in this project.

## 📚 Main Documentation

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - 2-minute quick start guide
- **[HOW_TO_RUN.md](HOW_TO_RUN.md)** - Detailed step-by-step instructions
- **[COMBINED_SETUP.md](COMBINED_SETUP.md)** - Web UI setup guide

### System Architecture
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture
- **[CLIENT_VIEW.md](CLIENT_VIEW.md)** - Client API reference

### Docker & Deployment
- **[DOCKER.md](DOCKER.md)** - Docker setup and configuration
- **[DOCKER_STEPS.md](DOCKER_STEPS.md)** - Complete Docker command reference
- **[DOCKER_OPTIMIZATION.md](DOCKER_OPTIMIZATION.md)** - Build time optimizations

### Reference
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command and port cheat sheet

## 🔧 Recent Fixes & Changes

### Comprehensive Guides
- **[COMPREHENSIVE_CHANGES_SUMMARY.md](COMPREHENSIVE_CHANGES_SUMMARY.md)** - Complete overview of all recent fixes
- **[MONGODB_MIGRATION_GUIDE.md](MONGODB_MIGRATION_GUIDE.md)** - MongoDB migration details
- **[RAFT_FIX_BEFORE_AFTER.md](RAFT_FIX_BEFORE_AFTER.md)** - Raft leader election fix
- **[IMPORT_ERROR_FIX.md](IMPORT_ERROR_FIX.md)** - MongoDB import error fix

### Detailed Fix Documentation
- **[FIXES_SUMMARY.md](FIXES_SUMMARY.md)** - Summary of all fixes
- **[FIXES_SUMMARY_V2.md](FIXES_SUMMARY_V2.md)** - Updated fix summary
- **[FIXES_APPLIED.md](FIXES_APPLIED.md)** - Applied fixes list
- **[BEFORE_AFTER_COMPARISON.md](BEFORE_AFTER_COMPARISON.md)** - Before/after comparisons
- **[COMPLETE_FIX_GUIDE.md](COMPLETE_FIX_GUIDE.md)** - Complete fix guide
- **[URGENT_FIX.md](URGENT_FIX.md)** - Urgent fix documentation
- **[SYNTAX_ERROR_FIXED.md](SYNTAX_ERROR_FIXED.md)** - JavaScript syntax fix

## 📖 Reading Order for New Users

1. Start with [QUICKSTART.md](QUICKSTART.md) for quick setup
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
3. Use [HOW_TO_RUN.md](HOW_TO_RUN.md) for detailed running instructions
4. Check [COMPREHENSIVE_CHANGES_SUMMARY.md](COMPREHENSIVE_CHANGES_SUMMARY.md) for recent fixes
5. Refer to [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for commands

## 📖 Reading Order for Debugging

1. Check [COMPREHENSIVE_CHANGES_SUMMARY.md](COMPREHENSIVE_CHANGES_SUMMARY.md) first
2. Look at specific fix guides:
   - MongoDB issues → [MONGODB_MIGRATION_GUIDE.md](MONGODB_MIGRATION_GUIDE.md)
   - Raft issues → [RAFT_FIX_BEFORE_AFTER.md](RAFT_FIX_BEFORE_AFTER.md)
   - Import errors → [IMPORT_ERROR_FIX.md](IMPORT_ERROR_FIX.md)
3. Check [FIXES_SUMMARY.md](FIXES_SUMMARY.md) for all known issues

## 🛠️ Script Documentation

See [../scripts/README.md](../scripts/README.md) for all available scripts.

---

**Last Updated:** 2025-11-13
**Total Documentation Files:** 21
EOF

echo -e "${GREEN}✓ Created docs/INDEX.md${NC}"

echo ""
echo -e "${YELLOW}Step 4: Creating scripts index...${NC}"
echo ""

# Create scripts/README.md
cat > scripts/README.md <<'EOF'
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
EOF

echo -e "${GREEN}✓ Created scripts/README.md${NC}"

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Reorganization Complete!${NC}"
echo "=================================================="
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "  • Documentation moved to docs/"
echo "  • Scripts moved to scripts/"
echo "  • Created docs/INDEX.md"
echo "  • Created scripts/README.md"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Check docs/INDEX.md for documentation index"
echo "  2. Check scripts/README.md for script documentation"
echo "  3. Update main README.md if needed"
echo ""
