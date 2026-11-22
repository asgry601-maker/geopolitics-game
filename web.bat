@echo off
setlocal
cd /d "%~dp0"
set PYCMD=
where python >nul 2>nul && set PYCMD=python
if not defined PYCMD where py >nul 2>nul && set PYCMD=py
if not defined PYCMD goto nopy
%PYCMD% geopolitics_web.py
echo.
echo Game server closed. Goodbye!
pause
exit /b 0

:nopy
echo.
echo [ERROR] Python not found!
echo Install Python 3.8.10 from:
echo   https://www.python.org/downloads/release/python-3810/
pause
