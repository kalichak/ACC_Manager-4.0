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

# Modulos que o app conhece e a combinacao usada quando o usuario nunca
# mexeu na tela de Configuracoes (todos ligados = comportamento atual).
AVAILABLE_MODULES = ["server", "telemetry", "setups", "leaderboard"]
DEFAULT_ENABLED_MODULES = ",".join(AVAILABLE_MODULES)
DEFAULT_LANGUAGE = "en"
DEFAULT_THEME = "light"

UI_SETTINGS_FILE = os.path.join(USER_DATA_DIR, "ui_settings.json")
ENV_FILE = os.path.join(USER_DATA_DIR, ".env")

def _parse_enabled_modules(raw):
    """Le a string 'server,telemetry,...' do .env e devolve so os modulos
    que o app reconhece.

    - raw is None (chave ENABLED_MODULES nem existe no .env, ex.: .env
      criado por uma versao antiga do app antes desta feature) -> assume
      todos habilitados, que era o comportamento antigo.
    - raw == "" (usuario desmarcou TODAS as caixinhas na tela de
      Configuracoes e salvou de proposito) -> retorna lista vazia mesmo.
      A janela principal sabe lidar com isso mostrando uma aba de aviso;
      o botao de Configuracoes continua sempre visivel no canto, entao o
      usuario nunca fica "trancado para fora" das proprias configuracoes.
    - texto invalido/corrompido -> ignora entradas desconhecidas; se
      sobrar nada valido, cai no mesmo caso de lista vazia acima (nunca
      trava o app, so mostra o aviso).
    """
    if raw is None:
        return list(AVAILABLE_MODULES)
    return [m.strip() for m in raw.split(",") if m.strip() in AVAILABLE_MODULES]

def _resolve_documents_folder() -> str:
    """Descobre a pasta Documentos real do usuario.

    No Windows, primeiro le a chave "Personal" do registro (User Shell
    Folders) - ela ja aponta pro lugar certo mesmo se o OneDrive
    redirecionou a pasta Documentos, sem precisar adivinhar nome de pasta
    por idioma. Se o registro nao ajudar (Linux/Mac, erro de leitura ou
    caminho que nao existe mais), cai para uma busca manual cobrindo
    OneDrive (via variavel de ambiente OneDrive/OneDriveConsumer) e a
    pasta local, testando os nomes "Documents"/"Documentos"/"Dokumente".
    """
    user_home = os.path.expanduser("~")

    if os.name == "nt":
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                value, _ = winreg.QueryValueEx(key, "Personal")
                resolved = os.path.expandvars(value)
                if os.path.exists(resolved):
                    return resolved
        except OSError:
            pass

    onedrive_root = (
        os.environ.get("OneDrive")
        or os.environ.get("OneDriveConsumer")
        or os.path.join(user_home, "OneDrive")
    )
    for docs_name in ("Documents", "Documentos", "Dokumente"):
        onedrive_docs = os.path.join(onedrive_root, docs_name)
        if os.path.exists(onedrive_docs):
            return onedrive_docs

    for docs_name in ("Documents", "Documentos", "Dokumente"):
        local_docs = os.path.join(user_home, docs_name)
        if os.path.exists(local_docs):
            return local_docs

    return os.path.join(user_home, "Documents")


def _steam_library_paths() -> list:
    """Lista as pastas raiz de cada biblioteca Steam encontrada (onde
    moram as pastas steamapps/common), combinando a instalacao principal
    (lida do registro quando possivel) com as bibliotecas extras
    registradas em steamapps/libraryfolders.vdf de cada instalacao
    encontrada. Cobre o caso comum de o jogo estar instalado em outro
    disco que nao o disco do Windows."""
    steam_roots = []

    if os.name == "nt":
        try:
            import winreg
            for hive, key_path in (
                (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
            ):
                try:
                    with winreg.OpenKey(hive, key_path) as key:
                        value, _ = winreg.QueryValueEx(key, "InstallPath")
                        steam_roots.append(value)
                except OSError:
                    continue
        except ImportError:
            pass

    for drive in ("C:\\", "D:\\", "E:\\", "F:\\"):
        for candidate in (os.path.join(drive, "Steam"), os.path.join(drive, "Program Files (x86)", "Steam")):
            steam_roots.append(candidate)

    libraries = []
    seen = set()
    for root in steam_roots:
        if not root or root in seen or not os.path.exists(root):
            continue
        seen.add(root)
        libraries.append(root)

        vdf_path = os.path.join(root, "steamapps", "libraryfolders.vdf")
        if not os.path.exists(vdf_path):
            continue
        try:
            with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue
        for line in content.splitlines():
            line = line.strip()
            if not line.startswith('"path"'):
                continue
            parts = line.split('"')
            if len(parts) >= 4:
                lib_path = parts[3].replace("\\\\", "\\")
                if lib_path and lib_path not in seen and os.path.exists(lib_path):
                    seen.add(lib_path)
                    libraries.append(lib_path)

    return libraries


def find_acc_server_path():
    """Procura a pasta 'server' do Dedicated Server do ACC em cada
    biblioteca Steam encontrada (disco padrao e discos extras). Devolve o
    caminho se achar accServer.exe dentro dela, senao None."""
    for library in _steam_library_paths():
        candidate = os.path.join(
            library, "steamapps", "common",
            "Assetto Corsa Competizione Dedicated Server", "server",
        )
        if os.path.exists(os.path.join(candidate, "accServer.exe")):
            return candidate
    return None


def find_acc_motec_setups_paths():
    """Localiza as pastas MoTeC e Setups dentro de 'Assetto Corsa
    Competizione', usando a pasta Documentos real resolvida por
    _resolve_documents_folder (ja cobre OneDrive e idioma do Windows).
    Devolve uma tupla (motec_path, setups_path); cada item fica None se a
    respectiva pasta nao existir."""
    acc_docs = os.path.join(_resolve_documents_folder(), "Assetto Corsa Competizione")
    motec_path = os.path.join(acc_docs, "MoTeC")
    setups_path = os.path.join(acc_docs, "Setups")
    return (
        motec_path if os.path.exists(motec_path) else None,
        setups_path if os.path.exists(setups_path) else None,
    )


def auto_detect_acc_paths() -> dict:
    """Roda a deteccao automatica completa usada pelo botao
    'Auto-detectar' da tela de Configuracoes: Steam para o servidor
    dedicado e Documentos/OneDrive para MoTeC e Setups. Devolve um dict
    somente com as chaves realmente encontradas - quem chama decide o
    que fazer com o que faltou."""
    found = {}

    server_path = find_acc_server_path()
    if server_path:
        found["ACC_SERVER_PATH"] = server_path

    motec_path, setups_path = find_acc_motec_setups_paths()
    if motec_path:
        found["ACC_MOTEC_PATH"] = motec_path
    if setups_path:
        found["ACC_SETUPS_PATH"] = setups_path

    return found


def load_or_create_env():
    user_home = os.path.expanduser("~")
    acc_docs = os.path.join(_resolve_documents_folder(), "Assetto Corsa Competizione")
    default_env = {
        "ACC_SERVER_PATH": r"C:\Steam\steamapps\common\Assetto Corsa Competizione Dedicated Server\server",
        "ACC_MOTEC_PATH": os.path.join(acc_docs, "MoTeC"),
        "ACC_SETUPS_PATH": os.path.join(acc_docs, "Setups"),
        "SUPABASE_URL": "",
        "SUPABASE_KEY": "",
        "DISCORD_WEBHOOK_URL": "",
        "ENABLED_MODULES": DEFAULT_ENABLED_MODULES,
        "APP_LANGUAGE": DEFAULT_LANGUAGE,
        "APP_THEME": DEFAULT_THEME,
    }

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
    global ENABLED_MODULES, APP_LANGUAGE, APP_THEME
    ENV_VARS = load_or_create_env()
    SERVER_PATH = ENV_VARS["ACC_SERVER_PATH"]
    DEFAULT_MOTEC_PATH = ENV_VARS["ACC_MOTEC_PATH"]
    DEFAULT_SETUPS_PATH = ENV_VARS["ACC_SETUPS_PATH"]
    SUPABASE_URL = ENV_VARS.get("SUPABASE_URL", "")
    SUPABASE_KEY = ENV_VARS.get("SUPABASE_KEY", "")
    DISCORD_WEBHOOK_URL = ENV_VARS.get("DISCORD_WEBHOOK_URL", "")
    ENABLED_MODULES = _parse_enabled_modules(ENV_VARS.get("ENABLED_MODULES", ""))
    APP_LANGUAGE = ENV_VARS.get("APP_LANGUAGE", DEFAULT_LANGUAGE)
    APP_THEME = ENV_VARS.get("APP_THEME", DEFAULT_THEME)
    return ENV_VARS


ENV_VARS = load_or_create_env()
SERVER_PATH = ENV_VARS["ACC_SERVER_PATH"]
DEFAULT_MOTEC_PATH = ENV_VARS["ACC_MOTEC_PATH"]
DEFAULT_SETUPS_PATH = ENV_VARS["ACC_SETUPS_PATH"]
SUPABASE_URL = ENV_VARS.get("SUPABASE_URL", "")
SUPABASE_KEY = ENV_VARS.get("SUPABASE_KEY", "")
DISCORD_WEBHOOK_URL = ENV_VARS.get("DISCORD_WEBHOOK_URL", "")
ENABLED_MODULES = _parse_enabled_modules(ENV_VARS.get("ENABLED_MODULES", ""))
APP_LANGUAGE = ENV_VARS.get("APP_LANGUAGE", DEFAULT_LANGUAGE)
APP_THEME = ENV_VARS.get("APP_THEME", DEFAULT_THEME)

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
    from core.leaderboard_client import LeaderboardClient, SetupUsageClient
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