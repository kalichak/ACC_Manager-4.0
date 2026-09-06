# Arquitetura real

## Visão geral

O ACC Manager é uma aplicação desktop PyQt6 executada por `main.py`. Não há
backend próprio: integrações externas são feitas diretamente pelos serviços em
`core/` usando arquivos locais, processos do ACC, REST do Supabase e webhooks
do Discord.

```text
main.py
  -> ui.main_window.ACCManagerApp
       -> ui/*_tab.py (mixins das abas)
       -> ui/settings_dialog.py e ui/i18n.py
       -> core/* (serviços)
            -> arquivos do ACC/MoTeC/Setups
            -> Supabase REST
            -> Discord Webhook
```

## Inicialização

`main.py` cria `QApplication`, aplica `ui.styles.DARK_STYLE`, configura o
ícone e instancia `ACCManagerApp`. `config.py` é importado durante a
inicialização: resolve a pasta base, lê ou cria `.env`, carrega os dados JSON,
importa os serviços e expõe as constantes usadas pela UI.

`ui/main_window.py` cria os serviços (`ServerController`, `MotecParser`,
`SetupManager`, `SetupCreator`, `LeaderboardClient` e `DiscordNotifier`) e
compõe as abas por herança múltipla de mixins. Os mixins não são widgets
independentes; a janela principal fornece o estado e os serviços usados por
eles.

## UI

- `ui/main_window.py`: janela, abas habilitadas, persistência de
  `ui_settings.json`, troca de idioma e reconstrução após configurações.
- `ui/server_tab.py`: formulário do servidor, clima, sessões e preview de
  pista.
- `ui/telemetry_tab.py`: lista de sessões MoTeC, filtros, detalhes e análise
  avançada `.ld`.
- `ui/setups_tab.py`: lista/edição de setups, presets, replicação, criador
  inteligente e análise.
- `ui/leaderboard_tab.py`: identidade do piloto, filtros, envio ao Supabase e
  ranking.
- `ui/settings_dialog.py`: edição de caminhos, integrações e módulos ativos.
- `ui/i18n.py`: dicionário em memória para português, inglês e alemão.
- `ui/styles.py` e `ui/dialogs.py`: tema e diálogos auxiliares.

## Core

- `server_controller.py`: escreve `settings.json`, `configuration.json` e
  `event.json` em UTF-16LE, inicia/encerra `accServer.exe` e limpa `current`.
- `motec_parser.py`: lê resumos XML `.ldx`, extrai volta, carro, pista, data e
  condições.
- `ld_telemetry_parser.py`: usa `core/vendor/ldparser.py` e marcadores `.ldx`
  para analisar canais binários `.ld`.
- `setup_manager.py`: lista, lê, salva, remove, clona e replica JSON de setups.
- `setup_creator.py`: gera variações de um setup válido com perfis de carro,
  pista, agressividade e condição.
- `track_profile_calibrator.py`: calcula e grava sugestões de perfil de pista
  a partir de voltas e telemetria.
- `leaderboard_client.py`: cliente REST insert/select do Supabase e redução
  do histórico ao melhor tempo por piloto/carro/pista.
- `discord_notifier.py`: envia mensagens e embeds por webhook.
- `data_loader.py`: fonte única, com cache por mtime, para
  `core/data/cars.json` e `core/data/tracks.json`.

## Dados e empacotamento

`assets/` contém imagens de pistas e o ícone. `build_exe.bat` gera um
distribuível PyInstaller `--onedir`, incluindo `core/data`, `assets` e a
licença vendorizada. `--onedir` é necessário porque a calibração pode gravar
em `core/data/tracks.json`.

## Fluxo de configuração

`.env` contém caminhos, idioma, módulos habilitados e credenciais opcionais.
`ui_settings.json` guarda valores de campos da UI. A tela de configurações
salva `.env`; `config.reload_env()` atualiza constantes e a janela reconstrói
abas e serviços sem reiniciar.
