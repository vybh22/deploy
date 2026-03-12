@echo off
echo ===============================================
echo         ECOFEAST - Application Setup
echo ===============================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python not found in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv

if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Checking for .env file...
if not exist .env (
    echo.
    echo Creating .env from template...
    copy .env.example .env
    echo ⚠ Please edit .env file with your settings:
    echo   - DATABASE_URL
    echo   - GOOGLE_MAPS_KEY
    echo   - SECRET_KEY
    echo   - JWT_SECRET_KEY
    echo.
    pause
) else (
    echo .env file found
)

echo.
echo Initializing database...
python run.py

echo.
echo ✓ Setup completed successfully!
echo.
echo To start the application, run: run.bat
echo.
pause
