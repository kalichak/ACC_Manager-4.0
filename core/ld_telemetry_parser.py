"""
Telemetria Avancada (.ld binario)
====================================

O motec_parser.py original so le o resumo do .ldx (tempo total da sessao,
numero de voltas). Este modulo vai mais fundo: le os canais reais gravados
pelo jogo (velocidade, freio, acelerador, temperatura de pneu/freio,
G lateral, RPM etc.) usando a biblioteca vendorizada core/vendor/ldparser.py
(ver licenca la dentro - GPL-3.0, uso privado sem restricao adicional).

Como o corte por volta funciona:
O canal LAP_BEACON dentro do .ld nem sempre vem preenchido (em sessoes sem
volta completa, por exemplo). Em vez de depender so dele, este modulo le os
marcadores de volta gravados no .ldx (<Marker ClassName="BCN" Time="..."/>),
que guardam o instante de cada passagem pela linha em MICROSSEGUNDOS desde o
inicio da gravacao. Cruzando esse instante com a frequencia de cada canal do
.ld (ex.: SPEED a 60Hz), da pra recortar exatamente os dados daquela volta.

Isso e o dado mais "real" que existe: nao e estimativa nem palpite, e a
telemetria de verdade gravada pelo proprio jogo.
"""

import os
import xml.etree.ElementTree as ET

import numpy as np

from core.vendor.ldparser import ldData

# Canais que sabemos existir nos .ld gravados pela ACC (nomes exatos no arquivo).
# Nem toda sessao tem todos - o codigo abaixo sempre confere antes de usar.
CHANNEL_SPEED = "SPEED"                # m/s
CHANNEL_THROTTLE = "THROTTLE"          # %
CHANNEL_BRAKE = "BRAKE"                # %
CHANNEL_STEER = "STEERANGLE"           # graus
CHANNEL_GLAT = "G_LAT"                 # m/s2
CHANNEL_GLON = "G_LON"                 # m/s2
CHANNEL_RPM = "RPMS"
TYRE_TEMP_CHANNELS = ["TYRE_TAIR_LF", "TYRE_TAIR_RF", "TYRE_TAIR_LR", "TYRE_TAIR_RR"]
BRAKE_TEMP_CHANNELS = ["BRAKE_TEMP_LF", "BRAKE_TEMP_RF", "BRAKE_TEMP_LR", "BRAKE_TEMP_RR"]

# Acima desse % de freio, consideramos "frenagem forte" para fins de
# estatistica de brake_stress (ajustavel).
HARD_BRAKE_THRESHOLD_PCT = 80.0


def get_ld_path(ldx_path: str) -> str:
    base, _ext = os.path.splitext(ldx_path)
    return base + ".ld"


def parse_lap_markers(ldx_path: str) -> list:
    """
    Le os marcadores de volta do .ldx (linha de chegada/beacon).
    Retorna lista de dicts: [{"lap": 0, "start_s": 0.0, "end_s": 103.099, "lap_time_s": 103.099}, ...]
    Os tempos sao em segundos desde o inicio da gravacao (Time no XML esta em microssegundos).
    """
    if not os.path.exists(ldx_path):
        return []
    try:
        root = ET.parse(ldx_path).getroot()
    except Exception:
        return []

    times_us = []
    for marker in root.iter("Marker"):
        if marker.get("ClassName") != "BCN":
            continue
        t = marker.get("Time")
        if t is None:
            continue
        try:
            times_us.append(float(t))
        except ValueError:
            continue

    times_us.sort()
    if len(times_us) < 2:
        return []

    laps = []
    for i in range(1, len(times_us)):
        start_s = times_us[i - 1] / 1_000_000.0
        end_s = times_us[i] / 1_000_000.0
        laps.append({
            "lap": i,
            "start_s": start_s,
            "end_s": end_s,
            "lap_time_s": round(end_s - start_s, 3),
        })
    return laps


def _channel_slice(ld: ldData, channel_name: str, start_s: float, end_s: float):
    """Retorna a fatia de dados de um canal entre dois instantes (em segundos),
    usando a frequencia de amostragem propria daquele canal. None se o canal nao existir."""
    try:
        chan = ld[channel_name]
    except Exception:
        return None
    freq = chan.freq or 1
    data = chan.data
    i0 = max(0, int(start_s * freq))
    i1 = min(len(data), int(end_s * freq))
    if i1 <= i0:
        return None
    return data[i0:i1]


def analyze_session(ld_path: str, ldx_path: str = None) -> dict:
    """
    Analisa um arquivo .ld (+ .ldx irmao para os cortes de volta) e retorna
    metricas reais por volta. Se o .ldx nao tiver marcadores (sessao sem
    volta completa), retorna metricas da sessao inteira em vez de por volta.
    """
    if not os.path.exists(ld_path):
        raise FileNotFoundError(f"Arquivo .ld nao encontrado: {ld_path}")

    ld = ldData.fromfile(ld_path)
    available = set(iter(ld))

    if ldx_path is None:
        ldx_path = os.path.splitext(ld_path)[0] + ".ldx"
    laps = parse_lap_markers(ldx_path)

    if not laps:
        total_speed = ld[CHANNEL_SPEED].data if CHANNEL_SPEED in available else np.array([])
        duration_s = len(total_speed) / (ld[CHANNEL_SPEED].freq or 1) if len(total_speed) else 0
        laps = [{"lap": 0, "start_s": 0.0, "end_s": duration_s, "lap_time_s": round(duration_s, 3)}]

    results = []
    for lap in laps:
        entry = {"lap": lap["lap"], "lap_time_s": lap["lap_time_s"]}

        speed = _channel_slice(ld, CHANNEL_SPEED, lap["start_s"], lap["end_s"]) if CHANNEL_SPEED in available else None
        if speed is not None and len(speed):
            entry["max_speed_kmh"] = round(float(speed.max()) * 3.6, 1)
            entry["avg_speed_kmh"] = round(float(speed.mean()) * 3.6, 1)

        throttle = _channel_slice(ld, CHANNEL_THROTTLE, lap["start_s"], lap["end_s"]) if CHANNEL_THROTTLE in available else None
        if throttle is not None and len(throttle):
            entry["full_throttle_pct_of_lap"] = round(float((throttle >= 99).mean()) * 100, 1)

        brake = _channel_slice(ld, CHANNEL_BRAKE, lap["start_s"], lap["end_s"]) if CHANNEL_BRAKE in available else None
        if brake is not None and len(brake):
            # conta "eventos" de frenagem forte (transicoes que cruzam o limiar pra cima)
            above = brake >= HARD_BRAKE_THRESHOLD_PCT
            crossings = int(np.sum(np.diff(above.astype(int)) == 1))
            entry["hard_brake_events"] = crossings
            entry["max_brake_pct"] = round(float(brake.max()), 1)

        glat = _channel_slice(ld, CHANNEL_GLAT, lap["start_s"], lap["end_s"]) if CHANNEL_GLAT in available else None
        if glat is not None and len(glat):
            # O canal G_LAT do ACC vem rotulado "m/s2" no cabecalho do .ld, mas os
            # valores batem com g diretamente (confirmado comparando o p1/p99 do
            # canal com forcas laterais reais de GT3, tipicamente 1.5-2.0g).
            # Usamos o percentil 99 (nao o maximo absoluto) porque picos de zebra/
            # impacto geram valores isolados fisicamente implausiveis (>4g) que nao
            # representam a curva em si.
            entry["lat_g_p99"] = round(float(np.percentile(np.abs(glat), 99)), 2)

        glon = _channel_slice(ld, CHANNEL_GLON, lap["start_s"], lap["end_s"]) if CHANNEL_GLON in available else None
        if glon is not None and len(glon):
            braking = glon[glon < 0]
            entry["brake_g_p99"] = round(float(np.percentile(np.abs(braking), 99)), 2) if len(braking) else 0.0

        tyre_temps = []
        for ch in TYRE_TEMP_CHANNELS:
            seg = _channel_slice(ld, ch, lap["start_s"], lap["end_s"]) if ch in available else None
            if seg is not None and len(seg):
                tyre_temps.append(float(seg.mean()))
        if tyre_temps:
            entry["avg_tyre_temp_c"] = round(sum(tyre_temps) / len(tyre_temps), 1)

        brake_temps = []
        for ch in BRAKE_TEMP_CHANNELS:
            seg = _channel_slice(ld, ch, lap["start_s"], lap["end_s"]) if ch in available else None
            if seg is not None and len(seg):
                brake_temps.append(float(seg.mean()))
        if brake_temps:
            entry["avg_brake_temp_c"] = round(sum(brake_temps) / len(brake_temps), 1)

        results.append(entry)

    return {
        "channels_available": sorted(available),
        "laps": results,
    }


def session_brake_events_per_lap(ld_path: str, ldx_path: str = None) -> float:
    """Media de eventos de frenagem forte por volta - usado pelo calibrador
    de pistas para estimar brake_stress a partir de dados reais."""
    try:
        analysis = analyze_session(ld_path, ldx_path)
    except Exception:
        return None
    laps = [l for l in analysis["laps"] if "hard_brake_events" in l]
    if not laps:
        return None
    return sum(l["hard_brake_events"] for l in laps) / len(laps)
