@echo off
REM Debug version - keeps window open to see errors

echo.
echo DEBUG MODE - Jira Archiver
echo ================================

REM Show current directory
echo Current directory: %CD%
echo.

REM Show Node.js version
echo Node.js version:
node --version
echo.

REM Show npm version
echo npm version:
npm --version
echo.

REM List files in current directory
echo Files in current directory:
dir /b
echo.

REM Check if package.json exists
if exist "package.json" (
    echo OK: package.json found
) else (
    echo ERROR: package.json NOT found
    pause
    exit /b 1
)

REM Check if node_modules exists
if exist "node_modules" (
    echo OK: node_modules found
) else (
    echo WARNING: node_modules NOT found - installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if server.js exists
if exist "server.js" (
    echo OK: server.js found
) else (
    echo ERROR: server.js NOT found
    pause
    exit /b 1
)

echo.
echo Starting server...
echo ================================

REM Start the server and keep window open
npm start

REM This will run if npm start exits
echo.
echo WARNING: Server stopped or failed to start
echo Error level: %errorlevel%
pause