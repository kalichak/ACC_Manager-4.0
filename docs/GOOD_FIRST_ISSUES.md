# Oportunidades de contribuição

As sugestões abaixo são baseadas no código atual. Elas são propostas de
trabalho; não são Issues GitHub abertas automaticamente.

| Categoria | Dificuldade | Sugestão |
|---|---|---|
| good first issue | easy | Adicionar teste unitário para `data_loader.normalize`. |
| good first issue | easy | Documentar todas as chaves de `core/data/cars.json`. |
| good first issue | easy | Documentar todas as chaves de `core/data/tracks.json`. |
| good first issue | easy | Adicionar validação de formato para `APP_LANGUAGE`. |
| documentation | easy | Traduzir mensagens restantes que ainda usam strings diretas na UI. |
| documentation | easy | Adicionar exemplos de troubleshooting para caminhos OneDrive. |
| documentation | medium | Documentar o schema efetivo dos três JSON escritos pelo servidor. |
| help wanted | medium | Criar fixtures pequenos de `.ldx` para testar o parser sem dados pessoais. |
| help wanted | medium | Criar testes de `MotecParser` com XML mínimo e nomes de arquivo variados. |
| help wanted | medium | Criar testes de `SetupManager` usando diretório temporário. |
| bug | medium | Tratar arquivos `.ldx` corrompidos com feedback específico em vez de apenas ignorá-los. |
| bug | medium | Revisar a descoberta de caminhos quando o Windows usa nomes diferentes para OneDrive. |
| bug | hard | Tornar a remoção de processos do servidor mais restrita ao servidor configurado. |
| refactor | medium | Extrair a persistência de `ui_settings.json` para um serviço testável. |
| refactor | medium | Substituir strings restantes de UI por chaves centralizadas em `ui/i18n.py`. |
| refactor | hard | Separar os mixins de abas em widgets independentes sem alterar o fluxo atual. |
| feature | medium | Adicionar importação/exportação explícita de uma configuração sem segredos. |
| feature | medium | Permitir escolher o limite de score para tempos inválidos. |
| feature | hard | Adicionar uma visualização histórica de evolução no ranking. |
| feature | hard | Adicionar suporte a mais formatos de telemetria sem remover o caminho `.ldx`. |

Antes de implementar uma sugestão, confirme o comportamento com um mantenedor
e não inclua arquivos reais do ACC, MoTeC, Supabase ou Discord.
