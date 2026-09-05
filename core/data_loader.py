"""
Carregador central da base de Carros e Pistas.

Fonte unica de verdade: core/data/cars.json e core/data/tracks.json.
Todo o app (main.py, motec_parser.py, setup_creator.py) le destes dois
arquivos, entao ao sair uma atualizacao do ACC com carro/pista novo, o
usuario so precisa adicionar uma entrada no JSON correspondente - nenhum
arquivo .py precisa ser tocado.

Os dados sao carregados uma unica vez (cache em memoria) e recarregados
automaticamente se o arquivo JSON for alterado depois do processo iniciar.
"""

import json
import os
import sys

# Quando empacotado com PyInstaller (modo --onedir, recomendado pra este app),
# sys.executable aponta pro .exe real, e core/data fica na mesma pasta dele.
# Rodando como script normal, sobe um nivel a partir deste arquivo (core/) ate
# a raiz do projeto. Isso e o que garante que core/data/*.json continua
# gravavel (o calibrador de pistas ESCREVE nesses arquivos) mesmo no .exe -
# por isso o build recomendado e --onedir, nao --onefile (ver build_exe.bat).
if getattr(sys, "frozen", False):
    _APP_ROOT = os.path.dirname(os.path.abspath(sys.executable))
else:
    _APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_DATA_DIR = os.path.join(_APP_ROOT, "core", "data")
_CARS_PATH = os.path.join(_DATA_DIR, "cars.json")
_TRACKS_PATH = os.path.join(_DATA_DIR, "tracks.json")

_DEFAULT_CAR = {"display_name": None, "class": "GT3", "temperament": 3}
_DEFAULT_TRACK = {"display_name": None, "downforce": 3, "bumpiness": 3, "brake_stress": 3, "avg_speed": 3}

_cache = {"cars": None, "cars_mtime": None, "tracks": None, "tracks_mtime": None}


def _load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _cars() -> dict:
    try:
        mtime = os.path.getmtime(_CARS_PATH)
    except OSError:
        mtime = None
    if _cache["cars"] is None or _cache["cars_mtime"] != mtime:
        _cache["cars"] = _load_json(_CARS_PATH).get("cars", {})
        _cache["cars_mtime"] = mtime
    return _cache["cars"]


def _tracks() -> dict:
    try:
        mtime = os.path.getmtime(_TRACKS_PATH)
    except OSError:
        mtime = None
    if _cache["tracks"] is None or _cache["tracks_mtime"] != mtime:
        _cache["tracks"] = _load_json(_TRACKS_PATH).get("tracks", {})
        _cache["tracks_mtime"] = mtime
    return _cache["tracks"]


# ---------------------------------------------------------------------------
# API publica
# ---------------------------------------------------------------------------

def all_cars() -> dict:
    """Retorna {car_id: {display_name, class, temperament}} de todos os carros conhecidos."""
    return _cars()


def all_tracks() -> dict:
    """Retorna {track_id: {display_name, downforce, bumpiness, brake_stress, avg_speed}}."""
    return _tracks()


def get_car(car_id: str) -> dict:
    return _cars().get((car_id or "").lower(), _DEFAULT_CAR)


def get_track(track_id: str) -> dict:
    return _tracks().get((track_id or "").lower(), _DEFAULT_TRACK)


def car_display_name(car_id: str) -> str:
    entry = get_car(car_id)
    return entry.get("display_name") or (car_id or "Carro Desconhecido").replace("_", " ").title()


def track_display_name(track_id: str) -> str:
    entry = get_track(track_id)
    return entry.get("display_name") or (track_id or "Pista Desconhecida").replace("_", " ").title()


def car_temperament(car_id: str) -> int:
    return get_car(car_id).get("temperament", 3)


def track_profile(track_id: str) -> dict:
    entry = get_track(track_id)
    return {
        "downforce": entry.get("downforce", 3),
        "bumpiness": entry.get("bumpiness", 3),
        "brake_stress": entry.get("brake_stress", 3),
        "avg_speed": entry.get("avg_speed", 3),
    }


def track_length_km(track_id: str):
    """Retorna o comprimento real da pista em km (dado objetivo, nao muda
    com patch) - usado pelo calibrador para converter tempo de volta em
    velocidade media real. None se a pista nao estiver cadastrada."""
    return get_track(track_id).get("length_km")


def normalize(value: int) -> float:
    """Converte uma nota 1-5 em -1.0 .. +1.0 (3 = neutro). Usado pelo Criador de Setups."""
    return (value - 3) / 2.0
