@echo off
echo Installing minimal dependencies...
npm install --production --no-optional
echo.
echo Starting server...
node server.js
pause