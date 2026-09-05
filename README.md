# ACC Manager

Aplicativo desktop para gerenciamento de servidores LAN do Assetto Corsa
Competizione (ACC), leitura de telemetria, criacao de setups e ranking.

## Requisitos

- Windows
- Python 3.10 ou superior
- Assetto Corsa Competizione
- Servidor dedicado do ACC, caso use a aba de servidor
- MoTeC i2 Pro e arquivos de telemetria, caso use a analise de telemetria

## Instalacao

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Na primeira execucao, o programa cria um arquivo `.env` com caminhos padrao.
Tambem e possivel ajustar os diretorios pela tela de configuracoes.

O `.env` pode conter credenciais do Supabase e a URL do webhook do Discord.
Ele e ignorado pelo Git e nunca deve ser publicado.

## Empacotamento

Para gerar o executavel no Windows, execute `build_exe.bat`. O resultado fica
em `dist\ACCManager\ACCManager.exe`; distribua a pasta inteira. Consulte
`EMPACOTAMENTO.md` para detalhes sobre o modo `--onedir`.

## Funcionalidades

- Controle do servidor dedicado e notificacoes via Discord.
- Leitura e analise de telemetria MoTeC.
- Gerenciamento e criacao inteligente de setups.
- Ranking compartilhado via Supabase.
