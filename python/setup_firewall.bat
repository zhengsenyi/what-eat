@echo off
chcp 65001 >nul
echo ========================================
echo What-Eat API 防火墙配置工具
echo ========================================
echo.
echo 此脚本将添加 Windows 防火墙规则以允许外部访问 8000 端口
echo 请确保以管理员权限运行此脚本
echo.
pause

echo.
echo 正在添加防火墙规则...
netsh advfirewall firewall add rule name="What-Eat API" dir=in action=allow protocol=TCP localport=8000

if %errorlevel% equ 0 (
    echo.
    echo ✓ 防火墙规则添加成功！
    echo.
    echo 现在可以通过以下方式访问：
    echo   - 本机: http://localhost:8000
    echo   - 局域网: http://[本机IP]:8000
    echo.
    echo 如需外网访问，还需要配置路由器端口转发
) else (
    echo.
    echo ✗ 添加失败！请确保：
    echo   1. 以管理员权限运行此脚本
    echo   2. Windows 防火墙服务已启动
)

echo.
pause
