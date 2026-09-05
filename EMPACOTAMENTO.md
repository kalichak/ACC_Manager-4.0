# Empacotando o ACC Manager como .exe

## Passo a passo

1. Copie a pasta inteira do projeto pra sua maquina Windows (o build tem
   que rodar no Windows - nao da pra gerar um .exe Windows a partir de
   Linux/Mac).
2. De dois cliques em `build_exe.bat` (ou rode `build_exe.bat` no
   PowerShell/CMD dentro da pasta do projeto).
3. Espere - a primeira vez demora mais porque instala tudo do zero
   (PyQt6, numpy etc. dentro de uma venv nova).
4. Pronto: o app fica em `dist\ACCManager\ACCManager.exe`.

## Distribuindo pros seus amigos

Zipe e mande a pasta **inteira** `dist\ACCManager`, nao so o `.exe`. Ela
contem:
- `ACCManager.exe`
- As bibliotecas Python empacotadas (PyQt6, numpy etc.)
- `core\data\cars.json` e `tracks.json` (a base de carros/pistas)
- `assets\` (imagens de previa das pistas)

Cada amigo, na primeira vez que abrir o `.exe`, vai ver o aviso de
diretorios nao encontrados (normal - cada PC tem os jogos em lugar
diferente) e pode clicar em **⚙ Configuracoes** pra apontar as pastas
certas, sem precisar mexer em nenhum arquivo de texto.

## Por que `--onedir` e nao `--onefile`

O PyInstaller pode gerar um unico `.exe` (`--onefile`) ou uma pasta com o
`.exe` + arquivos soltos (`--onedir`). Escolhi `--onedir` de proposito:

- O Criador de Setups Inteligente e o calibrador de pistas **escrevem**
  em `core/data/tracks.json` (ajustando notas de `avg_speed` e
  `brake_stress` com base na sua telemetria real).
- Num `--onefile`, esses arquivos ficam dentro do `.exe` e sao extraidos
  pra uma pasta temporaria toda vez que o programa abre - qualquer
  gravacao nessa pasta temporaria e apagada quando o programa fecha.
- Com `--onedir`, `core/data/tracks.json` fica de verdade ao lado do
  `.exe`, entao as calibracoes persistem entre uma sessao e outra.

## Se o build falhar

Troque `--windowed` por `--console` no `build_exe.bat` (ou rode o comando
`pyinstaller` manualmente) pra ver a mensagem de erro completa numa janela
de terminal - com `--windowed` o programa nao tem console pra mostrar
erros de inicializacao.

## Atualizando depois de mudar o codigo

Sempre que voce editar `main.py`/`core/`/`ui/`, rode `build_exe.bat` de
novo - ele limpa `build\` e `dist\` antigos automaticamente antes de
gerar a versao nova.
