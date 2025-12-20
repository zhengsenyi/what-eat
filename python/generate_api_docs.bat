@echo off
chcp 65001 >nul
cd /d %~dp0
call venv\Scripts\activate.bat

echo ========================================
echo 生成 OpenAPI 文档
echo ========================================
echo.

python generate_openapi.py

if %errorlevel% equ 0 (
    echo.
    echo ✓ 生成成功！
    echo.
    echo 文档位置: 吃啥盲盒.openapi.json
) else (
    echo.
    echo ✗ 生成失败，请检查错误信息
)

echo.
pause
