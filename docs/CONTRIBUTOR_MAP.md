# Mapa para contribuidores

| Área | Onde procurar | Responsabilidade |
|---|---|---|
| UI | `ui/main_window.py`, `ui/*_tab.py`, `ui/settings_dialog.py` | Widgets, eventos, composição e configurações |
| Server | `ui/server_tab.py`, `core/server_controller.py` | Formulário e controle do Dedicated Server |
| Telemetry | `ui/telemetry_tab.py`, `core/motec_parser.py`, `core/ld_telemetry_parser.py` | `.ldx`, `.ld`, métricas e scores |
| Setups | `ui/setups_tab.py`, `core/setup_manager.py`, `core/setup_creator.py` | JSON de setups, presets e criação inteligente |
| Ranking | `ui/leaderboard_tab.py`, `core/leaderboard_client.py` | Supabase, melhores tempos e filtros |
| Configuration | `config.py`, `ui/settings_dialog.py`, `.env` | Caminhos, idioma, módulos e credenciais |
| Build/Infrastructure | `build_exe.bat`, `ACCManager.spec`, `EMPACOTAMENTO.md`, `.github/` | PyInstaller, CI e manutenção |
| Documentation | `README*.md`, `CONTRIBUTING.md`, `docs/` | Uso, arquitetura e processo |

Dados de carros e pistas ficam em `core/data/`; imagens e ícone ficam em
`assets/`. O arquivo `test_discord_webhook.py` é um teste manual de integração.
