@echo off
echo ===============================================
echo    ECOFEAST - Starting Application
echo ===============================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo.
echo Starting Flask development server...
echo.
echo Application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python run.py
pause
