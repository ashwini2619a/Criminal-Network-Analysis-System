# SENTINEL v2.0 - 1-Click PowerShell Launcher
# Ministry of Home Affairs / NCRB / Women Safety Division

$Host.UI.RawUI.WindowTitle = "SENTINEL v2.0 - Operational Command Console"
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "  SENTINEL v2.0 - AI-POWERED CRIMINAL NETWORK ANALYSIS SYSTEM" -ForegroundColor White
Write-Host "  Ministry of Home Affairs / NCRB / Women Safety Division" -ForegroundColor Gray
Write-Host "===============================================================================" -ForegroundColor Cyan

$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONIOENCODING = "utf-8"

# 1. Start Backend Core
Write-Host "[1/3] Launching FastAPI Intelligence Core on port 8000..." -ForegroundColor Yellow
$backendDir = Join-Path $baseDir "backend"
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; `$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000" -PassThru

# 2. Start Frontend UI
Write-Host "[2/3] Launching Tactical UI Command Console on port 5173..." -ForegroundColor Yellow
$frontendDir = Join-Path $baseDir "frontend"
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; npm run dev" -PassThru

# 3. Wait and open browser
Write-Host "[3/3] Synchronizing microservices..." -ForegroundColor Yellow
Start-Sleep -Seconds 4

Write-Host "Opening Tactical Dashboard in browser..." -ForegroundColor Green
Start-Process "http://localhost:5173/"

Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "  SENTINEL v2.0 IS LIVE AND OPERATIONAL" -ForegroundColor Green
Write-Host "  Frontend:  http://localhost:5173/" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "===============================================================================" -ForegroundColor Cyan
