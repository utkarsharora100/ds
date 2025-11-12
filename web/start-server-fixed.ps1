# Fixed Web Server Startup Script for Windows
# Uses port 3000 and binds to localhost to avoid permission issues

Write-Host "🎬 Starting Movie Booking System Web Server..." -ForegroundColor Cyan
Write-Host ""

# Check if we're in the web directory
if (-not (Test-Path "index.html")) {
    Write-Host "❌ Error: index.html not found!" -ForegroundColor Red
    Write-Host "Please run this script from the 'web' directory." -ForegroundColor Yellow
    exit 1
}

# Find Python
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    Write-Host "❌ Error: Python not found!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found Python: $pythonCmd" -ForegroundColor Green
Write-Host ""

# Try ports in order of preference
$ports = @(3000, 5000, 8888, 9001, 7000)

foreach ($port in $ports) {
    Write-Host "🔍 Trying port $port..." -ForegroundColor Yellow
    
    # Check if port is available
    $portInUse = netstat -ano | findstr ":$port "
    
    if ($portInUse) {
        Write-Host "   Port $port is in use, trying next..." -ForegroundColor Yellow
        continue
    }
    
    Write-Host "✅ Starting server on port $port..." -ForegroundColor Green
    Write-Host "🌐 Open in browser: http://localhost:$port" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    
    # Try binding to localhost specifically (more reliable)
    try {
        # Python 3.8+ supports --bind flag
        & $pythonCmd -m http.server $port --bind 127.0.0.1
        break
    } catch {
        # Fallback: try without bind flag (older Python)
        try {
            & $pythonCmd -m http.server $port
            break
        } catch {
            Write-Host "❌ Failed on port $port, trying next..." -ForegroundColor Red
            continue
        }
    }
}

Write-Host ""
Write-Host "❌ Could not start server on any available port." -ForegroundColor Red
Write-Host "Please check your firewall settings or try running as Administrator." -ForegroundColor Yellow

