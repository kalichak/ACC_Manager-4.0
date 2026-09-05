"""
Calibrador de Perfis de Pista
================================

Responde a pergunta "como manter a base de pistas forte e atualizada": em vez
de confiar so em numeros digitados a mao (que podem ficar desatualizados ou
simplesmente errados), este modulo calcula o eixo `avg_speed` de cada pista
a partir dos SEUS proprios tempos de volta reais, gravados pelo MoTeC.

Como funciona:
  velocidade_media_kmh = comprimento_da_pista_km / (tempo_da_volta_h)

Isso e um dado objetivo: nao depende de opiniao, e se atualiza sozinho a
cada vez que voce roda mais voltas - inclusive quando a Kunos muda o BoP de
um carro (o que altera a velocidade media real na pista), sem voce precisar
editar nada manualmente.

Limitacao importante: isto calibra apenas `avg_speed`. Os eixos downforce,
bumpiness e brake_stress descrevem caracteristicas FISICAS da pista (formato
das curvas, estado do asfalto) que nao mudam de patch pra patch e nao dá pra
derivar de um tempo de volta sozinho - esses continuam vindo de
core/data/tracks.json editado a mao. Uma extensao futura possivel: ler os
canais binarios do MoTeC .ld (nao so o resumo .ldx que ja lemos hoje) para
contar eventos de frenagem forte e estimar brake_stress tambem.
"""

import json
import os

from core import data_loader


def compute_avg_speeds(best_laps: list) -> dict:
    """
    best_laps: saida de MotecParser.get_best_laps()
    Retorna {track_id: velocidade_media_kmh} usando a volta mais rapida
    registrada em cada pista (proxy razoavel do seu pace real ali).
    """
    speeds = {}
    for lap in best_laps:
        track_id = (lap.get("track_id") or "").lower()
        length_km = data_loader.track_length_km(track_id)
        raw_time = lap.get("raw_time")
        if not length_km or not raw_time or raw_time <= 0:
            continue
        speed_kmh = length_km / (raw_time / 3600.0)
        if track_id not in speeds or speed_kmh > speeds[track_id]:
            speeds[track_id] = speed_kmh
    return speeds


def suggest_avg_speed_ratings(best_laps: list) -> dict:
    """
    Converte as velocidades medias calculadas em notas 1-5 relativas entre
    si (a pista mais rapida do seu historico vira 5, a mais lenta vira 1).
    Retorna {track_id: {"suggested_rating", "computed_kmh", "current_rating"}}
    """
    speeds = compute_avg_speeds(best_laps)
    if not speeds:
        return {}

    values = list(speeds.values())
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0

    result = {}
    for track_id, kmh in speeds.items():
        normalized = (kmh - lo) / span  # 0..1
        rating = round(1 + normalized * 4)  # 1..5
        current = data_loader.track_profile(track_id).get("avg_speed", 3)
        result[track_id] = {
            "suggested_rating": int(rating),
            "computed_kmh": round(kmh, 1),
            "current_rating": current,
        }
    return result


def suggest_brake_stress_ratings(best_laps: list) -> dict:
    """
    Igual ao suggest_avg_speed_ratings, mas para brake_stress - usando a
    telemetria REAL do .ld (media de frenagens fortes por volta, via
    core/ld_telemetry_parser.py) em vez de so o tempo de volta.
    So funciona para sessoes que tem o .ld irmao do .ldx disponivel.
    """
    from core import ld_telemetry_parser as ltp

    per_track_events = {}
    for lap in best_laps:
        track_id = (lap.get("track_id") or "").lower()
        ldx_path = lap.get("file_path")
        if not ldx_path:
            continue
        ld_path = ltp.get_ld_path(ldx_path)
        if not os.path.exists(ld_path):
            continue
        avg_events = ltp.session_brake_events_per_lap(ld_path, ldx_path)
        if avg_events is None:
            continue
        per_track_events.setdefault(track_id, []).append(avg_events)

    if not per_track_events:
        return {}

    avg_per_track = {tid: sum(vals) / len(vals) for tid, vals in per_track_events.items()}
    values = list(avg_per_track.values())
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0

    result = {}
    for track_id, avg_events in avg_per_track.items():
        normalized = (avg_events - lo) / span
        rating = round(1 + normalized * 4)
        current = data_loader.track_profile(track_id).get("brake_stress", 3)
        result[track_id] = {
            "suggested_rating": int(rating),
            "computed_kmh": round(avg_events, 1),  # reaproveita o campo (aqui = eventos/volta)
            "current_rating": current,
        }
    return result


def apply_suggestions(suggestions: dict, min_gap: int = 1, field: str = "avg_speed") -> int:
    """
    Grava as notas sugeridas de volta em core/data/tracks.json, mas so para
    pistas onde a sugestao difere da atual em pelo menos `min_gap` pontos
    (evita reescrever o arquivo por causa de ruido de 1 unica sessao).
    `field` indica qual eixo atualizar ("avg_speed" ou "brake_stress").
    Retorna quantas entradas foram alteradas.
    """
    tracks = data_loader.all_tracks()
    changed = 0
    for track_id, info in suggestions.items():
        if track_id not in tracks:
            continue
        if abs(info["suggested_rating"] - info["current_rating"]) >= min_gap:
            tracks[track_id][field] = info["suggested_rating"]
            changed += 1

    if changed:
        with open(data_loader._TRACKS_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
        payload["tracks"] = tracks
        with open(data_loader._TRACKS_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        data_loader._cache["tracks_mtime"] = None  # forca reload no proximo acesso

    return changed
