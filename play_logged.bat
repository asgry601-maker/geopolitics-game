@echo off
setlocal
set PYTHONIOENCODING=utf-8
chcp 65001 >nul
cd /d "%~dp0"
python geopolitics.py play 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath run_log.txt"
echo.
echo ===== END OF RUN (auto-created by play_logged.bat) ===== >> run_log.txt
notepad run_log.txt
pause
