#!/bin/bash

echo "=========================================="
echo "Network Monitor Setup - Linux/macOS"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in your PATH."
    echo "Please install Python 3.8 or newer and try again."
    exit 1
fi

echo "Creating virtual environment (venv)..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Ensure you have the python3-venv package installed if on Debian/Ubuntu."
        exit 1
    fi
else
    echo "Virtual environment already exists."
fi

echo ""
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "Failed to install dependencies."
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "Make sure to run 'chmod +x run.sh' if you haven't already."
echo "You can now run the application using ./run.sh"
echo "=========================================="
