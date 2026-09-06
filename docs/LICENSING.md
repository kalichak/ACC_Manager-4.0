# Licenciamento

## Projeto

O código do ACC Manager é distribuído sob a [MIT License](../LICENSE). A MIT
permite uso, modificação e redistribuição, inclusive comercial, mantendo o
aviso de copyright e o texto da licença.

## Componente GPLv3

`core/vendor/ldparser.py` é um componente vendorizado sob GNU GPLv3. O texto
completo está em `core/vendor/LICENSE-ldparser.txt`. A licença desse arquivo
não é substituída pela MIT do projeto principal.

Ao modificar ou redistribuir o componente vendorizado, preserve seus avisos,
ofereça o código-fonte correspondente conforme a GPLv3 e não apresente o
componente como se fosse MIT. O build inclui a licença em `core/vendor`.

Esta documentação não é aconselhamento jurídico. Questões sobre combinação,
distribuição de executáveis ou alterações substanciais devem ser revisadas por
alguém com competência jurídica. Não altere nenhuma licença sem autorização
do mantenedor.

## Outras dependências

`requirements.txt` declara PyQt6, psutil, requests, numpy e pytest. As
licenças e avisos dessas dependências devem ser verificados nas versões
instaladas antes de uma redistribuição comercial; o repositório não mantém
cópias completas desses textos.
