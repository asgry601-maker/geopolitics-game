@echo off
setlocal
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

set PYCMD=
where python >nul 2>nul && set PYCMD=python
if not defined PYCMD where py >nul 2>nul && set PYCMD=py
if not defined PYCMD goto nopy

set GEO_ENGINE_DIR=%~dp0.
if exist "%~dp0engine\geopolitics.py" set GEO_ENGINE_DIR=%~dp0engine
if exist "%~dp0github__asgry601-maker__geopolitics-game\geopolitics.py" set GEO_ENGINE_DIR=%~dp0github__asgry601-maker__geopolitics-game

%PYCMD% geopolitics_api.py

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
exit /b 1
