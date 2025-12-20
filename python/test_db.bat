@echo off
chcp 65001 >nul
cd /d %~dp0
call venv\Scripts\activate.bat

echo ========================================
echo 数据库连接测试
echo ========================================
echo.

python test_db.py

echo.
pause
