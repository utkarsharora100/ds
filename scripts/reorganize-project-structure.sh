#!/bin/bash
# Project Structure Reorganization Script
# Moves Dockerfiles to docker/ and requirements files to requirements/

echo "=========================================================="
echo "📁 Project Structure Reorganization"
echo "=========================================================="
echo ""

cd "$(dirname "$0")/.."

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}This script will:${NC}"
echo "  1. Create docker/ folder for all Dockerfiles"
echo "  2. Create requirements/ folder for all requirements files"
echo "  3. Move 4 Dockerfiles to docker/"
echo "  4. Move 5 requirements files to requirements/"
echo "  5. Update references in docker-compose files"
echo "  6. Update references in Dockerfiles"
echo ""
echo -e "${YELLOW}Files to move:${NC}"
echo "  Dockerfiles:"
echo "    • Dockerfile.app → docker/Dockerfile.app"
echo "    • Dockerfile.raft → docker/Dockerfile.raft"
echo "    • Dockerfile.llm → docker/Dockerfile.llm"
echo "    • Dockerfile.combined → docker/Dockerfile.combined"
echo ""
echo "  Requirements:"
echo "    • requirements.txt → requirements/requirements.txt"
echo "    • requirements-app.txt → requirements/requirements-app.txt"
echo "    • requirements-llm.txt → requirements/requirements-llm.txt"
echo "    • requirements-raft.txt → requirements/requirements-raft.txt"
echo "    • requirements-base.txt → requirements/requirements-base.txt"
echo ""
echo -e "${RED}WARNING: This will modify your project structure!${NC}"
echo -e "${YELLOW}Make sure to commit your changes first!${NC}"
echo ""

read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

# Step 1: Create directories
echo -e "${YELLOW}Step 1: Creating directories...${NC}"

if [ ! -d "docker" ]; then
    mkdir docker
    echo "  ✓ Created docker/"
else
    echo "  ✓ docker/ already exists"
fi

if [ ! -d "requirements" ]; then
    mkdir requirements
    echo "  ✓ Created requirements/"
else
    echo "  ✓ requirements/ already exists"
fi

echo ""

# Step 2: Move Dockerfiles
echo -e "${YELLOW}Step 2: Moving Dockerfiles...${NC}"

for dockerfile in Dockerfile.app Dockerfile.raft Dockerfile.llm Dockerfile.combined; do
    if [ -f "$dockerfile" ]; then
        mv "$dockerfile" "docker/$dockerfile"
        echo "  ✓ Moved $dockerfile → docker/$dockerfile"
    else
        echo "  ⚠️  $dockerfile not found (may already be moved)"
    fi
done

echo ""

# Step 3: Move requirements files
echo -e "${YELLOW}Step 3: Moving requirements files...${NC}"

for reqfile in requirements.txt requirements-app.txt requirements-llm.txt requirements-raft.txt requirements-base.txt; do
    if [ -f "$reqfile" ]; then
        mv "$reqfile" "requirements/$reqfile"
        echo "  ✓ Moved $reqfile → requirements/$reqfile"
    else
        echo "  ⚠️  $reqfile not found (may already be moved)"
    fi
done

echo ""

# Step 4: Update docker-compose.yml
echo -e "${YELLOW}Step 4: Updating docker-compose.yml...${NC}"

if [ -f "docker-compose.yml" ]; then
    # Backup first
    cp docker-compose.yml docker-compose.yml.backup
    echo "  ✓ Created backup: docker-compose.yml.backup"

    # Update Dockerfile paths
    sed -i.tmp 's|dockerfile: Dockerfile.app|dockerfile: docker/Dockerfile.app|g' docker-compose.yml
    sed -i.tmp 's|dockerfile: Dockerfile.raft|dockerfile: docker/Dockerfile.raft|g' docker-compose.yml
    sed -i.tmp 's|dockerfile: Dockerfile.llm|dockerfile: docker/Dockerfile.llm|g' docker-compose.yml
    rm docker-compose.yml.tmp 2>/dev/null

    echo "  ✓ Updated dockerfile paths in docker-compose.yml"
else
    echo "  ⚠️  docker-compose.yml not found"
fi

echo ""

# Step 5: Update docker-compose.combined.yml
echo -e "${YELLOW}Step 5: Updating docker-compose.combined.yml...${NC}"

if [ -f "docker-compose.combined.yml" ]; then
    # Backup first
    cp docker-compose.combined.yml docker-compose.combined.yml.backup
    echo "  ✓ Created backup: docker-compose.combined.yml.backup"

    # Update Dockerfile paths
    sed -i.tmp 's|dockerfile: Dockerfile.combined|dockerfile: docker/Dockerfile.combined|g' docker-compose.combined.yml
    sed -i.tmp 's|dockerfile: Dockerfile.raft|dockerfile: docker/Dockerfile.raft|g' docker-compose.combined.yml
    sed -i.tmp 's|dockerfile: Dockerfile.llm|dockerfile: docker/Dockerfile.llm|g' docker-compose.combined.yml
    rm docker-compose.combined.yml.tmp 2>/dev/null

    echo "  ✓ Updated dockerfile paths in docker-compose.combined.yml"
else
    echo "  ⚠️  docker-compose.combined.yml not found"
fi

echo ""

# Step 6: Update Dockerfile.app
echo -e "${YELLOW}Step 6: Updating Dockerfile references...${NC}"

if [ -f "docker/Dockerfile.app" ]; then
    cp docker/Dockerfile.app docker/Dockerfile.app.backup
    sed -i.tmp 's|COPY requirements-app.txt|COPY requirements/requirements-app.txt|g' docker/Dockerfile.app
    rm docker/Dockerfile.app.tmp 2>/dev/null
    echo "  ✓ Updated docker/Dockerfile.app"
fi

if [ -f "docker/Dockerfile.raft" ]; then
    cp docker/Dockerfile.raft docker/Dockerfile.raft.backup
    sed -i.tmp 's|COPY requirements-raft.txt|COPY requirements/requirements-raft.txt|g' docker/Dockerfile.raft
    rm docker/Dockerfile.raft.tmp 2>/dev/null
    echo "  ✓ Updated docker/Dockerfile.raft"
fi

if [ -f "docker/Dockerfile.llm" ]; then
    cp docker/Dockerfile.llm docker/Dockerfile.llm.backup
    sed -i.tmp 's|COPY requirements-llm.txt|COPY requirements/requirements-llm.txt|g' docker/Dockerfile.llm
    rm docker/Dockerfile.llm.tmp 2>/dev/null
    echo "  ✓ Updated docker/Dockerfile.llm"
fi

if [ -f "docker/Dockerfile.combined" ]; then
    cp docker/Dockerfile.combined docker/Dockerfile.combined.backup
    sed -i.tmp 's|COPY requirements-base.txt|COPY requirements/requirements-base.txt|g' docker/Dockerfile.combined
    rm docker/Dockerfile.combined.tmp 2>/dev/null
    echo "  ✓ Updated docker/Dockerfile.combined"
fi

echo ""

# Step 7: Verification
echo -e "${YELLOW}Step 7: Verifying structure...${NC}"

echo ""
echo "docker/ folder:"
ls -1 docker/ 2>/dev/null | while read file; do echo "  ✓ $file"; done

echo ""
echo "requirements/ folder:"
ls -1 requirements/ 2>/dev/null | while read file; do echo "  ✓ $file"; done

echo ""
echo "=========================================================="
echo -e "${GREEN}✅ Reorganization Complete!${NC}"
echo "=========================================================="
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Test Docker builds:"
echo "     docker compose -f docker-compose.combined.yml build"
echo ""
echo "  2. If successful, remove backup files:"
echo "     rm docker-compose.yml.backup"
echo "     rm docker-compose.combined.yml.backup"
echo "     rm docker/Dockerfile.*.backup"
echo ""
echo "  3. Commit changes:"
echo "     git add docker/ requirements/"
echo "     git add docker-compose.yml docker-compose.combined.yml"
echo "     git commit -m 'Reorganize: Move Dockerfiles and requirements to dedicated folders'"
echo ""
echo -e "${YELLOW}If something went wrong:${NC}"
echo "  Restore from backups:"
echo "    mv docker-compose.yml.backup docker-compose.yml"
echo "    mv docker-compose.combined.yml.backup docker-compose.combined.yml"
echo "    mv docker/*.backup docker/ (and rename)"
echo ""
