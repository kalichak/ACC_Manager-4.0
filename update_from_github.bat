@echo off
setlocal ENABLEDELAYEDEXPANSION

set "REPO_DIR=%~dp0"
cd /d "%REPO_DIR%"

set "MODE=%~1"
if "%MODE%"=="" set "MODE=update"

rem --- helpers ---------------------------------------------------------------
call :GetLocalVersion
call :GetRemoteBranch
call :GetRemoteVersion

if /I "%MODE%"=="--check" goto :CheckOnly
if /I "%MODE%"=="check" goto :CheckOnly
if /I "%MODE%"=="-c" goto :CheckOnly

:Banner
cls
echo ================================================
echo ACC Manager - Atualizacao do GitHub
echo ================================================
echo.
echo Versao local: %LOCAL_VERSION%
echo Versao remote: %REMOTE_VERSION%
echo Branch remota: %REMOTE_BRANCH%

echo.
if /I "%LOCAL_VERSION%"=="unknown" (
    echo AVISO: nao foi possivel ler version.json local.
)

if /I "%REMOTE_VERSION%"=="unavailable" (
    echo AVISO: nao foi possivel consultar a versao remota do GitHub.
    echo Tente novamente mais tarde ou verifique sua conexao com a internet.
    pause
    exit /b 1
)

if /I "%LOCAL_VERSION%"=="%REMOTE_VERSION%" (
    echo Sua versao ja esta atualizada.
    echo.
    echo Deseja forcar verificacao de atualizacao no GitHub?
    echo Use: update_from_github.bat --check
    echo.
    set /p "CONTINUE=Pressione Enter para atualizar mesmo assim ou CTRL+C para sair: "
)

rem --- validate Git ---------------------------------------------------------
where git >nul 2>nul
if errorlevel 1 (
    echo Git nao encontrado no PATH.
    echo Instale o Git e tente novamente.
    pause
    exit /b 1
)

rem --- check local dirty state ---------------------------------------------
call :HasLocalChanges
if "%LOCAL_DIRTY%"=="YES" (
    echo.
    echo Existem alteracoes locais nao salvas.
    echo Commit ou stash antes de atualizar.
    echo.
    git status --short
    pause
    exit /b 1
)

rem --- fetch and pull -------------------------------------------------------
 echo.
 echo [1/3] Buscando atualizacoes do GitHub...
 git fetch --all --tags --prune
 if errorlevel 1 (
     echo Falha ao buscar atualizacoes.
     echo Verifique a conexao com a internet e o acesso ao repositorio.
     pause
     exit /b 1
 )

 echo.
 echo [2/3] Atualizando branch %REMOTE_BRANCH%...
 git checkout %REMOTE_BRANCH%
 if errorlevel 1 (
     echo Falha ao trocar para a branch remota.
     pause
     exit /b 1
 )

 git pull --ff-only origin %REMOTE_BRANCH%
 if errorlevel 1 (
     echo.
     echo Falha no pull em modo fast-forward.
     echo Pode haver conflitos locais ou branch divergente.
     echo Tente: git status ; git pull --rebase origin %REMOTE_BRANCH%
     pause
     exit /b 1
 )

 echo.
 echo [3/3] Verificando versao final...
 call :GetLocalVersion
 echo Versao local apos atualizacao: %LOCAL_VERSION%
 echo.
 echo Atualizacao concluida com sucesso.
 echo.
 pause
 exit /b 0

:CheckOnly
 echo.
 echo ================================================
 echo Verificacao de versao do GitHub
 echo ================================================
 echo.
 echo Versao local: %LOCAL_VERSION%
 echo Versao remote: %REMOTE_VERSION%
 echo Branch remota: %REMOTE_BRANCH%
 echo.
 if /I "%LOCAL_VERSION%"=="%REMOTE_VERSION%" (
     echo Estado: sincronizado.
 ) else (
     echo Estado: atualizacao disponivel.
 )
 echo.
 exit /b 0

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
