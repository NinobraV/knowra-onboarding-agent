#!/bin/bash

# Knowledge Chatbot Setup Script for Linux/Mac
# Run this script to set up the complete project

echo "🤖 Knowledge Chatbot Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python found: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✅ Python found: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.9 or higher."
    exit 1
fi

# Check Node.js version
echo "Checking Node.js version..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js found: $NODE_VERSION"
else
    echo "❌ Node.js not found. Please install Node.js 18 or higher."
    exit 1
fi

echo ""
echo "📦 Setting up Backend..."

# Backend setup
cd backend

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please add your OpenAI API key."
    echo "   Edit backend/.env and add: OPENAI_API_KEY=your_key_here"
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

cd ..

echo ""
echo "📦 Setting up Frontend..."

# Frontend setup
cd frontend

echo "Installing Node.js dependencies..."
npm install
if [ $? -eq 0 ]; then
    echo "✅ Node.js dependencies installed"
else
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi

cd ..

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Add your OpenAI API key to backend/.env"
echo "2. Open two terminals:"
echo "   Terminal 1 (Backend):"
echo "     cd backend"
echo "     source venv/bin/activate"
echo "     python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "   Terminal 2 (Frontend):"
echo "     cd frontend"
echo "     npm run dev"
echo ""
echo "3. Open http://localhost:5173 in your browser"
echo ""
echo "🎉 Happy chatting!"
