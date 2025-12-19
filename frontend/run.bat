@echo off
chcp 65001 >nul
echo ========================================
echo 前端运行脚本 - WorkOut Frontend
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
set ENV_NAME=workout-frontend

REM 检查环境是否存在
echo [2/5] 检查conda环境 '%ENV_NAME%'...
call conda env list | findstr /C:"%ENV_NAME%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 环境不存在，正在创建...
    REM 使用nodejs包创建环境
    call conda create -n %ENV_NAME% nodejs npm -y
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

REM 检查node和npm
echo [4/5] 检查Node.js和npm...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 正在安装Node.js...
    call conda install nodejs npm -y
    if %errorlevel% neq 0 (
        echo [错误] 安装Node.js失败
        pause
        exit /b 1
    )
)
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Node.js未正确安装
    pause
    exit /b 1
)
echo [✓] Node.js版本:
node --version
echo [✓] npm版本:
npm --version

REM 检查并安装依赖
if exist package.json (
    echo [5/5] 检查npm依赖...
    if not exist node_modules (
        echo [信息] 正在安装npm依赖包（这可能需要几分钟）...
        call npm install
        if %errorlevel% neq 0 (
            echo [错误] npm依赖安装失败
            pause
            exit /b 1
        )
        echo [✓] 依赖安装完成
    ) else (
        echo [✓] node_modules已存在，跳过安装
        echo [信息] 如需重新安装，请删除node_modules文件夹后重新运行
    )
) else (
    echo [错误] 未找到package.json文件
    pause
    exit /b 1
)

echo.
echo ========================================
echo 启动Vite开发服务器...
echo ========================================
echo 服务器地址: http://localhost:5173
echo 按 Ctrl+C 停止服务器
echo.

REM 运行Vite开发服务器
call npm run dev

pause

