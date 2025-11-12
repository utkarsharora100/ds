#!/bin/bash
# Quick Rebuild Script for Bug Fixes
# Run this after applying the backend fixes

set -e

echo "========================================"
echo "  REBUILDING WITH BUG FIXES"
echo "========================================"
echo ""
echo "Fixes applied:"
echo "  ✓ Admin sees all bookings with usernames"
echo "  ✓ Users see only their own bookings"  
echo "  ✓ RequestId displays correctly"
echo ""

# Ask which setup to rebuild
echo "Which setup are you using?"
echo "  1) Web UI (docker-compose.combined.yml)"
echo "  2) Desktop GUI (docker-compose.yml)"
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "Stopping containers..."
        docker compose -f docker-compose.combined.yml down
        
        echo ""
        echo "Rebuilding app-server (1-2 minutes)..."
        docker compose -f docker-compose.combined.yml build movie-booking-app
        
        echo ""
        echo "Starting all services..."
        docker compose -f docker-compose.combined.yml up -d
        
        echo ""
        echo "✅ Done! Web UI available at: http://localhost:3000"
        ;;
    2)
        echo ""
        echo "Stopping containers..."
        docker compose down
        
        echo ""
        echo "Rebuilding app-server (1-2 minutes)..."
        docker compose build app-server
        
        echo ""
        echo "Starting all services..."
        docker compose up -d
        
        echo ""
        echo "✅ Done! Run: python app.py"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "  TESTING INSTRUCTIONS"
echo "========================================"
echo ""
echo "1. Test System Health:"
echo "   - Login as admin/123"
echo "   - Click 'Check System Health'"
echo "   - Should show Raft nodes status"
echo ""
echo "2. Test Admin Bookings:"
echo "   - Login as admin/123"
echo "   - Load sample movies"
echo "   - Logout, register user1, book tickets"
echo "   - Logout, register user2, book tickets"
echo "   - Login as admin again"
echo "   - Check 'All User Bookings' - should show ALL bookings with USERNAME column"
echo ""
echo "3. Test User Bookings:"
echo "   - Login as user1"
echo "   - Check 'My Bookings' - should show ONLY user1's bookings"
echo "   - Logout, login as user2"
echo "   - Check 'My Bookings' - should show ONLY user2's bookings"
echo ""
echo "Check logs: docker compose logs app-server -f"
echo ""
