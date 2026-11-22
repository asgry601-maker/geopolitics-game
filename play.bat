@echo off
setlocal
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

set PYCMD=
where py >nul 2>nul && set PYCMD=py
if not defined PYCMD where python >nul 2>nul && set PYCMD=python
if not defined PYCMD goto nopy

%PYCMD% -X utf8 geopolitics.py play

echo.
echo ---------------------------------------------
pause
exit /b 0

:nopy
echo.
echo [ERROR] Python not found!
echo Please download and install Python 3.8 first:
echo   https://www.python.org/downloads/release/python-3810/
echo (check "Add Python to PATH" during setup)
echo.
pause
