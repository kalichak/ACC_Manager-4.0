@echo off
setlocal
cd /d "%~dp0"

echo ===============================================
echo   ACC Manager - Build do executavel (.exe)
echo ===============================================
echo.

if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Instalando dependencias (isso pode demorar na primeira vez)...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist ACCManager.spec del ACCManager.spec

echo.
echo Empacotando (modo --onedir)...
echo (--onedir e proposital: o Criador de Setups Inteligente e o
echo  calibrador de pistas ESCREVEM em core/data/*.json em tempo real.
echo  Isso so funciona com arquivos soltos ao lado do .exe - um --onefile
echo  extrai tudo pra uma pasta temporaria que e apagada ao fechar o
echo  programa, e essas gravacoes se perderiam.)
echo.

pyinstaller ^
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

echo.
echo ===============================================
echo   PRONTO! O executavel esta em:
echo   dist\ACCManager\ACCManager.exe
echo.
echo   IMPORTANTE: distribua a pasta INTEIRA "dist\ACCManager"
echo   pros seus amigos, nao so o .exe sozinho - ela contem os
echo   dados (core\data, assets) e as bibliotecas empacotadas.
echo ===============================================
pause
