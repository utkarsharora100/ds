# 🐳 Docker Installation Guide (Arch Linux)

## Quick Installation

```bash
# Install Docker
sudo pacman -S docker docker-compose

# Start Docker service
sudo systemctl start docker.service

# Enable Docker to start on boot
sudo systemctl enable docker.service

# Add your user to docker group (to run without sudo)
sudo usermod -aG docker $USER

# Log out and log back in for group changes to take effect
# Or run: newgrp docker
```

## Verify Installation

```bash
# Check Docker version
docker --version

# Check Docker Compose version (V1 - standalone)
docker-compose --version

# OR check Docker Compose V2 (integrated)
docker compose version

# Test Docker
docker run hello-world
```

## Start the Application

After Docker is installed and running:

```bash
# Using Docker Compose V1 (standalone)
docker-compose up -d

# OR using Docker Compose V2 (integrated - newer)
docker compose up -d
```

## Troubleshooting

### Permission Denied Error

```bash
# If you see: "permission denied while trying to connect to Docker daemon"
sudo usermod -aG docker $USER
newgrp docker

# Or restart your session
```

### Docker Service Not Running

```bash
# Check service status
sudo systemctl status docker

# Start service
sudo systemctl start docker

# Check for errors
journalctl -u docker.service -f
```

### Cannot Connect to Docker Daemon

```bash
# Make sure Docker service is running
sudo systemctl start docker

# Check if docker socket exists
ls -la /var/run/docker.sock
```

## Alternative: Podman (Docker Alternative)

If you prefer Podman (Docker-compatible):

```bash
# Install Podman
sudo pacman -S podman podman-compose

# Use podman-compose instead
podman-compose up -d
```

## After Installation

Once Docker is installed, return to the main documentation:
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
- **Full Guide**: See [README.md](README.md)

---

**System Requirements:**
- 4GB RAM minimum (6GB recommended)
- 10GB free disk space
- Internet connection (for first-time model download)
