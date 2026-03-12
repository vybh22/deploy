#!/bin/bash

echo "========================================"
echo "    ECOFEAST - Creating Database"
echo "========================================"
echo ""

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL not found."
    echo "Please install PostgreSQL 12 or higher"
    exit 1
fi

echo "Creating ECOFEAST database..."
psql -U postgres -c "CREATE DATABASE ecofeast_dev;"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Database created successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Run ./setup.sh to initialize the application"
else
    echo ""
    echo "Database may already exist or PostgreSQL connection failed"
    echo "Make sure PostgreSQL is running and accessible"
fi
