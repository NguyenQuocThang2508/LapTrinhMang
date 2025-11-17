@echo off
echo ========================================
echo   KHỞI ĐỘNG GAME MULTIPLAYER
echo ========================================
echo.

cd /d "%~dp0"

set PYTHONPATH=%CD%
echo [1/2] Đang khởi động Server...
start "Game Server" cmd /k "set PYTHONPATH=%CD% && python -m server.main"
timeout /t 2 /nobreak >nul

echo [2/2] Đang khởi động Client...
echo.
echo LƯU Ý: Khi được hỏi "Bật âm thanh?", nhập Y để bật âm thanh
echo.
python -m client.main

pause

