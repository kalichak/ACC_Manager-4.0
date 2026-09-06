# Telemetria

## Fontes

`core/motec_parser.py` lê arquivos `.ldx` na pasta `ACC_MOTEC_PATH`. O nome do
arquivo fornece tokens de pista, carro e piloto; o XML fornece tempo mais
rápido, voltas, sessão e temperaturas.

`core/ld_telemetry_parser.py` faz a análise avançada do `.ld` irmão. Usa
marcadores `BCN` do `.ldx` para separar voltas e extrai, quando disponíveis,
velocidade, acelerador, freio, G-LAT/G-LON, temperaturas e RPM.

## Fluxo na UI

`ui/telemetry_tab.py` lista as melhores sessões, filtra por carro/pista,
mostra preview da pista e abre a análise `.ld`. Sessões podem ser removidas;
a remoção apaga o `.ldx` e o `.ld` correspondente.

Tempos abaixo de 70 segundos são tratados pela UI como glitch para cálculo de
score. Esse limite é comportamento atual, não uma regra configurável.

## Calibração

`core/track_profile_calibrator.py` calcula `avg_speed` pela distância em
`tracks.json` e tempo de volta. Para `brake_stress`, usa eventos de frenagem
forte da análise `.ld`. A aplicação pode gravar sugestões em
`core/data/tracks.json`; por isso o build usa `--onedir`.

## Contribuindo

Use cópias de `.ld`/`.ldx` sem dados pessoais. Não envie sessões reais ao
repositório. O parser vendorizado tem licença GPLv3; consulte
[LICENSING.md](LICENSING.md).
