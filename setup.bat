@echo off
REM Setup script for Food Delivery Application - Windows

echo.
echo ===================================
echo 🍕 Food Delivery App - Setup Script
echo ===================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed. Please install it first.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ Python found: %PYTHON_VERSION%
echo.

REM Check Node
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed. Please install it first.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✓ Node.js found: %NODE_VERSION%
echo.

REM Backend setup
echo Setting up Backend...
cd backend

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Train model
echo Training ML model...
python train_model.py

REM Initialize database
echo Initializing database...
python -c "from app import create_app; app = create_app(); app.cli.invoke('init_db_command')"

echo ✓ Backend setup complete!
echo.

REM Frontend setup
echo Setting up Frontend...
cd ..\frontend

REM Install dependencies
echo Installing Node dependencies...
call npm install

REM Create env file
echo Creating environment file...
(
    echo VUE_APP_API_URL=http://localhost:5000/api
    echo VUE_APP_ENV=development
) > .env.local

echo ✓ Frontend setup complete!
echo.

echo ===================================
echo ✓ Setup Complete!
echo ===================================
echo.
echo To start the application:
echo.
echo Command Prompt 1 - Backend:
echo   cd backend
echo   venv\Scripts\activate.bat
echo   python app.py
echo.
echo Command Prompt 2 - Frontend:
echo   cd frontend
echo   npm run dev
echo.
echo Then open: http://localhost:5173
echo.
echo Demo Credentials:
echo   Email: admin@fooddelivery.com
echo   Password: admin123456
echo.
pause
