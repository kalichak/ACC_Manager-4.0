# Servidor

## Responsabilidade

`core/server_controller.py` controla um ACC Dedicated Server local. A aba
correspondente é `ui/server_tab.py`.

## Fluxo

Ao iniciar, a UI salva as configurações, valida requisitos de servidor,
interrompe uma instância anterior quando necessário, opcionalmente remove
`cfg/current`, grava três arquivos JSON e executa `accServer.exe` no diretório
configurado.

- `settings.json`: nome, senhas, vagas e requisitos de rating.
- `configuration.json`: portas, descoberta LAN e lobby.
- `event.json`: pista, sessões, horário e clima.

Os JSON do servidor são escritos em UTF-16LE conforme esperado pelo ACC.
Parar o servidor procura processos chamados `accServer.exe` usando `psutil`.

## Configuração

Defina `ACC_SERVER_PATH` apontando para a pasta que contém `accServer.exe`.
O controle é opcional: a aplicação pode ser usada sem habilitar a aba.

## Contribuindo

Teste primeiro com uma instalação local do Dedicated Server e nunca inclua
arquivos `cfg`, senhas ou logs reais no commit. Mudanças no formato dos JSON
devem ser comparadas com a documentação/versão do ACC utilizada pelo
contribuidor; o projeto não valida esses esquemas externamente.
