# Windows Web Server Startup Script
# Fixes port 8080 permission issue by using port 8000

Write-Host "🎬 Starting Movie Booking System Web Server..." -ForegroundColor Cyan
Write-Host ""

# Check if we're in the web directory
if (-not (Test-Path "index.html")) {
    Write-Host "❌ Error: index.html not found!" -ForegroundColor Red
    Write-Host "Please run this script from the 'web' directory." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  cd web" -ForegroundColor White
    Write-Host "  .\start-server.ps1" -ForegroundColor White
    exit 1
}

# Try to find Python
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    Write-Host "❌ Error: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.7+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found Python: $pythonCmd" -ForegroundColor Green
Write-Host ""

# Port to use (8000 instead of 8080 to avoid Windows reserved ports)
$port = 8000

Write-Host "📡 Starting server on port $port..." -ForegroundColor Cyan
Write-Host "   (Port 8080 is reserved by Windows)" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Open in browser: http://localhost:$port" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
try {
    & $pythonCmd -m http.server $port
} catch {
    Write-Host ""
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative ports to try:" -ForegroundColor Yellow
    Write-Host "  $pythonCmd -m http.server 3000" -ForegroundColor White
    Write-Host "  $pythonCmd -m http.server 5000" -ForegroundColor White
    Write-Host "  $pythonCmd -m http.server 8888" -ForegroundColor White
    exit 1
}

