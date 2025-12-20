@echo off
chcp 65001 >nul
echo ====================================
echo   Delta API 文档生成工具
echo ====================================
echo.

echo [1/3] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [2/3] 激活虚拟环境...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else (
    echo ⚠️  未找到虚拟环境，使用全局 Python
)

echo [3/3] 生成 OpenAPI 文档...
python generate_openapi.py

if errorlevel 1 (
    echo.
    echo ❌ 生成失败，请检查错误信息
    echo.
    echo 💡 提示：
    echo    1. 确保已安装依赖: pip install -r requirements.txt
    echo    2. 确保在项目根目录运行此脚本
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ✅ 文档生成成功！
    echo.
    echo 📁 文件位置: Delta游戏陪玩后端API.openapi.json
    echo 💡 提示: 可以直接导入到 Apifox 中使用
    echo.
)

pause
