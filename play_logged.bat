@echo off
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
powershell -NoProfile -Command "py -X utf8 geopolitics.py play 2>&1 | Tee-Object -FilePath run_log.txt"
echo. >> run_log.txt
echo ===== END OF RUN (this file was auto-created by play_logged.bat) ===== >> run_log.txt
notepad run_log.txt
pause
