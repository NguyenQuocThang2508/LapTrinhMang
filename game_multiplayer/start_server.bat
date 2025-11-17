@echo off
echo Starting Game Server...
cd /d "%~dp0"
python -m server.main
pause

