#!/bin/bash

echo "=========================================="
echo "Starting Network Monitor..."
echo "=========================================="

if [ ! -f "venv/bin/activate" ]; then
    echo "Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

source venv/bin/activate
echo "Starting application..."
python3 app.py
