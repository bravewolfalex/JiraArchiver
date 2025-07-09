@echo off
REM Jira Archiver Start Script for Windows
REM This script starts the Jira Archiver server

echo.
echo 🗂️  Starting Jira Archiver...
echo ================================

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Node.js is not installed
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: npm is not installed
    echo Please install npm (usually comes with Node.js)
    pause
    exit /b 1
)

REM Check if package.json exists
if not exist "package.json" (
    echo ❌ Error: package.json not found
    echo Please run this script from the JiraArchiver directory
    pause
    exit /b 1
)

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Start the server
echo 🚀 Starting server on http://localhost:3000
echo Press Ctrl+C to stop the server
echo ================================
echo.

npm start