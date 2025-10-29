# Knowledge Chatbot Setup Script for Windows
# Run this script to set up the complete project

Write-Host "🤖 Knowledge Chatbot Setup Script" -ForegroundColor Cyan
Write-Host "==================================`n" -ForegroundColor Cyan

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found. Please install Python 3.9 or higher." -ForegroundColor Red
    exit 1
}

# Check Node.js version
Write-Host "Checking Node.js version..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Node.js not found. Please install Node.js 18 or higher." -ForegroundColor Red
    exit 1
}

Write-Host "`n📦 Setting up Backend..." -ForegroundColor Cyan

# Backend setup
Set-Location backend

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Please add your OpenAI API key." -ForegroundColor Yellow
    Write-Host "   Edit backend/.env and add: OPENAI_API_KEY=your_key_here" -ForegroundColor Yellow
}

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}

Set-Location ..

Write-Host "`n📦 Setting up Frontend..." -ForegroundColor Cyan

# Frontend setup
Set-Location frontend

Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Node.js dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install Node.js dependencies" -ForegroundColor Red
    exit 1
}

Set-Location ..

Write-Host "`n✅ Setup Complete!" -ForegroundColor Green
Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Add your OpenAI API key to backend/.env" -ForegroundColor White
Write-Host "2. Open two terminals:" -ForegroundColor White
Write-Host "   Terminal 1 (Backend):" -ForegroundColor Yellow
Write-Host "     cd backend" -ForegroundColor Gray
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "     python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
Write-Host "`n   Terminal 2 (Frontend):" -ForegroundColor Yellow
Write-Host "     cd frontend" -ForegroundColor Gray
Write-Host "     npm run dev" -ForegroundColor Gray
Write-Host "`n3. Open http://localhost:5173 in your browser" -ForegroundColor White
Write-Host "`n🎉 Happy chatting!" -ForegroundColor Cyan
