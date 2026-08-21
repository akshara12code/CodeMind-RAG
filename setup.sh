#!/bin/bash

set -e

echo "🚀 Codebase RAG - Setup Script"
echo "=============================="
echo ""

# Check Python
echo "✓ Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Please install Python 3.11+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "  Found Python $PYTHON_VERSION"

# Check Node
echo "✓ Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "✗ Node.js not found. Please install Node.js 18+"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "  Found $NODE_VERSION"

# Setup Backend
echo ""
echo "📦 Setting up Backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "  Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "  Installing Python dependencies..."
pip install -q -r requirements.txt

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "  Creating .env file..."
    cp .env.example .env
fi

cd ..

# Setup Frontend
echo ""
echo "🎨 Setting up Frontend..."
cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "  Installing Node dependencies..."
    npm install
fi

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "  Creating .env file..."
    cp .env.example .env
fi

cd ..

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📝 To run the project:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python -m uvicorn app.main:app --reload --port 8000"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then visit:"
echo "  Backend API Docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:5173"
echo ""
