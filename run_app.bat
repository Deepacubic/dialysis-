@echo off
title Dialysis Patient Monitoring & Diet Recommendation System
color 0B
echo ===========================================
echo         DIALYSIS MONITORING & DIET SYSTEM - START      
echo ===========================================
echo.
echo [1/3] Navigating to project directory...
cd /d "%~dp0"

echo [2/3] Starting AI Engine (Flask Server)...
echo -------------------------------------------
echo Server will be available at: http://127.0.0.1:5000/dashboard
echo.
echo Opening browser... 🚀
echo.

:: Start Browser to the Dashboard directly
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5000/dashboard"

:: Run the server in foreground so we can see the console logs
py app.py

echo.
echo Server has been stopped. 🛑
pause
