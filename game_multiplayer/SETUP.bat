@echo off
echo ========================================
echo   CAI DAT GAME MULTIPLAYER
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Dang kiem tra Python...
python --version
if errorlevel 1 (
    echo ERROR: Python chua duoc cai dat!
    echo Vui long cai dat Python tu: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/3] Dang cai dat dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Khong the cai dat dependencies!
    pause
    exit /b 1
)

echo.
echo [3/3] Dang tao file am thanh...
python create_sounds.py
if errorlevel 1 (
    echo WARNING: Khong the tao file am thanh (co the bo qua)
)

echo.
echo ========================================
echo   CAI DAT HOAN TAT!
echo ========================================
echo.
echo De chay game:
echo   1. Double-click: start_game_with_audio.bat
echo   2. Hoac chay: python -m server.main (terminal 1)
echo      Sau do: python -m client.main (terminal 2)
echo.
pause

