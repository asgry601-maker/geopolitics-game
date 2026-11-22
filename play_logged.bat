@echo off
setlocal
set PYTHONIOENCODING=utf-8
chcp 65001 >nul
cd /d "%~dp0"
set PYCMD=
where python >nul 2>nul && set PYCMD=python
if not defined PYCMD where py >nul 2>nul && set PYCMD=py
if not defined PYCMD goto nopy
%PYCMD% geopolitics.py play log
echo.
echo ===== END OF RUN (auto-created by play_logged.bat) =====
echo run_log.txt is saved in this folder (opened in Notepad by the game).
pause
exit /b 0

:nopy
echo.
echo [ERROR] Python not found!
echo Please install Python 3.8.10 first:
echo   https://www.python.org/downloads/release/python-3810/
echo (check "Add Python to PATH" during setup)
pause
exit /b 1
