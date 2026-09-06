@echo off
echo ==========================================
echo Network Monitor Setup - Windows
echo ==========================================

echo.
echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in your PATH. 
    echo Please install Python 3.8 or newer and try again.
    pause
    exit /b 1
)

echo.
echo Creating virtual environment (venv)...
if not exist venv (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

echo.
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Setup complete! 
echo You can now run the application using run.bat
echo ==========================================
pause
