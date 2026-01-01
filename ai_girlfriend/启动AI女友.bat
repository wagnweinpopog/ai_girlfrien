@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    🤖 星黎级AI女友 - 一键启动
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖文件
if not exist "requirements.txt" (
    echo ❌ 未找到依赖文件 requirements.txt
    pause
    exit /b 1
)

REM 检查环境配置
if not exist ".env" (
    echo ⚠️ 未找到环境配置文件 .env
    echo 正在检查示例文件...
    if exist ".env.example" (
        copy .env.example .env >nul 2>&1
        echo ✅ 已创建 .env，请修改并填入API密钥
    ) else (
        echo ❌ 未找到 .env.example 文件
    )
    pause
    exit /b 1
)

REM 先更新pip（解决中文编码问题）
echo 📦 更新pip...
python -m pip install --upgrade pip --quiet

REM 安装依赖（指定UTF-8编码）
echo 📦 安装Python依赖包...
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo ❌ 依赖安装失败，尝试手动安装...
    echo 请运行：pip install -r requirements.txt
    pause
    exit /b 1
)

REM 检查核心文件
echo 🔍 检查核心文件...
if not exist "core\consciousness.py" (
    echo ❌ 缺少核心文件：consciousness.py
    pause
    exit /b 1
)

REM 启动AI女友
echo.
echo 🚀 启动AI女友...
echo.

python start.py

if errorlevel 1 (
    echo.
    echo ❌ 启动失败，请检查错误信息
    echo.
)

pause