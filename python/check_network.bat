@echo off
chcp 65001 >nul
echo ========================================
echo What-Eat API 网络诊断工具
echo ========================================
echo.

echo [1] 检查本机 IP 地址
echo ----------------------------------------
ipconfig | findstr /c:"IPv4"
echo.

echo [2] 检查 8000 端口是否被占用
echo ----------------------------------------
netstat -ano | findstr :8000
if %errorlevel% equ 0 (
    echo 端口 8000 正在被使用
) else (
    echo 端口 8000 未被使用 - 可以启动服务
)
echo.

echo [3] 检查防火墙规则
echo ----------------------------------------
netsh advfirewall firewall show rule name="What-Eat API" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 防火墙规则已存在
    netsh advfirewall firewall show rule name="What-Eat API"
) else (
    echo ✗ 防火墙规则不存在
    echo.
    echo 需要添加防火墙规则，请以管理员权限运行：
    echo netsh advfirewall firewall add rule name="What-Eat API" dir=in action=allow protocol=TCP localport=8000
)
echo.

echo [4] 测试本机连接
echo ----------------------------------------
echo 尝试连接 http://localhost:8000/health
curl -s http://localhost:8000/health 2>nul
if %errorlevel% equ 0 (
    echo.
    echo ✓ 本机连接成功
) else (
    echo ✗ 本机连接失败 - 请确保服务已启动
)
echo.

echo ========================================
echo 诊断完成
echo ========================================
pause
