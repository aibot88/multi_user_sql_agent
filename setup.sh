#!/bin/bash

# Multi-User SQL Agent Setup Script

echo "🤖 Multi-User SQL Agent Setup"
echo "=============================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies (simplified list that should work without internet)
echo "📚 Installing dependencies..."
pip install --quiet \
    fastapi \
    uvicorn \
    python-multipart \
    jinja2 \
    pandas \
    pydantic \
    httpx \
    pytest

echo "✓ Dependencies installed"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p user_databases
mkdir -p static
mkdir -p templates

echo "✓ Directories created"

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY environment variable is not set."
    echo "   The app will work with basic functionality but won't use actual LLM."
    echo "   To set it: export OPENAI_API_KEY='your-api-key-here'"
fi

echo ""
echo "🚀 Setup complete!"
echo ""
echo "To run the application:"
echo "  1. source venv/bin/activate"
echo "  2. python app.py"
echo ""
echo "Then open your browser to: http://localhost:8000"
echo ""
echo "To run tests:"
echo "  python test_app.py"