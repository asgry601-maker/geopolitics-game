@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
    echo [خطا] پایتون نصب نیست! اول از python.org پایتون ۳ را نصب کن.
    pause
    exit /b 1
)
python -X utf8 geopolitics.py play
pause
