#!/bin/bash

# Jira Archiver Python Start Script for Unix/Linux/macOS

echo "Starting Jira Archiver (Python version)..."
echo "========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Check if server.py exists
if [ ! -f "server.py" ]; then
    echo "ERROR: server.py not found"
    echo "Please run this script from the JiraArchiver directory"
    exit 1
fi

# Create static directory if it doesn't exist
if [ ! -d "static" ]; then
    mkdir static
fi

# Check if static/index.html exists
if [ ! -f "static/index.html" ]; then
    echo "ERROR: static/index.html not found"
    echo "Please ensure all files are in the correct location"
    exit 1
fi

# Start the server
echo "Starting server on http://localhost:3000"
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo

$PYTHON_CMD server.py