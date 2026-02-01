@echo off
REM Backend Setup Script for Windows

echo 🚀 Setting up LinkedIn MCP Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from env.example...
    copy env.example .env
    echo ⚠️  Please edit .env and add your Clerk keys!
)

echo ✅ Backend setup complete!
echo.
echo Next steps:
echo 1. Edit .env and add your Clerk keys
echo 2. Run: python main.py

pause
