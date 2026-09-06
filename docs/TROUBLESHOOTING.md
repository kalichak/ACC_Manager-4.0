# Solução de problemas

## PyQt6 ou dependências ausentes

Ative a virtualenv e rode `pip install -r requirements.txt`. Se o erro ocorre
ao abrir o executável, gere novamente com `build_exe.bat` e distribua a pasta
inteira `dist\ACCManager`.

## Caminho não encontrado

Confira `ACC_SERVER_PATH`, `ACC_MOTEC_PATH` e `ACC_SETUPS_PATH`. A aplicação
mostra um aviso na inicialização quando uma pasta habilitada não existe.

## Servidor não inicia

Confirme que `accServer.exe` existe no caminho configurado, que os arquivos
podem ser escritos em `cfg` e que outra instância não está bloqueando o
processo. Use o build `--console` temporariamente para obter erros de
inicialização do empacotamento.

## Telemetria ou setups vazios

Confirme a estrutura de pastas e extensões. Telemetria resumida usa `.ldx` e a
análise avançada requer o `.ld` correspondente. Setups são procurados em
`ACC_SETUPS_PATH\carro\pista\*.json`.

## Ranking ou Discord desconectado

Verifique URL, chave `anon`, tabela/políticas RLS e conectividade. Para Discord,
confirme que o webhook ainda existe. Não cole credenciais em issues; redija
logs e screenshots antes de anexá-los.

## Idioma ou módulos

Valores reconhecidos são `pt`, `en`, `de` e os quatro nomes de módulos
documentados em [CONFIGURATION.md](CONFIGURATION.md). Textos novos devem ter
chave nos três blocos de `ui/i18n.py`.
