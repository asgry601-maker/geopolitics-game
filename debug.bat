@echo off
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8

echo ===== GEOPOLITICS GAME - DEBUG REPORT ===== > debug_report.txt
echo. >> debug_report.txt
echo [1] Python version (python command): >> debug_report.txt
python --version >> debug_report.txt 2>&1
echo. >> debug_report.txt
echo [2] Python version (py command): >> debug_report.txt
py --version >> debug_report.txt 2>&1
echo. >> debug_report.txt
echo [3] Game file check: >> debug_report.txt
if exist geopolitics.py (echo geopolitics.py FOUND) else (echo geopolitics.py MISSING!) >> debug_report.txt
echo. >> debug_report.txt
echo [4] Game test run (help): >> debug_report.txt
python -X utf8 geopolitics.py help >> debug_report.txt 2>&1
echo. >> debug_report.txt
echo [5] Game test run (py command): >> debug_report.txt
py -X utf8 geopolitics.py help >> debug_report.txt 2>&1

echo Debug finished. Notepad will open in a moment...
notepad debug_report.txt
pause
