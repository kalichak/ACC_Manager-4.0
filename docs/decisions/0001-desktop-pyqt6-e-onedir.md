# ADR 0001: Aplicação desktop PyQt6 empacotada como onedir

- Status: aceito
- Data: 2026-09-06

## Contexto

O ACC Manager precisa oferecer uma interface Windows para controlar arquivos
locais do ACC, ler telemetria e editar setups. O criador inteligente e o
calibrador também gravam dados em `core/data/*.json`.

## Decisão

Usar PyQt6 para a interface, organizar a janela em mixins por aba e distribuir
o executável com PyInstaller no modo `--onedir`.

## Consequências

- `main.py` permanece pequeno e a UI é dividida por responsabilidade.
- `core/` pode ser exercitado sem conhecer os widgets.
- `--onedir` mantém `core/data` e `assets` como arquivos ao lado do executável,
  permitindo que calibrações persistam.
- A distribuição exige enviar a pasta inteira, não apenas o `.exe`.
- Uma futura migração para widgets independentes é possível, mas não é
  necessária para o comportamento atual.
