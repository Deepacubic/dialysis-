@echo off
title DialyCare AI - Flask Server
echo =======================================
echo     DialyCare AI Application
echo =======================================
echo.
echo Starting Flask server...
echo Server will be available at: http://127.0.0.1:5000
echo.
echo Press CTRL+C to stop the server.
echo.

cd /d "%~dp0"

:: Start Flask server in the background
start "" /B py app.py

:: Wait 3 seconds for the server to start, then open browser
timeout /t 3 /nobreak >nul
echo Opening browser...
start "" http://127.0.0.1:5000

:: Keep the window open and show server output
py app.py

echo.
echo Server stopped.
pause
