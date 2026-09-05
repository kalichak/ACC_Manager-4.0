"""
Configuracao central do ACC Manager
======================================

Tudo que precisa existir ANTES da interface grafica: carregamento do .env,
caminhos de pasta, importacao dos modulos de core/ (com mensagem de erro
amigavel se algo faltar) e a base de carros/pistas (vinda de
core/data_loader.py - unica fonte de verdade, nao duplique aqui).

Qualquer arquivo em ui/ que precise de BASE_DIR, TRACKS_DATABASE,
CAR_NAMES_MAPPING, SERVER_PATH etc. importa deste modulo:
    from config import TRACKS_DATABASE, CAR_NAMES_MAPPING
"""

import json
import os
import sys
import traceback

if getattr(sys, "frozen", False):
    # Local onde ficam as pastas empacotadas (assets, core/data) dentro do _internal
    BASE_DIR = sys._MEIPASS
    # Local onde o executavel esta rodando (para salvar .env e settings visíveis)
    USER_DATA_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    USER_DATA_DIR = BASE_DIR

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

UI_SETTINGS_FILE = os.path.join(USER_DATA_DIR, "ui_settings.json")
ENV_FILE = os.path.join(USER_DATA_DIR, ".env")

def load_or_create_env():
    user_home = os.path.expanduser("~")
    default_env = {
        "ACC_SERVER_PATH": r"C:\Steam\steamapps\common\Assetto Corsa Competizione Dedicated Server\server",
        "ACC_MOTEC_PATH": os.path.join(user_home, "Documents", "Assetto Corsa Competizione", "MoTeC"),
        "ACC_SETUPS_PATH": os.path.join(user_home, "Documents", "Assetto Corsa Competizione", "Setups"),
        "SUPABASE_URL": "",
        "SUPABASE_KEY": "",
        "DISCORD_WEBHOOK_URL": ""
    }

    onedrive_docs = os.path.join(user_home, "OneDrive", "Documentos", "Assetto Corsa Competizione")
    if os.path.exists(onedrive_docs):
        default_env["ACC_MOTEC_PATH"] = os.path.join(onedrive_docs, "MoTeC")
        default_env["ACC_SETUPS_PATH"] = os.path.join(onedrive_docs, "Setups")

    if not os.path.exists(ENV_FILE):
        try:
            with open(ENV_FILE, "w", encoding="utf-8") as f:
                f.write("# ACC MANAGER - CONFIGURACOES DE DIRETORIO\n")
                for key, value in default_env.items():
                    f.write(f"{key}={value}\n")
        except Exception:
            pass
        return default_env

    env_data = {}
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env_data[key.strip()] = val.strip()
    except Exception:
        return default_env

    for key in default_env:
        if key not in env_data:
            env_data[key] = default_env[key]

    return env_data

def save_env(values: dict):
    """Escreve um dict {CHAVE: valor} de volta no .env, preservando as
    chaves que ja existiam mas nao foram passadas. Usado pela tela de
    Configuracoes (ui/settings_dialog.py)."""
    current = load_or_create_env()
    current.update(values)
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write("# ACC MANAGER - CONFIGURACOES DE DIRETORIO\n")
        for key, value in current.items():
            f.write(f"{key}={value}\n")
    return current


def reload_env():
    """Re-le o .env do disco e atualiza as constantes deste modulo em
    tempo real (sem precisar reiniciar o app). Retorna o dict novo."""
    global ENV_VARS, SERVER_PATH, DEFAULT_MOTEC_PATH, DEFAULT_SETUPS_PATH
    global SUPABASE_URL, SUPABASE_KEY, DISCORD_WEBHOOK_URL
    ENV_VARS = load_or_create_env()
    SERVER_PATH = ENV_VARS["ACC_SERVER_PATH"]
    DEFAULT_MOTEC_PATH = ENV_VARS["ACC_MOTEC_PATH"]
    DEFAULT_SETUPS_PATH = ENV_VARS["ACC_SETUPS_PATH"]
    SUPABASE_URL = ENV_VARS.get("SUPABASE_URL", "")
    SUPABASE_KEY = ENV_VARS.get("SUPABASE_KEY", "")
    DISCORD_WEBHOOK_URL = ENV_VARS.get("DISCORD_WEBHOOK_URL", "")
    return ENV_VARS


ENV_VARS = load_or_create_env()
SERVER_PATH = ENV_VARS["ACC_SERVER_PATH"]
DEFAULT_MOTEC_PATH = ENV_VARS["ACC_MOTEC_PATH"]
DEFAULT_SETUPS_PATH = ENV_VARS["ACC_SETUPS_PATH"]
SUPABASE_URL = ENV_VARS.get("SUPABASE_URL", "")
SUPABASE_KEY = ENV_VARS.get("SUPABASE_KEY", "")
DISCORD_WEBHOOK_URL = ENV_VARS.get("DISCORD_WEBHOOK_URL", "")

try:
    import PyQt6.QtWidgets  # noqa: F401 - so para falhar cedo com mensagem amigavel
except ImportError:
    print("\n[ERRO CRITICO] PyQt6 nao esta instalado no ambiente atual!")
    print("Execute no terminal: pip install -r requirements.txt\n")
    sys.exit(1)

try:
    from core.server_controller import ServerController
    from core.motec_parser import MotecParser
    from core.setup_manager import SetupManager
    from core.setup_creator import SetupCreator
    from core.leaderboard_client import LeaderboardClient
    from core.discord_notifier import DiscordNotifier
    from core import data_loader
    from core import track_profile_calibrator
    from core import ld_telemetry_parser
except ImportError as e:
    print(f"\n[ERRO DE IMPORTACAO] Nao foi possivel carregar a pasta 'core': {e}")
    sys.exit(1)

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff"}

# Fonte unica de verdade: core/data/tracks.json e core/data/cars.json.
TRACKS_DATABASE = {tid: info.get("display_name", tid) for tid, info in data_loader.all_tracks().items()}
CAR_NAMES_MAPPING = {cid: info.get("display_name", cid) for cid, info in data_loader.all_cars().items()}
