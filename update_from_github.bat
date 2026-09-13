@echo off
setlocal ENABLEDELAYEDEXPANSION

set "REPO_DIR=%~dp0"
cd /d "%REPO_DIR%"

rem --- 1. Usar o Python do Ambiente Virtual (venv) ---
set "PYTHON_CMD=python"
if exist "venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0venv\Scripts\python.exe"
)

rem --- 2. Validar dependencias (Git e Python) ---
where git >nul 2>nul
if errorlevel 1 (
    echo ERRO: Git nao encontrado no PATH. Instale o Git e tente novamente.
    pause
    exit /b 1
)

"!PYTHON_CMD!" --version >nul 2>nul
if errorlevel 1 (
    echo ERRO: Python nao encontrado. O caminho testado foi: "!PYTHON_CMD!"
    pause
    exit /b 1
)

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

rem Remove espacos em branco da escolha
set "CHOICE=%CHOICE: =%"

if "!CHOICE!"=="1" goto :UpdateMode
if "!CHOICE!"=="2" goto :ReleaseMode
if "!CHOICE!"=="3" goto :CheckOnly
if "!CHOICE!"=="4" exit /b 0
goto :Menu

rem ===========================================================================
rem MODO 1: ATUALIZAR DO GITHUB (PULL)
rem ===========================================================================
:UpdateMode
cls
echo ================================================
echo ACC Manager - Atualizacao do GitHub (Pull)
echo ================================================
echo Consultando informacoes...
call :GetLocalVersion
call :GetRemoteBranch
call :GetRemoteVersion

if /I "!REMOTE_VERSION!"=="unavailable" (
    echo AVISO: Nao foi possivel consultar a versao remota do GitHub. API com limite de taxa ou sem internet.
    pause
    goto :Menu
)

call :HasLocalChanges
if "!LOCAL_DIRTY!"=="YES" (
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

echo.
echo [2/3] Atualizando branch !REMOTE_BRANCH!...
git checkout !REMOTE_BRANCH!
git pull --ff-only origin !REMOTE_BRANCH!
if errorlevel 1 (
    echo.
    echo ERRO: Falha no pull. Pode haver conflitos locais.
    pause
    goto :Menu
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

if not exist "core\version_manager.py" (
    echo ERRO: Arquivo 'version_manager.py' nao encontrado na pasta 'core'!
    pause
    goto :Menu
)

echo [1/5] Analisando alteracoes e gerando manifesto (Python)...
"!PYTHON_CMD!" core\version_manager.py
if errorlevel 1 (
    echo ERRO: O Python falhou. Leia a mensagem de erro acima.
    pause
    goto :Menu
)

echo.
echo [2/5] Lendo nova versao do manifesto...
set "NEW_VERSION=unknown"
for /f "delims=" %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='%~dp0version.json'; if(Test-Path $p){$j=Get-Content $p -Raw|ConvertFrom-Json; if($j.next_version){$j.next_version}else{'unknown'}}else{'unknown'}"') do set "NEW_VERSION=%%i"

if "!NEW_VERSION!"=="unknown" (
    echo ERRO: Nao foi possivel ler a next_version no version.json.
    pause
    goto :Menu
)
echo Nova versao calculada pelo Python: !NEW_VERSION!

echo.
echo [3/5] Verificando se a versao realmente subiu...
git tag -l | findstr /x "v!NEW_VERSION!" >nul
if not errorlevel 1 (
    echo ============================================================
    echo ALERTA: A Tag v!NEW_VERSION! ja existe no GitHub/Git!
    echo O Python manteve a mesma versao porque nao encontrou
    echo novos arquivos modificados no seu projeto para subir.
    echo.
    echo Faca alguma alteracao no codigo para a versao poder subir.
    echo ============================================================
    pause
    goto :Menu
)

echo Promovendo nova versao no version.json...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='%~dp0version.json'; $j=Get-Content $p -Raw|ConvertFrom-Json; $j.current_version=$j.next_version; $j|ConvertTo-Json -Depth 10|Set-Content $p"

echo.
echo [4/5] Preparando Commit e Tag (v!NEW_VERSION!)...
git add version.json
git add .
git diff --cached --quiet
if not errorlevel 1 (
    echo AVISO: Nenhuma alteracao alem do version.json foi detectada.
)

git commit -m "chore: release version !NEW_VERSION!"
git tag -a "v!NEW_VERSION!" -m "Release v!NEW_VERSION!"

echo.
echo [5/5] Enviando codigo e tag para o GitHub...
git push origin HEAD
if errorlevel 1 (
    echo ERRO: Falha ao enviar o codigo (Push). Verifique suas permissoes.
    pause
    goto :Menu
)

git push origin "v!NEW_VERSION!"
if errorlevel 1 (
    echo ERRO: Falha ao enviar a tag (Push tags).
    pause
    goto :Menu
)

echo.
echo ================================================
echo SUCESSO! Versao v!NEW_VERSION! publicada e enviada.
echo ================================================
pause
goto :Menu


rem ===========================================================================
rem MODO 3: APENAS CHECAR
rem ===========================================================================
:CheckOnly
cls
echo ================================================
echo Verificacao de versao do GitHub
echo ================================================
echo Consultando API do GitHub, aguarde...
echo.

call :GetLocalVersion
call :GetRemoteBranch
call :GetRemoteVersion

echo Versao local : !LOCAL_VERSION!
echo Versao remota: !REMOTE_VERSION!
echo Branch remota: !REMOTE_BRANCH!
echo.
if /I "!LOCAL_VERSION!"=="!REMOTE_VERSION!" (
    echo Estado: Sincronizado com o GitHub.
) else (
    echo Estado: Desatualizado ^(Atualizacao/Release disponivel^).
    if "!REMOTE_VERSION!"=="unavailable" (
        echo.
        echo ^(A API do GitHub pode ter bloqueado a consulta por excesso de tentativas.^)
    )
)
echo.
pause
goto :Menu


rem ===========================================================================
rem HELPERS
rem ===========================================================================
:GetLocalVersion
set "LOCAL_VERSION=unknown"
for /f "delims=" %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='%~dp0version.json'; if(Test-Path $p){$j=Get-Content $p -Raw|ConvertFrom-Json; if($j.current_version){$j.current_version}else{'unknown'}}else{'unknown'}"') do set "LOCAL_VERSION=%%i"
exit /b 0

:GetRemoteBranch
set "REMOTE_BRANCH=main"
for /f "delims=" %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $u='https://api.github.com/repos/kalichak/ACC_Manager-4.0'; try{$r=Invoke-RestMethod -Uri $u -Headers @{'User-Agent'='ACCManagerBot'}; if($r.default_branch){$r.default_branch}else{'main'}}catch{'main'}"') do set "REMOTE_BRANCH=%%i"
exit /b 0

:GetRemoteVersion
set "REMOTE_VERSION=unavailable"
for /f "delims=" %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $b='main'; try{$u='https://api.github.com/repos/kalichak/ACC_Manager-4.0'; $r=Invoke-RestMethod -Uri $u -Headers @{'User-Agent'='ACCManagerBot'}; if($r.default_branch){$b=$r.default_branch}}catch{} $raw='https://raw.githubusercontent.com/kalichak/ACC_Manager-4.0/'+$b+'/version.json'; try{$c=Invoke-WebRequest -Uri $raw -UseBasicParsing; $j=$c.Content|ConvertFrom-Json; if($j.current_version){$j.current_version}else{'unavailable'}}catch{'unavailable'}"') do set "REMOTE_VERSION=%%i"
exit /b 0

:HasLocalChanges
set "LOCAL_DIRTY=NO"
for /f %%i in ('git status --porcelain') do set "LOCAL_DIRTY=YES"
exit /b 0