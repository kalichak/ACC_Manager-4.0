# Contribuindo para o ACC Manager

Obrigado por considerar uma contribuição. O ACC Manager é uma aplicação
desktop para Windows, escrita em Python com PyQt6, e aceita melhorias de
 código, documentação, dados de carros/pistas e suporte ao desenvolvimento.

## Antes de começar

Leia [docs/START_HERE.md](docs/START_HERE.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
e [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md). Para mudanças de comportamento,
consulte também o módulo correspondente em `docs/`.

Nunca envie `.env`, `ui_settings.json`, credenciais, webhooks ou dados
extraídos de telemetria. Use valores vazios ou exemplos fictícios.

## Configurando o ambiente

Requisitos:

- Windows 10 ou superior.
- Python 3.10 ou superior.
- Assetto Corsa Competizione para testar integrações reais.
- MoTeC i2 Pro e arquivos de telemetria apenas para trabalhar no módulo de
  telemetria.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

O aplicativo cria `.env` na primeira execução. Consulte
[docs/CONFIGURATION.md](docs/CONFIGURATION.md) para configurar caminhos e
integrações sem expor segredos.

## Estrutura e branches

Use uma branch curta baseada em `main`:

```powershell
git switch main
git pull --ff-only
git switch -c tipo/descricao-curta
```

Prefira `feature/`, `fix/`, `docs/`, `refactor/` ou `ci/`. Não desenvolva
diretamente em `main`.

## Testes e validações

Antes de abrir um Pull Request:

```powershell
python -m compileall -q config.py core ui main.py test_discord_webhook.py
python -m pytest -q
```

O arquivo `test_discord_webhook.py` é um teste manual de integração, não um
teste automatizado seguro para CI: ele envia mensagens reais se houver um
webhook no `.env`. Não execute esse script em CI nem inclua um webhook no
repositório. O projeto ainda não possui uma suíte automatizada abrangente.

Para validar o empacotamento no Windows:

```powershell
.\build_exe.bat
```

Distribua a pasta inteira `dist\ACCManager`, conforme
[EMPACOTAMENTO.md](EMPACOTAMENTO.md).

## Commits

Escreva mensagens claras no imperativo e mantenha cada commit focado:

```text
Add German translations for telemetry labels
Fix setup replication for missing target directories
Document Supabase configuration
```

Não inclua segredos, arquivos gerados ou alterações não relacionadas.

## Pull Requests

Um Pull Request deve:

1. Explicar o problema e a solução.
2. Indicar os arquivos e módulos afetados.
3. Descrever como validar a mudança.
4. Informar limitações, dependências externas ou passos manuais.
5. Incluir screenshots para mudanças visuais, sem dados pessoais ou segredos.

O template solicitará essas informações. Mudanças maiores devem incluir ou
atualizar documentação e, quando aplicável, um ADR em `docs/decisions/`.

## Dados e licenças

Carros e pistas são mantidos em `core/data/cars.json` e
`core/data/tracks.json`. O código principal está sob MIT, mas
`core/vendor/ldparser.py` possui licença GPLv3 própria. Leia
[docs/LICENSING.md](docs/LICENSING.md) antes de redistribuir ou alterar
componentes de terceiros.
