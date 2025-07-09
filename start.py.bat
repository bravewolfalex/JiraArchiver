@echo off
echo Starting Jira Archiver (Python version)...
echo =========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if server.py exists
if not exist "server.py" (
    echo ERROR: server.py not found
    echo Please run this script from the JiraArchiver directory
    pause
    exit /b 1
)

REM Create static directory if it doesn't exist
if not exist "static" (
    mkdir static
)

REM Check if static/index.html exists
if not exist "static\index.html" (
    echo ERROR: static/index.html not found
    echo Please ensure all files are in the correct location
    pause
    exit /b 1
)

REM Start the server
echo Starting server on http://localhost:3000
echo Press Ctrl+C to stop the server
echo =========================================
echo.

python server.py

REM Keep the window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Server failed to start. Check the error above.
    pause
)