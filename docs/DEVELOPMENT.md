# Desenvolvimento

## Ambiente

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

O projeto depende de PyQt6, psutil, requests, numpy e pytest. O sistema
operacional suportado pelo fluxo real de desenvolvimento e build é Windows.

## Execução

```powershell
python main.py
# ou
.\run_acc_manager.bat
```

O `.env` e `ui_settings.json` são locais. Se o PowerShell bloquear a ativação,
use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`.

## Validação

```powershell
python -m compileall -q config.py core ui main.py test_discord_webhook.py
python -m pytest -q
```

Não existe atualmente uma suíte automatizada abrangente. O teste existente de
webhook é manual e envia requisições reais; não o execute com credenciais em
CI.

## Convenções

Mantenha a lógica de integração em `core/`, a composição/experiência em `ui/`
e os dados de carros/pistas em JSON. Evite duplicar a fonte de dados em Python.
Mudanças de comportamento devem atualizar a documentação correspondente.

## Build

`build_exe.bat` instala PyInstaller, limpa `build/` e `dist/` e gera
`dist\ACCManager\ACCManager.exe`. Consulte `EMPACOTAMENTO.md` antes de alterar
o processo.
