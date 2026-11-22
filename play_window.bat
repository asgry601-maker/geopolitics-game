@echo off
setlocal
cd /d "%~dp0"
set PYW=
where pythonw >nul 2>nul && set PYW=pythonw
if not defined PYW where python >nul 2>nul && set PYW=python
if not defined PYW goto nopy
start "Geopolitics" %PYW% geopolitics_gui.py
exit /b 0

:nopy
echo.
echo [ERROR] Python not found!
echo Please install Python 3.8.10 first:
echo   https://www.python.org/downloads/release/python-3810/
echo (check "Add Python to PATH" during setup)
pause
