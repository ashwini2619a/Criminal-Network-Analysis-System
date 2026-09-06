@echo off
echo ==========================================
echo Starting Network Monitor...
echo ==========================================

if not exist venv\Scripts\activate.bat (
    echo Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate
echo Starting application...
python app.py

pause
