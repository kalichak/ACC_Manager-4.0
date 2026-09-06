# ACC Manager

[Português (BR)](README.md) | [English](README.en.md) | [Deutsch](README.de.md)

Aplicativo desktop gratuito e open source para gerenciamento de servidores
LAN do **Assetto Corsa Competizione (ACC)**.

O ACC Manager reúne em uma única interface o controle do servidor dedicado,
a leitura de telemetria, o gerenciamento de setups, o ranking entre amigos e
as notificações via Discord.

## Recursos

- **Servidor LAN / Radmin**
  - Inicia e encerra o servidor dedicado do ACC.
  - Configura pista, carro, sessões, clima e condições de corrida.
  - Exibe o status do servidor e envia notificações para o Discord.
 <img width="1279" height="789" alt="SERVER - PT BR" src="https://github.com/user-attachments/assets/fd34fb56-8f04-45bb-9e16-82a9b74198d1" />
 
- **Telemetria**
  - Lê sessões gravadas pelo MoTeC.
  - Analisa arquivos `.ld` e `.ldx`.
  - Exibe voltas, tempos, velocidade média, frenagens, forças G e consistência.
  - Ajusta perfis de pistas com base nos dados de telemetria.
 <img width="1278" height="945" alt="TELEMETRY PT-BR" src="https://github.com/user-attachments/assets/18393002-10c1-47ad-83cd-0c7dad6f8000" />

- **Gerenciador de setups**
  - Lista, filtra, visualiza e edita setups do ACC.
  - Replica setups para outros carros ou pistas.
  - Ajusta pressões para compatibilidade com o ACC 1.9.
  - Cria sugestões de setup com base no carro, pista e estilo de condução.
 <img width="1280" height="1389" alt="SETUPS PT-BR" src="https://github.com/user-attachments/assets/ab42d7e2-d502-44b0-90a2-23ec0b5f5975" />

- **Ranking**
  - Publica melhores tempos em uma tabela compartilhada no Supabase.
  - Filtra resultados por carro e pista.
  - Mantém o histórico de voltas e o melhor tempo de cada piloto.
<img width="1279" height="789" alt="SERVER - PT BR" src="https://github.com/user-attachments/assets/fd34fb56-8f04-45bb-9e16-82a9b74198d1" />

- **Módulos e idiomas**
  - Ative ou desative as abas de servidor, telemetria, setups e ranking
    individualmente nas configurações, sem reiniciar o programa.
  - Troque o idioma da interface em tempo real entre português, inglês e
    alemão.
<img width="927" height="609" alt="image" src="https://github.com/user-attachments/assets/f094ca3e-428d-4e92-9317-094150a9895c" />

## Requisitos

- Windows 10 ou superior.
- Python 3.10 ou superior.
- Assetto Corsa Competizione.
- Servidor dedicado do ACC, caso queira usar o controle do servidor.
- MoTeC i2 Pro e arquivos de telemetria, caso queira usar a análise de
  telemetria.
- Conta no Supabase, somente para o ranking compartilhado.

## Instalação

Abra o PowerShell na pasta do projeto e execute:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação do ambiente virtual, execute:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

## Executando

Com o ambiente virtual ativado:

```powershell
python main.py
```

## Configuração

Na primeira execução, o programa cria um arquivo `.env` com caminhos padrão.
Também é possível alterar os diretórios pela tela de configurações.

Um exemplo de configuração é:

```dotenv
ACC_SERVER_PATH=C:\Steam\steamapps\common\Assetto Corsa Competizione Dedicated Server\server
ACC_MOTEC_PATH=C:\Users\SEU_USUARIO\Documents\Assetto Corsa Competizione\MoTeC
ACC_SETUPS_PATH=C:\Users\SEU_USUARIO\Documents\Assetto Corsa Competizione\Setups
SUPABASE_URL=
SUPABASE_KEY=
DISCORD_WEBHOOK_URL=
```

O arquivo `.env` pode conter credenciais e nunca deve ser publicado. Ele já
está incluído no `.gitignore`.

## Gerando o executável

No Windows, execute:

```powershell
.\build_exe.bat
```

O executável será criado em:

```text
dist\ACCManager\ACCManager.exe
```

Distribua a pasta inteira `dist\ACCManager`, e não apenas o arquivo `.exe`.
Consulte [EMPACOTAMENTO.md](EMPACOTAMENTO.md) para entender o modo
`--onedir`, os arquivos incluídos e a solução de problemas.

## Estrutura do projeto

```text
main.py              Ponto de entrada da aplicação
config.py            Configuração, .env e caminhos do aplicativo
core\                Lógica de servidor, telemetria, setups e ranking
ui\                  Janela principal, abas, diálogos e estilos
core\data\            Bases de carros e pistas
assets\              Imagens e recursos visuais
build_exe.bat        Script de empacotamento para Windows
```

## Dependências de terceiros

O arquivo `core\vendor\ldparser.py` é usado pela análise avançada de
telemetria `.ld`. Ele é distribuído sob a licença GPLv3 original, disponível
em [core/vendor/LICENSE-ldparser.txt](core/vendor/LICENSE-ldparser.txt).
Essa licença continua válida para o código vendorizado e deve ser respeitada
ao redistribuir o projeto.

## Contribuindo

Contribuições são bem-vindas. Você pode estudar o código, criar uma branch,
corrigir bugs, adicionar recursos, adaptar o projeto às suas necessidades e
redistribuir suas alterações conforme os termos da licença MIT.

Fluxo sugerido:

```powershell
git clone https://github.com/kalichak/ACC_Manager-4.0.git
cd "ACC_Manager 4.0"
git switch -c minha-alteracao
```

Antes de abrir um pull request:

1. Descreva claramente o problema ou recurso.
2. Mantenha credenciais e arquivos `.env` fora do commit.
3. Teste a aplicação e execute `python -m compileall -q config.py core ui main.py`.
4. Explique no pull request o que foi alterado e como testar.

## Novas implementações

As versões recentes reorganizaram a aplicação em módulos independentes,
adicionaram seleção de idioma em tempo real e permitiram ocultar os módulos
que não serão usados. A configuração é preservada no `.env`, enquanto os
campos da interface continuam salvos em `ui_settings.json` local.

## Licença do ACC Manager

O código original deste projeto é distribuído gratuitamente sob a
[Licença MIT](LICENSE). Ela permite usar, copiar, modificar, combinar,
publicar e redistribuir o software, inclusive em projetos comerciais, desde
que o aviso de copyright e o texto da licença sejam mantidos.

Essa licença MIT não substitui nem altera as licenças das dependências de
terceiros. Em particular, `core\vendor\ldparser.py` permanece sob GPLv3,
conforme indicado acima.

## Aviso

ACC Manager é um projeto independente e não é afiliado à KUNOS Simulazioni,
505 Games, MoTeC, Discord ou Supabase.
