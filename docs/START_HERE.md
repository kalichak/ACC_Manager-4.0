# Comece aqui

Este guia é o caminho mais curto para entender o ACC Manager e fazer a
primeira contribuição.

## 1. Prepare o ambiente

Use Windows 10+, Python 3.10+ e uma virtualenv. Instale
`requirements.txt` e execute `python main.py`. O programa é uma GUI PyQt6;
não é necessário um servidor local para iniciar a janela.

## 2. Leia nesta ordem

1. `README.md` — instalação e recursos visíveis ao usuário.
2. `main.py` e `config.py` — entrada da aplicação e inicialização.
3. `ui/main_window.py` — composição das abas e serviços.
4. `ui/i18n.py` — traduções.
5. A documentação do módulo que você pretende alterar.
6. `core/data/*.json` — base de carros e pistas.

## 3. Faça uma mudança pequena

Escolha um item de [GOOD_FIRST_ISSUES.md](GOOD_FIRST_ISSUES.md), crie uma
branch e preserve a separação entre UI (`ui/`) e serviços (`core/`). Para
novos textos de interface, adicione as chaves nos três idiomas em
`ui/i18n.py`.

## 4. Valide

Execute a compilação Python e `pytest`. Para mudanças de empacotamento, rode
`build_exe.bat` em Windows. Não use credenciais reais em exemplos, screenshots
ou commits.

## 5. Envie

Abra um Pull Request usando o template. Explique o comportamento anterior,
o novo comportamento e como testar. Para decisões arquiteturais duradouras,
adicione um ADR em `docs/decisions/`.
