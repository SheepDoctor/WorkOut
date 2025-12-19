@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo Frontend Run Script - WorkOut Frontend
echo ========================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"


echo [1/2] Checking npm dependencies...
call npm install

echo.
echo [2/2] Starting Vite development server...
echo ========================================
echo Starting Vite Development Server
echo ========================================
echo Server URL: http://localhost:5173
echo Press Ctrl+C to stop the server
echo.

REM Run Vite development server
call npm run dev

pause
