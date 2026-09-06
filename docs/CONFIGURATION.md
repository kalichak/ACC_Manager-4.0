# Configuração

## Arquivos

- `.env`: caminhos, idioma, módulos e credenciais opcionais. É criado
  automaticamente e ignorado pelo Git.
- `ui_settings.json`: valores persistidos dos campos da interface; também é
  local e ignorado.
- `core/data/cars.json`: nomes, classes e temperamento dos carros.
- `core/data/tracks.json`: nomes, comprimento e perfis das pistas.

## Variáveis do `.env`

| Variável | Uso |
|---|---|
| `ACC_SERVER_PATH` | Pasta que contém `accServer.exe`. |
| `ACC_MOTEC_PATH` | Pasta dos arquivos `.ldx`/`.ld`. |
| `ACC_SETUPS_PATH` | Raiz dos setups `carro\pista`. |
| `SUPABASE_URL` | URL do projeto Supabase, opcional. |
| `SUPABASE_KEY` | Chave pública `anon`, opcional. |
| `DISCORD_WEBHOOK_URL` | Webhook Discord, opcional. |
| `ENABLED_MODULES` | Lista separada por vírgula: `server`, `telemetry`, `setups`, `leaderboard`. |
| `APP_LANGUAGE` | `pt`, `en` ou `de`. |

Use a tela de Configurações para editar os valores. O idioma e os módulos
podem ser alterados em tempo de execução; a janela é reconstruída sem reinício.

## Segurança

Não publique `.env`, chaves, webhooks, `ui_settings.json`, screenshots de
configurações ou arquivos de telemetria. A chave `anon` é pública por desenho,
mas ainda deve ser configurada localmente e acompanhada de RLS apropriada.
