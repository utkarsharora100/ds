@echo off
REM Quick Start Script for Distributed Movie Booking System (Windows)

echo ================================================
echo   Distributed Movie Booking System - Quick Start
echo ================================================
echo.

echo Choose an option:
echo 1. Full System (GUI + Application Server + 3 Raft Nodes)
echo 2. Application Server Only
echo 3. Raft Nodes Only (3 nodes)
echo 4. GUI Only
echo 5. LLM Server Only
echo 6. Stop All Components
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto full_system
if "%choice%"=="2" goto app_server
if "%choice%"=="3" goto raft_nodes
if "%choice%"=="4" goto gui_only
if "%choice%"=="5" goto llm_server
if "%choice%"=="6" goto stop_all
goto invalid

:full_system
echo.
echo Starting Full System...
echo.

REM Start Application Server
start "Application Server" cmd /k python Application_server/Application_server.py

timeout /t 3 /nobreak > nul

REM Start Raft Nodes
start "Raft Node 1" cmd /k python main.py node1
start "Raft Node 2" cmd /k python main.py node2
start "Raft Node 3" cmd /k python main.py node3

echo Waiting for services to initialize (5 seconds)...
timeout /t 5 /nobreak > nul

echo Starting GUI Application...
python app.py
goto end

:app_server
echo.
echo Starting Application Server...
python Application_server/Application_server.py
goto end

:raft_nodes
echo.
echo Starting Raft Nodes...
start "Raft Node 1" cmd /k python main.py node1
start "Raft Node 2" cmd /k python main.py node2
start "Raft Node 3" cmd /k python main.py node3
echo All Raft nodes started. Leader election will occur automatically.
pause
goto end

:gui_only
echo.
echo Starting GUI...
python app.py
goto end

:llm_server
echo.
echo Starting LLM Server...
python -m uvicorn llm.llm_server:app --host 0.0.0.0 --port 8500
goto end

:stop_all
echo.
echo Stopping all components...
taskkill /F /FI "WindowTitle eq Application Server*" 2>nul
taskkill /F /FI "WindowTitle eq Raft Node*" 2>nul
taskkill /F /FI "WindowTitle eq LLM Server*" 2>nul
echo All components stopped.
pause
goto end

:invalid
echo Invalid choice. Exiting.
pause
goto end

:end
echo.
echo ================================================
echo   Setup Complete!
echo ================================================
