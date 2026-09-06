@echo off
title SENTINEL v2.0 Operations Launcher
color 0B
cls

echo ===============================================================================
echo   SENTINEL v2.0 - CRIMINAL NETWORK ANALYSIS & WOMEN SAFETY TRACKER
echo   Directorate of Intelligence & Women Safety Operations Center
echo ===============================================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [*] Verifying system prerequisites...

:: Check Python virtual environment
if exist "backend\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=backend\.venv\Scripts\python.exe"
    echo [OK] Detected backend virtual environment: backend\.venv
) else (
    where python >nul 2>nul
    if %errorlevel% neq 0 (
        color 0C
        echo [ERROR] Python was not found on PATH or in backend\.venv.
        echo Please ensure Python 3.10+ is installed and accessible.
        pause
        exit /b 1
    )
    set "PYTHON_EXE=python"
    echo [WARN] Virtual environment not found; using system Python.
)

:: Check Node.js / NPM
where npm >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Node.js / npm was not found on PATH.
    echo Please install Node.js 18+ to execute the frontend application.
    pause
    exit /b 1
)
echo [OK] Detected Node.js / npm environment.

echo.
echo ===============================================================================
echo   LAUNCHING SENTINEL SUBSYSTEMS
echo ===============================================================================

:: 1. Launch FastAPI Backend
echo [*] Starting Intelligence Graph Backend on http://127.0.0.1:8000 ...
start "SENTINEL Backend API [Port 8000]" cmd /k "cd /d "%SCRIPT_DIR%backend" && "%SCRIPT_DIR%%PYTHON_EXE%" -m uvicorn main:app --host 127.0.0.1 --port 8000"

:: 2. Launch Vite Tactical Frontend
echo [*] Starting Tactical Web Operations Console on http://localhost:5173 ...
start "SENTINEL Frontend [Port 5173]" cmd /k "cd /d "%SCRIPT_DIR%frontend" && npm run dev"

echo.
echo [*] Subsystems dispatched. Waiting for network initialization (4 seconds)...
timeout /t 4 /nobreak >nul

:: 3. Launch Default Browser
echo [*] Opening Operations Console in web browser...
start http://localhost:5173

echo.
echo ===============================================================================
echo   OPERATIONS CONSOLE READY
echo ===============================================================================
echo   - Tactical Dashboard:      http://localhost:5173
echo   - Women Safety Edge AI:    http://localhost:5173/tracker
echo   - Backend OpenAPI Docs:    http://127.0.0.1:8000/docs
echo.
echo   TACTICAL LOGIN CREDENTIALS:
echo   - Administrator:           admin / sentinel2024
echo   - Field Investigator:      investigator / investigator2026
echo   - Intelligence Analyst:    analyst / analyst2026
echo ===============================================================================
echo.
echo Keep the backend and frontend command windows open while operating SENTINEL.
echo Press any key to exit this launcher window...
pause >nul
