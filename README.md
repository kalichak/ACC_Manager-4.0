# ACC Manager

Aplicativo desktop para gerenciamento de servidores LAN do **Assetto Corsa Competizione (ACC)**, leitura de telemetria, criação de setups e compartilhamento de ranking entre amigos.

## Funcionalidades

- **Servidor LAN / Radmin**
  - Inicia e encerra o `accServer.exe`.
  - Configura nome, pista, carro, sessões, clima e condições da corrida.
  - Permite acompanhar o status do servidor e enviar notificações ao Discord.
- **Telemetria e rating**
  - Lê sessões gravadas pelo MoTeC.
  - Exibe voltas, carro, pista, tempo, temperatura e condições da sessão.
  - Analisa arquivos `.ld` e `.ldx`, incluindo velocidade média, frenagens fortes, forças G e consistência.
  - Sugere ajustes de rating por pista com base nas voltas registradas.
- **Gerenciador de setups**
  - Lista e filtra setups salvos pelo ACC.
  - Permite visualizar e editar parâmetros.
  - Replica setups para outro carro ou pista.
  - Ajusta pressões para a compatibilidade com o ACC 1.9.
  - Cria setups inteligentes com base no carro, pista e estilo de condução.
- **Ranking dos amigos**
  - Publica os melhores tempos em uma tabela compartilhada no Supabase.
  - Filtra por carro e pista.
  - Mantém o histórico de voltas e mostra o melhor tempo de cada piloto.
- **Notificações**
  - Usa um webhook do Discord para avisar sobre início e encerramento do servidor e novos recordes.

## Requisitos

- Windows
- Python 3.10 ou superior
- Assetto Corsa Competizione
- Servidor dedicado do ACC, caso queira usar a aba de servidor
- MoTeC i2 Pro e arquivos de telemetria, caso queira usar a análise de telemetria
- Conta no Supabase, somente para o ranking compartilhado

## Instalação

Abra o PowerShell na pasta do projeto:

```powershell
cd "C:\caminho\para\ACC Manager 4.0"
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação do ambiente virtual, execute apenas nesta janela:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

## Configuração do `.env`

Na primeira execução, o programa cria um `.env` automaticamente com caminhos padrão. Edite-o para apontar para as pastas do seu computador:

```dotenv
ACC_SERVER_PATH=C:\Steam\steamapps\common\Assetto Corsa Competizione Dedicated Server\server
ACC_MOTEC_PATH=C:\Users\SEU_USUARIO\Documents\Assetto Corsa Competizione\MoTeC
ACC_SETUPS_PATH=C:\Users\SEU_USUARIO\Documents\Assetto Corsa Competizione\Setups
SUPABASE_URL=
SUPABASE_KEY=
DISCORD_WEBHOOK_URL=
```

Se os documentos do ACC estiverem no OneDrive, o aplicativo tenta detectar automaticamente os caminhos de MoTeC e de setups. A configuração manual no `.env` sempre pode ser usada.

> O arquivo `.env` contém credenciais e está incluído no `.gitignore`. Nunca publique esse arquivo nem a chave `SUPABASE_KEY` em um repositório.

## Inicialização

Com o ambiente virtual ativado:

```powershell
python main.py
```

No Windows, também é possível executar:

```powershell
.\run_acc_manager.bat
```

O aplicativo avisa na inicialização quais diretórios configurados não foram encontrados.

## Configurando o Supabase

O Supabase é usado apenas para o ranking compartilhado. O aplicativo acessa a tabela pela API REST, sem precisar hospedar um servidor próprio.

### 1. Criar o projeto

1. Acesse [supabase.com](https://supabase.com) e crie uma conta.
2. Crie um novo projeto.
3. Abra **SQL Editor** no painel do projeto.
4. Execute o SQL abaixo:

```sql
create table leaderboard (
    id bigint generated always as identity primary key,
    driver_name text not null,
    car_id text not null,
    track_id text not null,
    lap_time_seconds numeric not null,
    lap_time_formatted text not null,
    session_type text,
    track_temp text,
    ambient_temp text,
    recorded_at timestamptz default now()
);

alter table leaderboard enable row level security;

create policy "allow_insert"
on leaderboard
for insert
to anon
with check (true);

create policy "allow_select"
on leaderboard
for select
to anon
using (true);
```

As políticas permitem que usuários com a chave pública `anon` leiam e insiram resultados. Não são permitidas operações públicas de edição ou exclusão, mantendo o histórico de voltas.

### 2. Copiar as credenciais da API

No painel do Supabase, acesse **Project Settings > API** e copie:

- **Project URL** para `SUPABASE_URL`;
- **anon public key** para `SUPABASE_KEY`.

Exemplo:

```dotenv
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon_publica
```

Use a chave **anon public**, nunca uma chave `service_role` no aplicativo ou em um arquivo distribuído aos amigos. Todos os usuários devem configurar a mesma URL e a mesma chave anon para consultar o mesmo ranking.

### 3. Verificar a conexão

1. Salve o `.env`.
2. Reinicie o ACC Manager.
3. Abra a aba **Ranking dos Amigos**.
4. O status deve aparecer como conectado.

Se a URL ou a chave estiverem vazias, o restante do aplicativo continua funcionando, mas o ranking compartilhado fica desativado.

## Configurando o Discord (opcional)

1. No Discord, abra as configurações do canal desejado.
2. Crie um **Webhook**.
3. Copie a URL e coloque no `.env`:

```dotenv
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

Não é necessário criar um bot. Se o valor ficar vazio, as funcionalidades locais continuam disponíveis sem notificações.

## Estrutura do projeto

```text
.
├── main.py
├── requirements.txt
├── run_acc_manager.bat
├── assets/
└── core/
    ├── data/
    │   ├── cars.json
    │   └── tracks.json
    ├── vendor/
    │   └── ldparser.py
    ├── discord_notifier.py
    ├── leaderboard_client.py
    ├── ld_telemetry_parser.py
    ├── motec_parser.py
    ├── server_controller.py
    ├── setup_creator.py
    └── setup_manager.py
```

Para adicionar carros ou pistas, edite os arquivos `core/data/cars.json` e `core/data/tracks.json`.

## Solução de problemas

- **PyQt6 não instalado:** confirme que o ambiente virtual está ativado e execute `pip install -r requirements.txt`.
- **Servidor não encontrado:** ajuste `ACC_SERVER_PATH` para a pasta que contém `accServer.exe`.
- **Telemetria ou setups não aparecem:** confira `ACC_MOTEC_PATH` e `ACC_SETUPS_PATH`.
- **Ranking desconectado:** confira `SUPABASE_URL`, `SUPABASE_KEY`, a tabela `leaderboard` e as políticas RLS.
- **Notificações não chegam:** valide se o webhook do Discord está ativo e se `DISCORD_WEBHOOK_URL` foi preenchido corretamente.

## Licença

Este projeto inclui o parser de telemetria localizado em `core/vendor/ldparser.py` e sua licença correspondente em `core/vendor/LICENSE-ldparser.txt`. Consulte esse arquivo antes de redistribuir o projeto.
