@echo off
chcp 65001 >nul
cd /d %~dp0
call venv\Scripts\activate.bat

echo ========================================
echo API 接口测试
echo ========================================
echo.
echo 请确保服务已启动（运行 start.bat）
echo.
pause

python test_api.py

echo.
pause
