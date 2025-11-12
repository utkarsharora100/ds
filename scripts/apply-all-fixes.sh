#!/bin/bash
# Complete Fix Application Script
# Applies all fixes: Raft dependencies, Health check, Bookings, LLM chat

set -e

echo "======================================================================="
echo "  APPLYING ALL FIXES - Movie Booking System"
echo "======================================================================="
echo ""
echo "Fixes included:"
echo "  ✓ Raft nodes FastAPI dependency"
echo "  ✓ Health check improvements"
echo "  ✓ LLM service handling"
echo "  ✓ Admin bookings display"
echo "  ✓ User booking privacy"
echo "  ✓ AI Chatbox feature"
echo ""

# Ask which setup to rebuild
echo "Which setup are you using?"
echo "  1) Web UI (docker-compose.combined.yml)"
echo "  2) Desktop GUI (docker-compose.yml)"
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "=== Stopping containers ==="
        docker compose -f docker-compose.combined.yml down
        
        echo ""
        echo "=== Rebuilding services (this will take 2-3 minutes) ==="
        docker compose -f docker-compose.combined.yml build movie-booking-app raft-node1 raft-node2 raft-node3
        
        echo ""
        echo "=== Starting all services ==="
        docker compose -f docker-compose.combined.yml up -d
        
        echo ""
        echo "✅ Done! Services starting up..."
        echo ""
        echo "Web UI: http://localhost:3000"
        echo "API: http://localhost:9000"
        echo ""
        echo "Waiting for services to be ready (30 seconds)..."
        sleep 30
        
        echo ""
        echo "=== Checking Health ==="
        curl -s http://localhost:9000/health | python3 -m json.tool || echo "App server starting..."
        ;;
    2)
        echo ""
        echo "=== Stopping containers ==="
        docker compose down
        
        echo ""
        echo "=== Rebuilding services (this will take 2-3 minutes) ==="
        docker compose build app-server raft-node1 raft-node2 raft-node3
        
        echo ""
        echo "=== Starting all services ==="
        docker compose up -d
        
        echo ""
        echo "✅ Done! Services starting up..."
        echo ""
        echo "API: http://localhost:9000"
        echo "Run: python app.py (for desktop GUI)"
        echo ""
        echo "Waiting for services to be ready (30 seconds)..."
        sleep 30
        
        echo ""
        echo "=== Checking Health ==="
        curl -s http://localhost:9000/health | python3 -m json.tool || echo "App server starting..."
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "======================================================================="
echo "  TESTING INSTRUCTIONS"
echo "======================================================================="
echo ""
echo "1. System Health Check:"
echo "   • Login as admin/123"
echo "   • Click 'Check System Health'"
echo "   • Should show:"
echo "     ✓ App Server: OK"
echo "     ⚠️  LLM Server: Not Running (Optional Service)"
echo "     ✓ Raft Node 1/2/3: OK (State: follower/leader)"
echo ""
echo "2. Admin Bookings:"
echo "   • Login as admin → Load Sample Movies"
echo "   • Logout → Register user1 → Book tickets"
echo "   • Login as admin → Check 'All User Bookings'"
echo "   • Should show USERNAME column"
echo ""
echo "3. User Privacy:"
echo "   • Login as user1 → Check 'My Bookings'"
echo "   • Should show ONLY user1's bookings"
echo ""
echo "4. AI Chatbox (NEW!):"
echo "   • Click the 💬 button (bottom-right)"
echo "   • Ask: 'How do I book a ticket?'"
echo "   • Should get AI response (if LLM running)"
echo ""
echo "======================================================================="
echo "  VIEW LOGS"
echo "======================================================================="
echo ""
echo "# All services:"
if [ "$choice" = "1" ]; then
    echo "docker compose -f docker-compose.combined.yml logs -f"
else
    echo "docker compose logs -f"
fi
echo ""
echo "# Specific service:"
if [ "$choice" = "1" ]; then
    echo "docker compose -f docker-compose.combined.yml logs -f movie-booking-app"
    echo "docker compose -f docker-compose.combined.yml logs -f raft-node1"
else
    echo "docker compose logs -f app-server"
    echo "docker compose logs -f raft-node1"
fi
echo ""
echo "======================================================================="
echo "🎉 All fixes applied successfully!"
echo "======================================================================="
