#!/bin/bash

echo "========================================"
echo "  ECOFEAST - Application Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found."
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment"
    exit 1
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

echo ""
echo "Checking for .env file..."
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env from template..."
    cp .env.example .env
    echo "⚠ Please edit .env file with your settings:"
    echo "  - DATABASE_URL"
    echo "  - GOOGLE_MAPS_KEY"
    echo "  - SECRET_KEY"
    echo "  - JWT_SECRET_KEY"
    echo ""
    read -p "Press Enter to continue..."
else
    echo ".env file found"
fi

echo ""
echo "Initializing database..."
python run.py

echo ""
echo "✓ Setup completed successfully!"
echo ""
echo "To start the application, run: ./run.sh"
echo ""
