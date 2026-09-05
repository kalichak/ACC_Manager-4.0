@echo off
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo Falha na execucao do app.
    echo Verifique se o Python e as dependencias estao instaladas.
    pause
)
