#!/bin/bash

echo "========================================"
echo "   ECOFEAST - Starting Application"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found."
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment"
    exit 1
fi

echo ""
echo "Starting Flask development server..."
echo ""
echo "Application will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python run.py
