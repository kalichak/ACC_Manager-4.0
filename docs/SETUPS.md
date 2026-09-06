# Setups

## Estrutura dos dados

`core/setup_manager.py` percorre `ACC_SETUPS_PATH` no formato
`carro\pista\arquivo.json`. A UI de `ui/setups_tab.py` lista, filtra, edita,
salva, remove, clona e replica esses arquivos.

## Recursos existentes

- presets Qualy, Corrida e Chuva;
- ajuste opcional de pressão para ACC 1.9 ao replicar;
- Criador de Setup Inteligente baseado em setup válido, perfil de carro,
  perfil de pista, agressividade e condição;
- calibração de perfis da pista com dados MoTeC;
- análise exibida pelo Engenheiro de Pista Virtual.

O criador não gera JSON do zero: parte de um setup exportado pelo ACC para
respeitar faixas específicas de cada carro.

## Alterações seguras

Preserve a estrutura esperada pelo ACC e faça backup de setups antes de testar.
Não committe setups pessoais. Ao adicionar um parâmetro, trate arquivos
antigos que não possuam a chave e mantenha o comportamento de cópia profunda
usado nos presets.
