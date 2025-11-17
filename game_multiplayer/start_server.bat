@echo off
echo Starting Game Server...
cd /d "%~dp0"
set PYTHONPATH=%CD%
python -m server.main
pause

