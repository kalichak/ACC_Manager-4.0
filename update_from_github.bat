@echo off
setlocal ENABLEDELAYEDEXPANSION

set "REPO_DIR=%~dp0"
cd /d "%REPO_DIR%"

rem --- Validar dependencias (Git e Python) ----------------------------------
where git >nul 2>nul
if errorlevel 1 (
    echo ERRO: Git nao encontrado no PATH. Instale o Git e tente novamente.
    pause
    exit /b 1
)
where python >nul 2>nul
if errorlevel 1 (
    echo ERRO: Python nao encontrado no PATH. Instale o Python para gerar as versoes.
    pause
    exit /b 1
)

rem --- Modo por argumento (opcional) -----------------------------------------
set "MODE=%~1"
if /I "%MODE%"=="--check" goto :CheckOnly
if /I "%MODE%"=="check" goto :CheckOnly
if /I "%MODE%"=="-c" goto :CheckOnly
if /I "%MODE%"=="update" goto :UpdateMode
if /I "%MODE%"=="release" goto :ReleaseMode

:Menu
cls
echo ================================================
echo ACC Manager - Gerenciador Git e Versao
echo ================================================
echo.
echo 1. Baixar atualizacoes do GitHub (Pull)
echo 2. Versionar, Commitar e Enviar (Release / Push)
echo 3. Apenas verificar status de versao
echo 4. Sair
echo.
set /p "CHOICE=Escolha uma opcao (1-4): "

if "%CHOICE%"=="1" goto :UpdateMode
if "%CHOICE%"=="2" goto :ReleaseMode
if "%CHOICE%"=="3" goto :CheckOnly
if "%CHOICE%"=="4" exit /b 0
goto :Menu

rem ===========================================================================
rem MODO 1: ATUALIZAR DO GITHUB (PULL)
rem ===========================================================================
:UpdateMode
cls
echo ================================================
echo ACC Manager - Atualizacao do GitHub (Pull)
echo ================================================
call :GetLocalVersion
call :GetRemoteBranch
call :GetRemoteVersion

if /I "%REMOTE_VERSION%"=="unavailable" (
    echo AVISO: Nao foi possivel consultar a versao remota do GitHub.
    echo Tente novamente mais tarde.
    pause
    exit /b 1
)

call :HasLocalChanges
if "%LOCAL_DIRTY%"=="YES" (
    echo.
    echo ERRO: Existem alteracoes locais nao salvas.
    echo Faca o Release ^(Opcao 2^) ou stash antes de baixar atualizacoes.
    echo.
    git status --short
    pause
    goto :Menu
)

echo.
echo [1/3] Buscando atualizacoes do GitHub...
git fetch --all --tags --prune
if errorlevel 1 (
    echo Falha ao buscar atualizacoes.
    pause
    exit /b 1
)

echo.
echo [2/3] Atualizando branch %REMOTE_BRANCH%...
git checkout %REMOTE_BRANCH%
git pull --ff-only origin %REMOTE_BRANCH%
if errorlevel 1 (
    echo.
    echo Falha no pull. Pode haver conflitos locais.
    pause
    exit /b 1
)

echo.
echo [3/3] Atualizacao concluida com sucesso.
pause
goto :Menu

rem ===========================================================================
rem MODO 2: VERSIONAR, COMMITAR, TAG E PUSH
rem ===========================================================================
:ReleaseMode
cls
echo ================================================
echo ACC Manager - Versionamento e Push
echo ================================================
echo.

rem 👇 MUDANÇA AQUI: Agora ele procura dentro da pasta core 👇
if not exist "core\version_manager.py" (
    echo ERRO: Arquivo 'version_manager.py' nao encontrado na pasta 'core'!
    pause
    goto :Menu
)

echo [1/5] Analisando alteracoes e gerando manifesto (Python)...
rem 👇 MUDANÇA AQUI: Executa o python apontando para a pasta core 👇
python core\version_manager.py >nul 2>&1
if errorlevel 1 (
    echo ERRO: Falha ao executar o script version_manager.py.
    pause
    exit /b 1
)

echo.
echo [2/5] Lendo nova versao do manifesto...
for /f "delims=" %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$p = Join-Path (Get-Location).Path 'version.json'; if(Test-Path $p){$j = Get-Content $p -Raw | ConvertFrom-Json; if($j.next_version){$j.next_version}else{'unknown'}} else {'unknown'}"') do set "NEW_VERSION=%%i"

if "%NEW_VERSION%"=="unknown" (
    echo ERRO: Nao foi possivel ler a next_version no version.json.
    pause
    exit /b 1
)
echo Nova versao calculada: %NEW_VERSION%

echo.
echo [3/5] Promovendo nova versao no version.json...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p = 'version.json'; $j = Get-Content $p -Raw | ConvertFrom-Json; $j.current_version = $j.next_version; $j | ConvertTo-Json -Depth 10 | Set-Content $p"

echo.
echo [4/5] Preparando Commit e Tag (v%NEW_VERSION%)...
git add .
git diff --cached --quiet
if %errorlevel%==0 (
    echo Nenhuma alteracao identificada pelo Git para commitar.
    pause
    goto :Menu
)

git commit -m "chore: release version %NEW_VERSION%"
git tag -a "v%NEW_VERSION%" -m "Release v%NEW_VERSION%"

echo.
echo [5/5] Enviando codigo e tag para o GitHub...
git push origin HEAD
if errorlevel 1 (
    echo ERRO: Falha ao enviar o codigo (Push). Verifique suas permissoes.
    pause
    exit /b 1
)

git push origin "v%NEW_VERSION%"
if errorlevel 1 (
    echo ERRO: Falha ao enviar a tag (Push tags).
    pause
    exit /b 1
)

echo.
echo ================================================
echo SUCESSO! Versao v%NEW_VERSION% publicada e enviada.
echo ================================================
pause
goto :Menu


rem ===========================================================================
rem MODO 3: APENAS CHECAR
rem ===========================================================================
:CheckOnly
cls
call :GetLocalVersion
call :GetRemoteBranch
call :GetRemoteVersion
echo ================================================
echo Verificacao de versao do GitHub
echo ================================================
echo.
echo Versao local: %LOCAL_VERSION%
echo Versao remote: %REMOTE_VERSION%
echo Branch remota: %REMOTE_BRANCH%
echo.
if /I "%LOCAL_VERSION%"=="%REMOTE_VERSION%" (
    echo Estado: Sincronizado.
) else (
    echo Estado: Desatualizado (Atualizacao/Release disponivel).
)
echo.
pause
goto :Menu


rem ===========================================================================
rem HELPERS
rem ===========================================================================
:GetLocalVersion
for /f "delims=" %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$p = Join-Path (Get-Location).Path 'version.json'; if(Test-Path $p){$j = Get-Content $p -Raw | ConvertFrom-Json; if($j.current_version){$j.current_version}else{'unknown'}} else {'unknown'}"') do set "LOCAL_VERSION=%%i"
exit /b 0

:GetRemoteBranch
for /f "delims=" %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$u = 'https://api.github.com/repos/kalichak/ACC_Manager-4.0'; try { $r = Invoke-RestMethod -Uri $u -Headers @{ 'User-Agent'='ACCManagerBot' }; if($r.default_branch){$r.default_branch}else{'main'} } catch { 'main' }"') do set "REMOTE_BRANCH=%%i"
exit /b 0

:GetRemoteVersion
for /f "delims=" %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$b = 'main'; try { $u='https://api.github.com/repos/kalichak/ACC_Manager-4.0'; $r = Invoke-RestMethod -Uri $u -Headers @{ 'User-Agent'='ACCManagerBot' }; if($r.default_branch){$b=$r.default_branch} } catch {} $raw = 'https://raw.githubusercontent.com/kalichak/ACC_Manager-4.0/' + $b + '/version.json'; try { $content = Invoke-WebRequest -Uri $raw -UseBasicParsing; $j = $content.Content | ConvertFrom-Json; if($j.current_version){$j.current_version}else{'unavailable'} } catch { 'unavailable' }"') do set "REMOTE_VERSION=%%i"
exit /b 0

:HasLocalChanges
set "LOCAL_DIRTY=NO"
for /f %%i in ('git status --porcelain') do set "LOCAL_DIRTY=YES"
exit /b 0