@echo off
echo ========================================
echo   KHỞI ĐỘNG GAME VỚI ÂM THANH
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Đang khởi động Server...
start "Game Server" cmd /k "python -m server.main"
timeout /t 2 /nobreak >nul

echo [2/2] Đang khởi động Client với âm thanh...
echo.
echo ✓ Âm thanh sẽ được BẬT tự động
echo.

REM Tự động trả lời "Y" cho câu hỏi bật âm thanh
echo Y | python -m client.main

pause

