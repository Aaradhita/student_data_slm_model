@echo off
REM Student Portal - Quick Start Script for Windows

echo.
echo ============================================================
echo 🚀 Student Portal - Startup Script
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

REM Navigate to project directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -q fastapi uvicorn pydantic pyjwt bcrypt scikit-learn

REM Initialize database
echo.
echo Initializing database...
python database_init.py

REM Start the server
echo.
echo ============================================================
echo ✅ Starting Student Portal Server
echo ============================================================
echo.
echo 📍 Access the application at: http://localhost:8000
echo.
echo 📝 Demo Credentials:
echo    Register: DEMO001
echo    Password: demo@123
echo.
echo 📖 API Documentation: http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo ============================================================
echo.

python app.py

pause
