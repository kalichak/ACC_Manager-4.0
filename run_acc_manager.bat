@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "APP=%~dp0dist\ACCManager\ACCManager.exe"
if not exist "%APP%" set "APP=%~dp0ACCManager.exe"
if exist "%APP%" (
    start "ACC Manager" "%APP%"
    exit /b 0
)

echo O executavel empacotado nao foi encontrado:
echo "%APP%"
echo.
echo Execute build_exe.bat nesta pasta para gerar a versao distribuivel.
echo O fallback abaixo e apenas para desenvolvimento e exige Python e dependencias.
where python >nul 2>&1
if errorlevel 1 goto :missing_python
python main.py
if errorlevel 1 goto :run_error
exit /b 0

:missing_python
echo Python nao encontrado. Para usar este .bat sem Python, distribua a pasta dist\ACCManager.
pause
exit /b 1

:run_error
echo.
echo Falha na execucao do app em modo desenvolvimento.
pause
exit /b 1
