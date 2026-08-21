@echo off
setlocal enabledelayedexpansion

echo.
echo 🚀 Codebase RAG - Setup Script (Windows)
echo ======================================
echo.

:: Check Python
echo ✓ Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python not found. Please install Python 3.11+
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo   Found Python %PYTHON_VERSION%

:: Check Node
echo ✓ Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)
for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo   Found %NODE_VERSION%

:: Setup Backend
echo.
echo 📦 Setting up Backend...
cd backend

if not exist "venv" (
    echo   Creating virtual environment...
    python -m venv venv
)

echo   Activating virtual environment...
call venv\Scripts\activate

echo   Installing Python dependencies...
pip install -q -r requirements.txt

if not exist ".env" (
    echo   Creating .env file...
    copy .env.example .env
)

cd ..

:: Setup Frontend
echo.
echo 🎨 Setting up Frontend...
cd frontend

if not exist "node_modules" (
    echo   Installing Node dependencies...
    call npm install
)

if not exist ".env" (
    echo   Creating .env file...
    copy .env.example .env
)

cd ..

echo.
echo ✅ Setup Complete!
echo.
echo 📝 To run the project:
echo.
echo Terminal 1 (Backend):
echo   cd backend
echo   venv\Scripts\activate
echo   python -m uvicorn app.main:app --reload --port 8000
echo.
echo Terminal 2 (Frontend):
echo   cd frontend
echo   npm run dev
echo.
echo Then visit:
echo   Backend API Docs: http://localhost:8000/docs
echo   Frontend: http://localhost:5173
echo.
pause
