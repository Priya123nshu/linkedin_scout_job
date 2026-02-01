#!/bin/bash

# Backend Setup Script

echo "🚀 Setting up LinkedIn MCP Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from env.example..."
    cp env.example .env
    echo "⚠️  Please edit .env and add your Clerk keys!"
fi

echo "✅ Backend setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Clerk keys"
echo "2. Run: python main.py"
