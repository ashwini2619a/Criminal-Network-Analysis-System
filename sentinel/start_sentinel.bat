@echo off
title SENTINEL v2.0 - Criminal Network Analysis System
color 0B

echo ===============================================================================
echo   SENTINEL v2.0 - AI-POWERED CRIMINAL NETWORK ANALYSIS SYSTEM
echo   Ministry of Home Affairs / NCRB / Women Safety Division
echo ===============================================================================
echo [1/3] Initializing Tactical Environment...
set PYTHONIOENCODING=utf-8

echo [2/3] Launching FastAPI Intelligence Core on port 8000...
cd /d "%~dp0\backend"
start "SENTINEL Core [Port 8000]" cmd /k ".venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000"

echo [3/3] Launching Tactical UI Command Console on port 5173...
cd /d "%~dp0\frontend"
start "SENTINEL UI [Port 5173]" cmd /k "npm run dev"

echo.
echo Waiting 4 seconds for services to initialize...
timeout /t 4 /nobreak >nul

echo Launching Operational Command Console in Default Browser...
start http://localhost:5173/

echo.
echo ===============================================================================
echo   SENTINEL v2.0 is ACTIVE and OPERATIONAL
echo   Frontend:  http://localhost:5173/
echo   Backend:   http://localhost:8000/docs
echo ===============================================================================
echo.
pause
