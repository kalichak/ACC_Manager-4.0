# Copilot instructions for ACC Manager

## Project overview

ACC Manager is a Windows desktop application built with Python 3.10+ and PyQt6. It does not have a separate backend service; the app assembles UI and calls direct local/REST integrations from the `core/` layer.

The repository layout follows a simple split:

- `main.py` starts the Qt application and opens `ACCManagerApp`.
- `config.py` loads `.env`, resolves runtime paths, exposes app settings, and imports core services. It is the central configuration entry point.
- `ui/` contains the Qt window, tabs, dialogs, translations, and styling.
- `core/` contains domain logic: server control, telemetry parsing, setup management, leaderboard sync, and Discord notifications.
- `core/data/` provides car and track metadata used throughout the app.
- `assets/` contains images and the application icon.

The project is intentionally organized around multiple tab mixins in `ui/main_window.py`; keep those responsibilities separated from the business logic under `core/`.

## Build, test, and validation commands

Set up the environment from the repo root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the app locally:

```powershell
python main.py
```

Compile the Python sources (used by CI and the contribution guide):

```powershell
python -m compileall -q config.py core ui main.py test_discord_webhook.py
```

Run the test suite:

```powershell
python -m pytest -q
```

Run a single test file:

```powershell
python -m pytest -q tests/test_data_loader.py
```

Run a specific test or keyword selection:

```powershell
python -m pytest -q tests/test_data_loader.py -k normalize
```

Build the Windows distributable:

```powershell
.\build_exe.bat
```

This creates `dist\ACCManager\ACCManager.exe` and follows the repo’s `--onedir` packaging approach described in `EMPACOTAMENTO.md`.

## High-level architecture

The app is a single desktop process with a Qt UI shell and service modules that call external tools directly:

- `ui/main_window.py` creates the app window, enables/disables tabs, manages `ui_settings.json`, and swaps languages.
- `ui/*.py` tab modules represent specific product areas such as server control, telemetry, setups, and leaderboard.
- `core/server_controller.py` manages ACC server configuration and execution.
- `core/motec_parser.py` and `core/ld_telemetry_parser.py` parse MoTeC telemetry and `.ld` files.
- `core/setup_manager.py` and `core/setup_creator.py` handle setup storage and generation.
- `core/leaderboard_client.py` communicates with Supabase and stores leaderboard data.
- `core/discord_notifier.py` posts alerts and embeds via webhook.
- `core/data_loader.py` is the single source of truth for the tracked car and track metadata.

`.env` contains local paths, optional credentials, and module toggles. `ui_settings.json` stores UI-level values that are not meant to be treated as code. In runtime, `config.reload_env()` can rebuild app state without restarting the whole app.

## Key conventions specific to this repo

- Keep UI code in `ui/` and business logic in `core/`; do not mix heavy logic into Qt widgets.
- When changing user-visible text, add the key to all supported languages in `ui/i18n.py` instead of only one locale.
- Do not commit secrets, `.env` values, webhook URLs, real telemetry data, or generated files.
- Prefer focused changes and short feature/fix/docs branches from `main`.
- Before broad edits, consult `docs/START_HERE.md`, `docs/ARCHITECTURE.md`, and `CONTRIBUTING.md`.
- Preserve third-party legal constraints: `core/vendor/ldparser.py` remains under its own GPLv3 license and should not be redistributed without respecting that license.
- The project already uses automated validation in CI (`.github/workflows/quality.yml`), but the repo’s own guidance still treats `python -m compileall` and `pytest` as the minimum validation steps for PRs.

## Relevant docs

- `README.md`
- `CONTRIBUTING.md`
- `docs/START_HERE.md`
- `docs/ARCHITECTURE.md`
- `EMPACOTAMENTO.md`
