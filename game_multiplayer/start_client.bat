@echo off
echo Starting Game Client...
cd /d "%~dp0"
set PYTHONPATH=%CD%
python -m client.main
pause

