@echo off
echo ===============================================
echo         ECOFEAST - Database Setup
echo ===============================================
echo.

REM Check if PostgreSQL is installed
where psql >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo PostgreSQL not found in PATH
    echo Please install PostgreSQL 12 or higher
    pause
    exit /b 1
)

echo Creating ECOFEAST database...
psql -U postgres -c "CREATE DATABASE ecofeast_dev;"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Database created successfully!
    echo.
    echo Next steps:
    echo 1. Edit .env file with your configuration
    echo 2. Run setup.bat to initialize the application
) else (
    echo.
    echo Database may already exist or PostgreSQL connection failed
    echo Make sure PostgreSQL is running and accessible
)

pause
