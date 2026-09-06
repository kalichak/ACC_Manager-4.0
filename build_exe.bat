@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ===============================================
echo   ACC Manager - Build do executavel (.exe)
echo ===============================================
echo.

where py >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado.
    echo Instale Python 3.10+ e marque "Add Python to PATH".
    pause
    exit /b 1
)

if not exist venv (
    echo Criando ambiente virtual...
    py -3 -m venv venv
    if errorlevel 1 (
        echo [ERRO] Nao foi possivel criar a ambiente virtual.
        pause
        exit /b 1
    )
)

set "PYTHON=%~dp0venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo [ERRO] Python da virtualenv nao encontrado: "%PYTHON%"
    pause
    exit /b 1
)

echo Instalando dependencias (isso pode demorar na primeira vez)...
"%PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto :build_error
"%PYTHON%" -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto :build_error

echo.
echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Empacotando (modo --onedir)...
echo (--onedir e proposital: o Criador de Setups Inteligente e o
echo  calibrador de pistas ESCREVEM em core/data/*.json em tempo real.
echo  Isso so funciona com arquivos soltos ao lado do .exe - um --onefile
echo  extrai tudo pra uma pasta temporaria que e apagada ao fechar o
echo  programa, e essas gravacoes se perderiam.)
echo.

"%PYTHON%" -m PyInstaller ^
    --name ACCManager ^
    --onedir ^
    --icon "assets\icon.ico" ^
    --windowed ^
    --collect-all numpy ^
    --add-data "core\data;core\data" ^
    --add-data "assets;assets" ^
    --add-data "core\vendor\LICENSE-ldparser.txt;core\vendor" ^
    main.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo   O BUILD FALHOU. Rode de novo trocando --windowed por
    echo   --console no comando acima para ver a mensagem de erro
    echo   completa em uma janela de terminal.
    echo ============================================================
    pause
    exit /b 1
)

if not exist "dist\ACCManager\ACCManager.exe" goto :build_error
copy /y "run_acc_manager.bat" "dist\ACCManager\run_acc_manager.bat" >nul
if errorlevel 1 goto :build_error

echo.
echo ===============================================
echo   PRONTO! O executavel esta em:
echo   dist\ACCManager\ACCManager.exe
echo.
echo   IMPORTANTE: distribua a pasta INTEIRA "dist\ACCManager"
echo   pros seus amigos, nao so o .exe sozinho - ela contem os
echo   dados (core\data, assets) e as bibliotecas empacotadas.
echo   O arquivo run_acc_manager.bat tambem foi copiado para essa pasta.
echo ===============================================
pause
exit /b 0

:build_error
echo.
echo ============================================================
echo   O BUILD FALHOU. Confira a mensagem acima.
echo   Para diagnosticar, troque --windowed por --console no
echo   comando do PyInstaller e execute este arquivo novamente.
echo ============================================================
pause
exit /b 1
