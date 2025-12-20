@echo off
cd /d %~dp0
call venv\Scripts\activate.bat

echo ========================================
echo What-Eat API Starting...
echo ========================================
echo.
echo Host: 0.0.0.0 (All network interfaces)
echo Port: 8000
echo.
echo Local Access:
echo   - http://localhost:8000
echo   - http://127.0.0.1:8000
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        echo LAN Access: http://%%b:8000
    )
)
echo.
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
