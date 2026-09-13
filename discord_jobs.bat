@echo off
cd /d "%~dp0"
python discord_jobs.py --loop
if errorlevel 1 (
    echo.
    echo [discord_jobs] falha ao inicializar o job do Discord.
    pause
)
