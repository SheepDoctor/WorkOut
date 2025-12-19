@echo off
chcp 65001 >nul
echo ========================================
echo 后端运行脚本 - WorkOut Backend
echo ========================================
echo.

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM 检查conda是否安装
echo [1/5] 检查conda环境...
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到conda，请先安装Anaconda或Miniconda
    echo 下载地址: https://www.anaconda.com/products/distribution
    pause
    exit /b 1
)
echo [✓] conda已安装

REM 初始化conda（如果尚未初始化）
call conda init cmd.exe >nul 2>&1

REM 设置环境名称
set ENV_NAME=workout-backend
set PYTHON_VERSION=3.10

REM 检查环境是否存在
echo [2/5] 检查conda环境 '%ENV_NAME%'...
call conda env list | findstr /C:"%ENV_NAME%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 环境不存在，正在创建...
    call conda create -n %ENV_NAME% python=%PYTHON_VERSION% -y
    if %errorlevel% neq 0 (
        echo [错误] 创建conda环境失败
        pause
        exit /b 1
    )
    echo [✓] 环境创建成功
) else (
    echo [✓] 环境已存在
)

REM 激活环境
echo [3/5] 激活conda环境...
call conda activate %ENV_NAME%
if %errorlevel% neq 0 (
    echo [错误] 激活conda环境失败
    pause
    exit /b 1
)
echo [✓] 环境已激活

REM 检查并安装依赖
echo [4/5] 检查Python依赖...
if exist requirements.txt (
    echo [信息] 正在安装依赖包...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo [警告] 部分依赖安装可能失败，继续运行...
    ) else (
        echo [✓] 依赖安装完成
    )
) else (
    echo [警告] 未找到requirements.txt文件
)

REM 检查数据库迁移
echo [5/5] 检查数据库迁移...
python manage.py makemigrations --noinput >nul 2>&1
python manage.py migrate --noinput
if %errorlevel% neq 0 (
    echo [警告] 数据库迁移可能有问题，继续运行...
)

echo.
echo ========================================
echo 启动Django开发服务器...
echo ========================================
echo 服务器地址: http://localhost:8000
echo 按 Ctrl+C 停止服务器
echo.

REM 运行Django服务器
python manage.py runserver

pause

