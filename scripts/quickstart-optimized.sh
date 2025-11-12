#!/bin/bash
# Quick Start Script for Optimized Docker Build
# Run this for the fastest way to get started

set -e  # Exit on error

echo "================================================"
echo "  Movie Booking System - Optimized Quick Start"
echo "================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "   Please start Docker and try again"
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Ask user which setup they want
echo "Choose your setup:"
echo "  1) Web UI (Recommended - Fastest)"
echo "  2) Desktop GUI (Traditional)"
echo "  3) Web UI without LLM (Ultra Fast)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "Starting Web UI with all services..."
        docker compose -f docker-compose.combined.yml up -d --build
        echo ""
        echo "✅ Services started!"
        echo ""
        echo "Access the application:"
        echo "  → Web UI: http://localhost:3000"
        echo "  → API: http://localhost:9000"
        echo ""
        echo "Login credentials:"
        echo "  → Admin: admin / 123"
        echo "  → User: utkarsh / password123"
        ;;
    2)
        echo ""
        echo "Starting backend services for Desktop GUI..."
        docker compose up -d --build
        echo ""
        echo "✅ Backend services started!"
        echo ""
        echo "Now run the GUI:"
        echo "  python app.py         # Single window"
        echo "  python app_multi.py   # Multi window"
        echo ""
        echo "Login credentials:"
        echo "  → Admin: admin / 123"
        echo "  → User: utkarsh / password123"
        ;;
    3)
        echo ""
        echo "Starting Web UI without LLM (Ultra Fast)..."
        docker compose -f docker-compose.combined.yml up -d movie-booking-app raft-node1 raft-node2 raft-node3
        echo ""
        echo "✅ Services started (without LLM)!"
        echo ""
        echo "Access the application:"
        echo "  → Web UI: http://localhost:3000"
        echo "  → API: http://localhost:9000"
        echo ""
        echo "⚠️  Note: AI Assistant will not be available"
        echo ""
        echo "Login credentials:"
        echo "  → Admin: admin / 123"
        echo "  → User: utkarsh / password123"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "================================================"
echo "Useful Commands:"
echo "================================================"
echo "  View logs:    docker compose logs -f"
echo "  Stop:         docker compose down"
echo "  Health check: curl http://localhost:9000/health"
echo ""
