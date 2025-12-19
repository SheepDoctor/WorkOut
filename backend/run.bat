@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo Backend Run Script - WorkOut Backend
echo ========================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check conda installation
echo [1/5] Checking conda environment...
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] conda not found. Please install Anaconda or Miniconda first.
    echo Download: https://www.anaconda.com/products/distribution
    pause
    exit /b 1
)
echo [OK] conda is installed

REM Initialize conda if not already initialized
call conda init cmd.exe >nul 2>&1

REM Set environment name
set ENV_NAME=workout
set PYTHON_VERSION=3.10

REM Check if environment exists
echo [2/5] Checking conda environment '%ENV_NAME%'...
call conda env list | findstr /C:"%ENV_NAME%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Environment does not exist, creating...
    call conda create -n %ENV_NAME% python=%PYTHON_VERSION% -y
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create conda environment
        pause
        exit /b 1
    )
    echo [OK] Environment created successfully
) else (
    echo [OK] Environment already exists
)

REM Activate environment
echo [3/5] Activating conda environment...
call conda activate %ENV_NAME%
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate conda environment
    pause
    exit /b 1
)
echo [OK] Environment activated

REM Check and install dependencies
echo [4/5] Checking Python dependencies...
if exist requirements.txt (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo [WARNING] Some dependencies may have failed to install, continuing...
    ) else (
        echo [OK] Dependencies installed
    )
) else (
    echo [WARNING] requirements.txt file not found
)

REM Check database migrations
echo [5/5] Checking database migrations...
python manage.py makemigrations --noinput >nul 2>&1
python manage.py migrate --noinput
if %errorlevel% neq 0 (
    echo [WARNING] Database migration may have issues, continuing...
)

echo.
echo ========================================
echo Starting Django Development Server
echo ========================================
echo Server URL: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

REM Run Django server
python manage.py runserver

pause
