import json
import os
import sys
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

UI_SETTINGS_FILE = os.path.join(BASE_DIR, "ui_settings.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")

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

ENV_VARS = load_or_create_env()
SERVER_PATH = ENV_VARS["ACC_SERVER_PATH"]
DEFAULT_MOTEC_PATH = ENV_VARS["ACC_MOTEC_PATH"]
DEFAULT_SETUPS_PATH = ENV_VARS["ACC_SETUPS_PATH"]
SUPABASE_URL = ENV_VARS.get("SUPABASE_URL", "")
SUPABASE_KEY = ENV_VARS.get("SUPABASE_KEY", "")
DISCORD_WEBHOOK_URL = ENV_VARS.get("DISCORD_WEBHOOK_URL", "")

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTabWidget, QPushButton, QLabel, QComboBox, QLineEdit,
        QTableWidget, QTableWidgetItem, QSpinBox, QDoubleSpinBox, QMessageBox, QGroupBox,
        QHeaderView, QTextEdit, QCheckBox, QTreeWidget, QTreeWidgetItem, QSplitter,
        QDialog, QFormLayout, QDialogButtonBox, QInputDialog, QSlider
    )
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPixmap, QFont, QColor
except ImportError:
    print("\n[ERRO CRITICO] PyQt6 nao esta instalado no ambiente atual!")
    print("Execute no terminal: pip install PyQt6 psutil\n")
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
# Adicionar um carro/pista novo do ACC = editar so o JSON (ver core/data_loader.py).
TRACKS_DATABASE = {tid: info.get("display_name", tid) for tid, info in data_loader.all_tracks().items()}
CAR_NAMES_MAPPING = {cid: info.get("display_name", cid) for cid, info in data_loader.all_cars().items()}

DARK_STYLE = """
* { outline: none; }
QMainWindow, QWidget, QDialog { background-color: #0d0d10; color: #e8e8ed; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; }

QTabWidget::pane { border: 1px solid #232328; background-color: #17171b; border-radius: 10px; top: -1px; }
QTabBar::tab { background: transparent; color: #85858f; padding: 10px 22px; margin-right: 2px; border-top-left-radius: 8px; border-top-right-radius: 8px; font-weight: 600; }
QTabBar::tab:hover { color: #c7c7cf; }
QTabBar::tab:selected { background: #17171b; color: #ff4b3e; border-bottom: 2px solid #ff4b3e; }

QGroupBox { border: 1px solid #232328; border-radius: 10px; margin-top: 16px; padding-top: 6px; font-weight: 700; font-size: 12px; color: #ff4b3e; background-color: #131316; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 2px 8px; }

QLabel { color: #c7c7cf; }

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #0a0a0c; border: 1px solid #2b2b32; border-radius: 6px;
    padding: 7px 9px; color: #ffffff; selection-background-color: #ff4b3e;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus { border: 1px solid #ff4b3e; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView { background-color: #17171b; border: 1px solid #2b2b32; selection-background-color: #ff4b3e; selection-color: #0d0d10; outline: none; }

QTableWidget { background-color: #0a0a0c; border: 1px solid #232328; border-radius: 8px; gridline-color: #1c1c21; color: #e8e8ed; alternate-background-color: #101013; }
QTableWidget::item { padding: 4px; }
QTableWidget::item:selected { background-color: #2a1613; color: #ff4b3e; }
QHeaderView::section { background-color: #1a1a1f; color: #9a9aa4; padding: 8px; border: none; border-bottom: 1px solid #232328; font-weight: 700; }

QPushButton {
    background-color: #232328; color: #f0f0f4; border: 1px solid #2f2f36; border-radius: 8px;
    padding: 9px 18px; font-weight: 600;
}
QPushButton:hover { background-color: #2c2c33; border: 1px solid #3a3a42; }
QPushButton:pressed { background-color: #1c1c20; }
QPushButton#btn_start { background-color: #04d361; color: #062910; border: none; }
QPushButton#btn_start:hover { background-color: #05e86b; }
QPushButton#btn_reset, QPushButton#btn_delete { background-color: #ff4b3e; color: #ffffff; border: none; }
QPushButton#btn_reset:hover, QPushButton#btn_delete:hover { background-color: #e8382b; }

QTreeWidget { background-color: #0a0a0c; color: #e8e8ed; border: 1px solid #2b2b32; border-radius: 8px; }
QTreeWidget::item { padding: 3px; }
QTreeWidget::item:hover { background-color: #1a1a1f; }
QTreeWidget::item:selected { background-color: #2a1613; color: #ff4b3e; }

QSplitter::handle { background-color: #1c1c21; }
QSplitter::handle:hover { background-color: #ff4b3e; }

QCheckBox { spacing: 8px; color: #c7c7cf; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 1px solid #3a3a42; background-color: #0a0a0c; }
QCheckBox::indicator:checked { background-color: #ff4b3e; border: 1px solid #ff4b3e; }

QSlider::groove:horizontal { height: 6px; background: #232328; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #ff4b3e; border-radius: 3px; }
QSlider::add-page:horizontal { background: #232328; border-radius: 3px; }
QSlider::handle:horizontal { background: #ffffff; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }
QSlider::handle:horizontal:hover { background: #ff4b3e; }

QScrollBar:vertical { background: #0d0d10; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #2b2b32; border-radius: 5px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #3a3a42; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QMessageBox { background-color: #17171b; }
"""

class ReplicateDialog(QDialog):
    def __init__(self, cars, tracks, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Replicar Setup")
        self.resize(400, 200)

        layout = QVBoxLayout(self)
        self.car_combo = QComboBox()
        for c in cars:
            display_name = CAR_NAMES_MAPPING.get(c.lower(), c.replace("_", " ").title())
            self.car_combo.addItem(display_name, c)
            
        self.track_combo = QComboBox()
        self.track_combo.addItems(tracks)
        
        self.name_input = QLineEdit("Setup_Replicado")
        self.chk_19 = QCheckBox("Adequar pressoes de pneu para ACC v1.9 (-1.0 psi)")
        self.chk_19.setChecked(True)

        form = QFormLayout()
        form.addRow("Carro Destino:", self.car_combo)
        form.addRow("Pista Destino:", self.track_combo)
        form.addRow("Novo Nome:", self.name_input)
        
        layout.addLayout(form)
        layout.addWidget(self.chk_19)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return (
            self.car_combo.currentData(),
            self.track_combo.currentText(),
            self.name_input.text().strip(),
            self.chk_19.isChecked()
        )

class ACCManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ACC Server LAN & Telemetry Manager")
        self.resize(1200, 850)

        self.server = ServerController(SERVER_PATH)
        self.motec = MotecParser(DEFAULT_MOTEC_PATH)
        self.setup_mgr = SetupManager(DEFAULT_SETUPS_PATH)
        self.setup_creator = SetupCreator()
        self.leaderboard = LeaderboardClient(SUPABASE_URL, SUPABASE_KEY)
        self.discord = DiscordNotifier(DISCORD_WEBHOOK_URL)

        self._current_setup_path = None
        self._current_setup_dict = None

        self.init_ui()
        self.load_ui_settings()
        self.validate_paths()
        
        self.refresh_motec_filters()
        self.refresh_motec_table()
        self.refresh_setups_filters()
        self.refresh_setups_table()

    def validate_paths(self):
        warnings = []
        if not os.path.exists(SERVER_PATH):
            warnings.append(f"Servidor: {SERVER_PATH}")
        if not os.path.exists(DEFAULT_MOTEC_PATH):
            warnings.append(f"MoTeC: {DEFAULT_MOTEC_PATH}")
        if not os.path.exists(DEFAULT_SETUPS_PATH):
            warnings.append(f"Setups: {DEFAULT_SETUPS_PATH}")

        if warnings:
            msg = "Alguns diretorios configurados nao foram encontrados no seu sistema:\n\n"
            msg += "\n".join(warnings)
            msg += "\n\nPor favor, edite o arquivo '.env' na pasta do programa com os caminhos corretos do seu computador."
            QMessageBox.warning(self, "Atencao - Configuracao Necessaria", msg)

    def init_ui(self):
        tabs = QTabWidget()
        tabs.addTab(self.create_server_tab(), "Servidor LAN / Radmin")
        tabs.addTab(self.create_telemetry_tab(), "Telemetria e Rating (MoTeC)")
        tabs.addTab(self.create_setups_tab(), "Gerenciador de Setups")
        tabs.addTab(self.create_leaderboard_tab(), "Ranking dos Amigos")
        self.setCentralWidget(tabs)

    # ==========================
    # ABA 1: SERVIDOR
    # ==========================
    def create_server_tab(self):
        tab = QWidget()
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        box_general = QGroupBox("Servidor & Pista")
        gen_layout = QVBoxLayout()
        gen_layout.addWidget(QLabel("Nome do Servidor:"))
        self.input_name = QLineEdit("LAN Radmin Session")
        gen_layout.addWidget(self.input_name)
        gen_layout.addWidget(QLabel("Senha de Acesso:"))
        self.input_pass = QLineEdit()
        gen_layout.addWidget(self.input_pass)
        gen_layout.addWidget(QLabel("Selecione a Pista:"))
        self.combo_track = QComboBox()
        for track_id, track_display in TRACKS_DATABASE.items():
            self.combo_track.addItem(track_display, track_id)
        self.combo_track.currentIndexChanged.connect(self.update_track_preview)
        gen_layout.addWidget(self.combo_track)
        box_general.setLayout(gen_layout)
        left_layout.addWidget(box_general)

        sessions_weather_layout = QHBoxLayout()
        box_sessions = QGroupBox("Sessoes & Horario")
        sess_layout = QVBoxLayout()
        
        lbl_q = QHBoxLayout(); lbl_q.addWidget(QLabel("Qualy (min):"))
        self.spin_q = QSpinBox(); self.spin_q.setRange(5, 180); self.spin_q.setValue(15)
        lbl_q.addWidget(self.spin_q); sess_layout.addLayout(lbl_q)

        lbl_r = QHBoxLayout(); lbl_r.addWidget(QLabel("Race (min):"))
        self.spin_r = QSpinBox(); self.spin_r.setRange(5, 360); self.spin_r.setValue(20)
        lbl_r.addWidget(self.spin_r); sess_layout.addLayout(lbl_r)

        lbl_h = QHBoxLayout(); lbl_h.addWidget(QLabel("Hora da Corrida:"))
        self.spin_hour = QSpinBox(); self.spin_hour.setRange(0, 23); self.spin_hour.setValue(14)
        lbl_h.addWidget(self.spin_hour); sess_layout.addLayout(lbl_h)
        
        box_sessions.setLayout(sess_layout)
        sessions_weather_layout.addWidget(box_sessions)

        box_weather = QGroupBox("Clima da Pista")
        weather_layout = QVBoxLayout()
        
        lbl_temp = QHBoxLayout(); lbl_temp.addWidget(QLabel("Temperatura (C):"))
        self.spin_temp = QSpinBox(); self.spin_temp.setRange(10, 40); self.spin_temp.setValue(22)
        lbl_temp.addWidget(self.spin_temp); weather_layout.addLayout(lbl_temp)

        lbl_cloud = QHBoxLayout(); lbl_cloud.addWidget(QLabel("Nuvens (0.0 a 1.0):"))
        self.spin_cloud = QDoubleSpinBox(); self.spin_cloud.setRange(0.0, 1.0); self.spin_cloud.setSingleStep(0.1); self.spin_cloud.setValue(0.1)
        lbl_cloud.addWidget(self.spin_cloud); weather_layout.addLayout(lbl_cloud)

        lbl_rain = QHBoxLayout(); lbl_rain.addWidget(QLabel("Chuva (0.0 a 1.0):"))
        self.spin_rain = QDoubleSpinBox(); self.spin_rain.setRange(0.0, 1.0); self.spin_rain.setSingleStep(0.1); self.spin_rain.setValue(0.0)
        lbl_rain.addWidget(self.spin_rain); weather_layout.addLayout(lbl_rain)

        lbl_rnd = QHBoxLayout(); lbl_rnd.addWidget(QLabel("Aleatoriedade (0 a 7):"))
        self.spin_random = QSpinBox(); self.spin_random.setRange(0, 7); self.spin_random.setValue(1)
        lbl_rnd.addWidget(self.spin_random); weather_layout.addLayout(lbl_rnd)

        box_weather.setLayout(weather_layout)
        sessions_weather_layout.addWidget(box_weather)
        left_layout.addLayout(sessions_weather_layout)

        box_rules = QGroupBox("Regras & Slots")
        rules_layout = QVBoxLayout()
        slots_rating_layout = QHBoxLayout()
        slots_rating_layout.addWidget(QLabel("Slots:"))
        self.spin_slots = QSpinBox(); self.spin_slots.setRange(1, 30); self.spin_slots.setValue(30)
        slots_rating_layout.addWidget(self.spin_slots)
        slots_rating_layout.addWidget(QLabel(" TM:"))
        self.spin_track_medal = QSpinBox(); self.spin_track_medal.setRange(0, 3); self.spin_track_medal.setValue(0)
        slots_rating_layout.addWidget(self.spin_track_medal)
        slots_rating_layout.addWidget(QLabel(" SA:"))
        self.spin_safety = QSpinBox(); self.spin_safety.setRange(0, 99); self.spin_safety.setValue(0)
        slots_rating_layout.addWidget(self.spin_safety)
        rules_layout.addLayout(slots_rating_layout)

        self.chk_register_to_lobby = QCheckBox("Registrar no lobby (Servidor Publico)")
        rules_layout.addWidget(self.chk_register_to_lobby)
        self.chk_reset_current = QCheckBox("Limpar pasta 'current' antes de iniciar (Evita bugs)")
        self.chk_reset_current.setChecked(True)
        rules_layout.addWidget(self.chk_reset_current)
        box_rules.setLayout(rules_layout)
        left_layout.addWidget(box_rules)

        buttons_layout = QHBoxLayout()
        self.btn_save = QPushButton("Salvar Settings")
        self.btn_save.clicked.connect(self.save_ui_settings)
        buttons_layout.addWidget(self.btn_save)
        self.btn_start = QPushButton("Iniciar Servidor")
        self.btn_start.setObjectName("btn_start")
        self.btn_start.clicked.connect(self.handle_start_server)
        buttons_layout.addWidget(self.btn_start)
        left_layout.addLayout(buttons_layout)
        self.btn_reset = QPushButton("Fechar Servidor")
        self.btn_reset.setObjectName("btn_reset")
        self.btn_reset.clicked.connect(self.handle_reset_server)
        left_layout.addWidget(self.btn_reset)
        left_layout.addStretch()
        main_layout.addLayout(left_layout, stretch=1)

        right_layout = QVBoxLayout()
        box_preview = QGroupBox("Circuito")
        preview_layout = QVBoxLayout()
        self.track_img_label = QLabel()
        self.track_img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.track_img_label.setFixedSize(380, 240)
        self.track_img_label.setStyleSheet("background-color: #09090a; border: 1px dashed #323238; border-radius: 6px;")
        self.track_title_label = QLabel()
        self.track_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont(); font.setPointSize(13); font.setBold(True)
        self.track_title_label.setFont(font)
        self.track_title_label.setStyleSheet("color: #ff3b30; margin-top: 8px;")
        preview_layout.addWidget(self.track_img_label)
        preview_layout.addWidget(self.track_title_label)
        preview_layout.addStretch()
        box_preview.setLayout(preview_layout)
        right_layout.addWidget(box_preview)
        main_layout.addLayout(right_layout, stretch=1)

        tab.setLayout(main_layout)
        self.update_track_preview()
        return tab

    # ==========================
    # ABA 2: MOTEC (Telemetria)
    # ==========================
    def create_telemetry_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        btn_refresh = QPushButton("Recarregar Tempos MoTeC")
        btn_refresh.clicked.connect(self.refresh_motec_table)
        top_bar.addWidget(btn_refresh)
        
        btn_del_motec = QPushButton("Deletar Sessao Selecionada")
        btn_del_motec.setObjectName("btn_delete")
        btn_del_motec.clicked.connect(self.handle_delete_motec)
        top_bar.addWidget(btn_del_motec)

        btn_advanced = QPushButton("Telemetria Avancada (.ld)")
        btn_advanced.setStyleSheet("background-color: #007aff; color: #fff;")
        btn_advanced.clicked.connect(self.show_advanced_telemetry)
        top_bar.addWidget(btn_advanced)
        
        self.motec_car_filter = QComboBox()
        self.motec_car_filter.addItem("Todos os carros")
        self.motec_car_filter.currentIndexChanged.connect(self.refresh_motec_table)
        top_bar.addWidget(QLabel("Carro:"))
        top_bar.addWidget(self.motec_car_filter)
        self.motec_track_filter = QComboBox()
        self.motec_track_filter.addItem("Todas as pistas")
        self.motec_track_filter.currentIndexChanged.connect(self.refresh_motec_table)
        top_bar.addWidget(QLabel("Pista:"))
        top_bar.addWidget(self.motec_track_filter)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.table_motec = QTableWidget(0, 6)
        self.table_motec.setHorizontalHeaderLabels(["Pista", "Piloto", "Carro", "Melhor Volta", "Score", "Data"])
        self.table_motec.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_motec.itemSelectionChanged.connect(self.show_selected_motec_details)
        splitter.addWidget(self.table_motec)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)

        self.motec_img_label = QLabel()
        self.motec_img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.motec_img_label.setFixedSize(380, 240)
        self.motec_img_label.setStyleSheet("background-color: #09090a; border: 1px dashed #323238; border-radius: 6px;")
        right_layout.addWidget(self.motec_img_label)

        self.motec_details = QTextEdit()
        self.motec_details.setReadOnly(True)
        self.motec_details.setStyleSheet("background-color: #09090a; border: 1px solid #323238; border-radius: 6px; padding: 10px; font-size: 13px;")
        self.motec_details.setHtml("<p>Selecione uma volta para visualizar os detalhes da sessao.</p>")
        right_layout.addWidget(self.motec_details)

        splitter.addWidget(right_panel)
        splitter.setSizes([600, 400])
        layout.addWidget(splitter)
        
        tab.setLayout(layout)
        return tab

    # ==========================
    # ABA 3: SETUPS E ANALISE
    # ==========================
    def create_setups_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        btn_refresh = QPushButton("Recarregar Pasta")
        btn_refresh.clicked.connect(self.refresh_setups_table)
        top_bar.addWidget(btn_refresh)
        
        btn_del_setup = QPushButton("Deletar Setup Selecionado")
        btn_del_setup.setObjectName("btn_delete")
        btn_del_setup.clicked.connect(self.handle_delete_setup)
        top_bar.addWidget(btn_del_setup)

        self.setup_car_filter = QComboBox()
        self.setup_car_filter.addItem("Todos os carros")
        self.setup_car_filter.currentIndexChanged.connect(self.refresh_setups_table)
        top_bar.addWidget(QLabel("Carro:"))
        top_bar.addWidget(self.setup_car_filter)

        self.setup_track_filter = QComboBox()
        self.setup_track_filter.addItem("Todas as pistas")
        self.setup_track_filter.currentIndexChanged.connect(self.refresh_setups_table)
        top_bar.addWidget(QLabel("Pista:"))
        top_bar.addWidget(self.setup_track_filter)

        btn_open = QPushButton("Abrir Pasta")
        btn_open.clicked.connect(self.open_setups_directory)
        top_bar.addWidget(btn_open)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        main_splitter = QSplitter(Qt.Orientation.Vertical)

        self.table_setups = QTableWidget(0, 3)
        self.table_setups.setHorizontalHeaderLabels(["Carro", "Pista", "Nome do Setup"])
        self.table_setups.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_setups.itemSelectionChanged.connect(self.show_selected_setup_details)
        main_splitter.addWidget(self.table_setups)

        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        tree_container = QVBoxLayout()
        
        factory_box = QGroupBox("Fabrica de Setups (Quick Presets)")
        factory_layout = QHBoxLayout()
        
        btn_q = QPushButton("Gerar Qualy")
        btn_q.setStyleSheet("background-color: #ff3b30; color: #fff;")
        btn_q.clicked.connect(lambda: self.apply_preset("qualy"))
        factory_layout.addWidget(btn_q)
        
        btn_r = QPushButton("Gerar Corrida")
        btn_r.setStyleSheet("background-color: #04d361; color: #000;")
        btn_r.clicked.connect(lambda: self.apply_preset("race"))
        factory_layout.addWidget(btn_r)
        
        btn_w = QPushButton("Gerar Chuva")
        btn_w.setStyleSheet("background-color: #007aff; color: #fff;")
        btn_w.clicked.connect(lambda: self.apply_preset("wet"))
        factory_layout.addWidget(btn_w)
        
        factory_box.setLayout(factory_layout)
        tree_container.addWidget(factory_box)

        creator_box = QGroupBox("Criador de Setups Inteligente (Pista + Carro + Agressividade)")
        creator_layout = QVBoxLayout()

        creator_row1 = QHBoxLayout()
        creator_row1.addWidget(QLabel("Pista alvo:"))
        self.creator_track_combo = QComboBox()
        for track_id, track_display in TRACKS_DATABASE.items():
            self.creator_track_combo.addItem(track_display, track_id)
        creator_row1.addWidget(self.creator_track_combo, stretch=1)

        creator_row1.addWidget(QLabel("Condicao:"))
        self.creator_condition_combo = QComboBox()
        self.creator_condition_combo.addItem("Seco", "dry")
        self.creator_condition_combo.addItem("Molhado", "wet")
        creator_row1.addWidget(self.creator_condition_combo)
        creator_layout.addLayout(creator_row1)

        creator_row2 = QHBoxLayout()
        creator_row2.addWidget(QLabel("Conservador"))
        self.creator_aggr_slider = QSlider(Qt.Orientation.Horizontal)
        self.creator_aggr_slider.setRange(0, 100)
        self.creator_aggr_slider.setValue(50)
        self.creator_aggr_slider.valueChanged.connect(self._update_aggr_label)
        creator_row2.addWidget(self.creator_aggr_slider, stretch=1)
        creator_row2.addWidget(QLabel("Agressivo"))
        creator_layout.addLayout(creator_row2)

        self.creator_aggr_label = QLabel("Nivel atual: 50 (Equilibrado)")
        self.creator_aggr_label.setStyleSheet("font-weight: bold; color: #ff3b30;")
        creator_layout.addWidget(self.creator_aggr_label)

        btn_generate_smart = QPushButton("Gerar Setup Inteligente a partir do Selecionado")
        btn_generate_smart.setStyleSheet("background-color: #ff3b30; color: #fff;")
        btn_generate_smart.clicked.connect(self.generate_smart_setup)
        creator_layout.addWidget(btn_generate_smart)

        btn_calibrate = QPushButton("Calibrar Pistas com Meus Dados Reais (MoTeC)")
        btn_calibrate.clicked.connect(self.calibrate_track_speeds)
        creator_layout.addWidget(btn_calibrate)

        creator_box.setLayout(creator_layout)
        tree_container.addWidget(creator_box)

        tree_buttons = QHBoxLayout()
        btn_save_setup = QPushButton("Salvar Edicoes")
        btn_save_setup.clicked.connect(self.save_setup_edits)
        tree_buttons.addWidget(btn_save_setup)
        
        btn_clone = QPushButton("Clonar")
        btn_clone.clicked.connect(self.clone_setup)
        tree_buttons.addWidget(btn_clone)
        
        btn_replicate = QPushButton("Replicar p/ Carro")
        btn_replicate.clicked.connect(self.replicate_setup)
        tree_buttons.addWidget(btn_replicate)
        tree_container.addLayout(tree_buttons)

        self.setup_tree = QTreeWidget()
        self.setup_tree.setHeaderLabels(["Parametro do Setup", "Valor Editavel"])
        self.setup_tree.setColumnWidth(0, 220)
        self.setup_tree.itemChanged.connect(self.on_tree_item_changed)
        tree_container.addWidget(self.setup_tree)
        
        tree_widget_container = QWidget()
        tree_widget_container.setLayout(tree_container)
        bottom_layout.addWidget(tree_widget_container, stretch=1)

        advisor_container = QVBoxLayout()
        self.setup_advisor = QTextEdit()
        self.setup_advisor.setReadOnly(True)
        self.setup_advisor.setStyleSheet("background-color: #09090a; border: 1px solid #323238; border-radius: 6px; padding: 12px; font-size: 14px;")
        self.setup_advisor.setHtml("<h3>Engenheiro de Pista Virtual</h3><p>Selecione um setup para avaliar o impacto aerodinamico e mecanico na sua seguranca vs pace.</p>")
        advisor_container.addWidget(self.setup_advisor)
        
        btn_copy_tips = QPushButton("Copiar Relatorio e Dicas")
        btn_copy_tips.clicked.connect(self.copy_setup_analysis)
        advisor_container.addWidget(btn_copy_tips)

        advisor_widget_container = QWidget()
        advisor_widget_container.setLayout(advisor_container)
        bottom_layout.addWidget(advisor_widget_container, stretch=1)

        main_splitter.addWidget(bottom_widget)
        main_splitter.setSizes([200, 400]) 
        layout.addWidget(main_splitter)

        tab.setLayout(layout)
        return tab

    # ==========================
    # ABA 4: RANKING DOS AMIGOS
    # ==========================
    def create_leaderboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        config_box = QGroupBox("Sua Identidade")
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("Seu nome de piloto:"))
        self.input_driver_name = QLineEdit()
        self.input_driver_name.setPlaceholderText("Ex: Joao Silva")
        self.input_driver_name.editingFinished.connect(lambda: self.save_ui_settings(silent=True))
        config_layout.addWidget(self.input_driver_name, stretch=1)

        status_text = "Conectado" if self.leaderboard.enabled else "Nao configurado (defina SUPABASE_URL e SUPABASE_KEY no .env)"
        status_color = "#04d361" if self.leaderboard.enabled else "#ff4b3e"
        self.leaderboard_status_label = QLabel(f"Ranking: {status_text}")
        self.leaderboard_status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        config_layout.addWidget(self.leaderboard_status_label)

        discord_text = "Discord conectado" if self.discord.enabled else "Discord nao configurado (defina DISCORD_WEBHOOK_URL no .env)"
        discord_color = "#04d361" if self.discord.enabled else "#a8a8b3"
        self.discord_status_label = QLabel(discord_text)
        self.discord_status_label.setStyleSheet(f"color: {discord_color}; font-weight: bold;")
        config_layout.addWidget(self.discord_status_label)
        config_box.setLayout(config_layout)
        layout.addWidget(config_box)

        top_bar = QHBoxLayout()
        btn_refresh_lb = QPushButton("Atualizar Ranking")
        btn_refresh_lb.clicked.connect(self.refresh_leaderboard_table)
        top_bar.addWidget(btn_refresh_lb)

        btn_submit_lb = QPushButton("Enviar Meus Melhores Tempos (MoTeC)")
        btn_submit_lb.setStyleSheet("background-color: #04d361; color: #000;")
        btn_submit_lb.clicked.connect(self.submit_my_best_laps)
        top_bar.addWidget(btn_submit_lb)

        self.lb_car_filter = QComboBox()
        self.lb_car_filter.addItem("Todos os carros", None)
        for car_display in sorted(set(CAR_NAMES_MAPPING.values())):
            self.lb_car_filter.addItem(car_display, car_display)
        self.lb_car_filter.currentIndexChanged.connect(self.refresh_leaderboard_table)
        top_bar.addWidget(QLabel("Carro:"))
        top_bar.addWidget(self.lb_car_filter)

        self.lb_track_filter = QComboBox()
        self.lb_track_filter.addItem("Todas as pistas", None)
        for track_id, track_display in TRACKS_DATABASE.items():
            self.lb_track_filter.addItem(track_display, track_id)
        self.lb_track_filter.currentIndexChanged.connect(self.refresh_leaderboard_table)
        top_bar.addWidget(QLabel("Pista:"))
        top_bar.addWidget(self.lb_track_filter)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        self.table_leaderboard = QTableWidget(0, 6)
        self.table_leaderboard.setHorizontalHeaderLabels(
            ["#", "Piloto", "Carro", "Pista", "Melhor Volta", "Enviado em"]
        )
        self.table_leaderboard.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_leaderboard)

        note = QLabel(
            "Dica: o ranking mostra o melhor tempo de cada piloto por combinacao de carro+pista. "
            "Toda sessao enviada fica guardada no historico, entao da pra acompanhar sua evolucao com o tempo."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #a8a8b3; font-size: 12px;")
        layout.addWidget(note)

        tab.setLayout(layout)
        return tab

    def submit_my_best_laps(self):
        if not self.leaderboard.enabled:
            QMessageBox.warning(self, "Ranking nao configurado",
                                 "Defina SUPABASE_URL e SUPABASE_KEY no arquivo .env para usar o ranking compartilhado.\n"
                                 "Veja as instrucoes em core/leaderboard_client.py.")
            return

        driver_name = self.input_driver_name.text().strip()
        if not driver_name:
            QMessageBox.warning(self, "Aviso", "Preencha seu nome de piloto antes de enviar.")
            return

        laps = self.motec.get_best_laps()
        if not laps:
            QMessageBox.information(self, "Sem dados", "Nenhuma volta encontrada na pasta do MoTeC.")
            return

        best_per_combo = {}
        for lap in laps:
            # Mesmo filtro de "tempo irreal/glitch" usado na aba de Telemetria
            # (voltas abaixo de 70s sao fisicamente impossiveis em GT3/GT4 no ACC).
            if lap.get("raw_time", 0) < 70.0:
                continue
            key = (lap["car"], lap["track_id"])
            if key not in best_per_combo or lap["raw_time"] < best_per_combo[key]["raw_time"]:
                best_per_combo[key] = lap

        sent, failed = 0, 0
        for (car, track_id), lap in best_per_combo.items():
            try:
                # Confere se esse tempo bate o recorde atual do grupo ANTES de enviar,
                # para so notificar no Discord quando for uma quebra de recorde de verdade.
                is_new_record = False
                if self.discord.enabled:
                    try:
                        existing = self.leaderboard.fetch_raw(track_id=track_id, car_id=car)
                        current_best = min((r["lap_time_seconds"] for r in existing), default=None)
                        is_new_record = current_best is None or lap["raw_time"] < current_best
                    except Exception:
                        is_new_record = False

                self.leaderboard.submit_lap(
                    driver_name=driver_name,
                    car_id=car,
                    track_id=track_id,
                    lap_time_seconds=lap["raw_time"],
                    lap_time_formatted=lap["lap_time"],
                    session_type=lap.get("session_type"),
                    track_temp=lap.get("track_temp"),
                    ambient_temp=lap.get("ambient_temp"),
                )
                sent += 1
                if is_new_record:
                    self.discord.notify_new_record(
                        driver_name=driver_name,
                        car_display=car,
                        track_display=TRACKS_DATABASE.get(track_id, track_id),
                        lap_time_formatted=lap["lap_time"],
                    )
            except Exception:
                failed += 1

        self.refresh_leaderboard_table()
        QMessageBox.information(self, "Envio concluido",
                                 f"{sent} tempo(s) enviado(s) com sucesso.\n{failed} falha(s).")

    def refresh_leaderboard_table(self):
        if not self.leaderboard.enabled:
            return
        car_id = self.lb_car_filter.currentData()
        track_id = self.lb_track_filter.currentData()
        try:
            rows = self.leaderboard.fetch_raw(track_id=track_id, car_id=car_id)
        except Exception as e:
            QMessageBox.critical(self, "Erro ao buscar ranking", str(e))
            return

        best_rows = self.leaderboard.best_per_driver(rows)
        self.table_leaderboard.setRowCount(len(best_rows))
        for i, r in enumerate(best_rows):
            display_car = r.get("car_id", "")
            display_track = TRACKS_DATABASE.get(r.get("track_id", ""), r.get("track_id", ""))
            self.table_leaderboard.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table_leaderboard.setItem(i, 1, QTableWidgetItem(r.get("driver_name", "")))
            self.table_leaderboard.setItem(i, 2, QTableWidgetItem(display_car))
            self.table_leaderboard.setItem(i, 3, QTableWidgetItem(display_track))
            self.table_leaderboard.setItem(i, 4, QTableWidgetItem(r.get("lap_time_formatted", "")))
            self.table_leaderboard.setItem(i, 5, QTableWidgetItem(str(r.get("recorded_at", ""))[:16].replace("T", " ")))

    # ==========================
    # METODOS SERVIDOR E UI
    # ==========================
    def save_ui_settings(self, silent=False):
        settings = {
            "server_name": self.input_name.text(),
            "password": self.input_pass.text(),
            "track": self.combo_track.currentData(),
            "q_min": self.spin_q.value(),
            "r_min": self.spin_r.value(),
            "hour": self.spin_hour.value(),
            "temp": self.spin_temp.value(),
            "cloud": round(self.spin_cloud.value(), 2),
            "rain": round(self.spin_rain.value(), 2),
            "random": self.spin_random.value(),
            "slots": self.spin_slots.value(),
            "tm": self.spin_track_medal.value(),
            "sa": self.spin_safety.value(),
            "lobby": self.chk_register_to_lobby.isChecked(),
            "reset": self.chk_reset_current.isChecked(),
            "driver_name": self.input_driver_name.text() if hasattr(self, "input_driver_name") else ""
        }
        try:
            with open(UI_SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
            if not silent: QMessageBox.information(self, "Salvo", "Configuracoes salvas com sucesso!")
        except Exception as e:
            if not silent: QMessageBox.warning(self, "Erro", f"Nao foi possivel salvar: {e}")

    def load_ui_settings(self):
        if not os.path.exists(UI_SETTINGS_FILE): return
        try:
            with open(UI_SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
            self.input_name.setText(settings.get("server_name", "LAN Radmin Session"))
            self.input_pass.setText(settings.get("password", ""))
            track = settings.get("track", "monza")
            idx = self.combo_track.findData(track)
            if idx >= 0: self.combo_track.setCurrentIndex(idx)
            self.spin_q.setValue(settings.get("q_min", 15))
            self.spin_r.setValue(settings.get("r_min", 20))
            self.spin_hour.setValue(settings.get("hour", 14))
            self.spin_temp.setValue(settings.get("temp", 22))
            self.spin_cloud.setValue(settings.get("cloud", 0.1))
            self.spin_rain.setValue(settings.get("rain", 0.0))
            self.spin_random.setValue(settings.get("random", 1))
            self.spin_slots.setValue(settings.get("slots", 30))
            self.spin_track_medal.setValue(settings.get("tm", 0))
            self.spin_safety.setValue(settings.get("sa", 0))
            self.chk_register_to_lobby.setChecked(settings.get("lobby", False))
            self.chk_reset_current.setChecked(settings.get("reset", True))
            if hasattr(self, "input_driver_name"):
                self.input_driver_name.setText(settings.get("driver_name", ""))
        except Exception:
            pass

    def handle_start_server(self):
        try:
            self.save_ui_settings(silent=True)
            track_id = self.combo_track.currentData()
            max_slots = self.spin_slots.value()
            track_medal = self.spin_track_medal.value()
            safety_rating = self.spin_safety.value()
            register_to_lobby = 1 if self.chk_register_to_lobby.isChecked() else 0
            is_public = (register_to_lobby == 1) and (not self.input_pass.text().strip())

            if max_slots > 10 and is_public:
                if track_medal < 3 or safety_rating < 70:
                    reply = QMessageBox.warning(
                        self, "Aviso de Limitacao",
                        "Servidores publicos exigem 3 TM e 70 SA para mais de 10 carros. Deseja iniciar?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No: return

            self.server.start(
                server_name=self.input_name.text(), password=self.input_pass.text(), track=track_id,
                q_min=self.spin_q.value(), r_min=self.spin_r.value(),
                max_car_slots=max_slots, track_medals_requirement=track_medal, safety_rating_requirement=safety_rating,
                register_to_lobby=register_to_lobby, force_current_reset=self.chk_reset_current.isChecked(),
                hour=self.spin_hour.value(), temp=self.spin_temp.value(),
                cloud=self.spin_cloud.value(), rain=self.spin_rain.value(), randomness=self.spin_random.value()
            )
            QMessageBox.information(self, "Sucesso", f"Servidor iniciado com a pista {track_id.upper()}!")
            self.discord.notify_server_started(
                server_name=self.input_name.text() or "Servidor LAN",
                track_display=TRACKS_DATABASE.get(track_id, track_id),
                slots=max_slots,
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Iniciar", str(e))

    def handle_reset_server(self):
        try:
            self.server.stop_server()
            QMessageBox.information(self, "Servidor Finalizado", "accServer.exe foi fechado.")
            self.discord.notify_server_stopped(server_name=self.input_name.text() or "Servidor LAN")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def update_track_preview(self):
        track_id = self.combo_track.currentData()
        self.track_title_label.setText(self.combo_track.currentText().upper())
        img_path = self._find_track_image(track_id)
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                self.track_img_label.setPixmap(pixmap.scaled(self.track_img_label.width(), self.track_img_label.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                return
        self.track_img_label.clear()
        self.track_img_label.setText(f"[Sem imagem disponivel para {track_id}]")

    def _find_track_image(self, track_id):
        if not track_id: return None
        for ext in SUPPORTED_IMAGE_EXTENSIONS:
            cand = os.path.join(ASSETS_DIR, f"{track_id}{ext}")
            if os.path.exists(cand): return cand
        return None

    # ==========================
    # METODOS MOTEC E TELEMETRIA
    # ==========================
    def refresh_motec_filters(self):
        laps = self.motec.get_best_laps()
        self.motec_car_filter.blockSignals(True)
        self.motec_car_filter.clear(); self.motec_car_filter.addItem("Todos os carros")
        for car in sorted({lap["car"] for lap in laps}): self.motec_car_filter.addItem(car)
        self.motec_car_filter.blockSignals(False)

        self.motec_track_filter.blockSignals(True)
        self.motec_track_filter.clear(); self.motec_track_filter.addItem("Todas as pistas")
        for track in sorted({lap["track"] for lap in laps}): self.motec_track_filter.addItem(track)
        self.motec_track_filter.blockSignals(False)

    def refresh_motec_table(self):
        laps = self.motec.get_best_laps()
        c_val = self.motec_car_filter.currentText()
        t_val = self.motec_track_filter.currentText()
        if c_val != "Todos os carros": laps = [l for l in laps if l["car"] == c_val]
        if t_val != "Todas as pistas": laps = [l for l in laps if l["track"] == t_val]

        # Calculo de Track Records para geracao de Score
        track_records = {}
        for lap in laps:
            t = lap["track"]
            rt = lap["raw_time"]
            if rt >= 70.0:
                if t not in track_records or rt < track_records[t]:
                    track_records[t] = rt

        self.table_motec.setRowCount(len(laps))
        for row, lap in enumerate(laps):
            rt = lap["raw_time"]
            if rt < 70.0:
                lap["is_valid"] = False
                lap["score"] = 0.0
            else:
                lap["is_valid"] = True
                tr = track_records.get(lap["track"], rt)
                pace_score = (tr / rt) * 5.0
                cons_score = min(5.0, lap.get("total_laps", 0) / 2.0)
                lap["score"] = round(pace_score + cons_score, 1)

            self.table_motec.setItem(row, 0, QTableWidgetItem(lap["track"]))
            self.table_motec.setItem(row, 1, QTableWidgetItem(lap["driver"]))
            self.table_motec.setItem(row, 2, QTableWidgetItem(lap["car"]))
            self.table_motec.setItem(row, 3, QTableWidgetItem(lap["lap_time"]))
            
            score_item = QTableWidgetItem(f"{lap['score']}/10")
            if not lap["is_valid"]:
                score_item.setForeground(QColor("#ff3b30"))
            self.table_motec.setItem(row, 4, score_item)
            
            self.table_motec.setItem(row, 5, QTableWidgetItem(lap["date"]))
            
            # Armazena os dados completos para o display lateral
            self.table_motec.item(row, 0).setData(Qt.ItemDataRole.UserRole, lap)

    def show_advanced_telemetry(self):
        if not self.table_motec.selectedItems():
            QMessageBox.warning(self, "Aviso", "Selecione uma sessao na tabela primeiro.")
            return

        row = self.table_motec.currentRow()
        lap = self.table_motec.item(row, 0).data(Qt.ItemDataRole.UserRole)
        ldx_path = lap.get("file_path")
        ld_path = ld_telemetry_parser.get_ld_path(ldx_path) if ldx_path else None

        if not ld_path or not os.path.exists(ld_path):
            QMessageBox.warning(self, "Arquivo .ld nao encontrado",
                                 f"Nao encontrei o arquivo binario de telemetria ao lado do .ldx:\n{ld_path}\n\n"
                                 "Ele e gerado automaticamente pelo ACC junto com o .ldx - confira se nao foi movido/apagado.")
            return

        try:
            analysis = ld_telemetry_parser.analyze_session(ld_path, ldx_path)
        except Exception as e:
            QMessageBox.critical(self, "Erro ao ler telemetria", str(e))
            return

        laps = analysis["laps"]
        if not laps:
            QMessageBox.information(self, "Sem dados", "Nao foi possivel extrair voltas dessa sessao.")
            return

        # Ordena pelas voltas mais rapidas primeiro pra facilitar comparacao
        laps_sorted = sorted(laps, key=lambda l: l["lap_time_s"])

        html = f"<h3>Telemetria Avancada: {lap['track']}</h3>"
        html += f"<p style='color:#a8a8b3;'>Extraido diretamente do arquivo binario .ld (nao e estimativa) - {len(laps)} volta(s) detectada(s), {len(analysis['channels_available'])} canais disponiveis.</p><hr>"
        html += "<table cellspacing='6' style='width:100%; font-size:12px;'>"
        html += ("<tr style='color:#a8a8b3;'><th align='left'>Volta</th><th>Tempo</th><th>Vel.Max</th>"
                 "<th>%Full Throttle</th><th>Freadas Fortes</th><th>Lat. G (p99)</th><th>Freio G (p99)</th>"
                 "<th>Temp.Pneu</th><th>Temp.Freio</th></tr>")
        for l in laps_sorted[:15]:
            html += "<tr>"
            html += f"<td>{l['lap']}</td>"
            html += f"<td>{l['lap_time_s']:.3f}s</td>"
            html += f"<td>{l.get('max_speed_kmh', '-')} km/h</td>"
            html += f"<td>{l.get('full_throttle_pct_of_lap', '-')}%</td>"
            html += f"<td>{l.get('hard_brake_events', '-')}</td>"
            html += f"<td>{l.get('lat_g_p99', '-')}g</td>"
            html += f"<td>{l.get('brake_g_p99', '-')}g</td>"
            html += f"<td>{l.get('avg_tyre_temp_c', '-')}C</td>"
            html += f"<td>{l.get('avg_brake_temp_c', '-')}C</td>"
            html += "</tr>"
        html += "</table><hr>"
        html += ("<p style='color:#a8a8b3; font-size:12px;'>Freadas fortes = numero de vezes que o freio passou de "
                  f"{ld_telemetry_parser.HARD_BRAKE_THRESHOLD_PCT:.0f}% na volta. Lat./Freio G no percentil 99 "
                  "(evita que um unico pico de zebra/impacto distorca o numero). Use isso pra comparar seu estilo de "
                  "pilotagem entre voltas ou pra calibrar a base de pistas com dados reais (botao na aba de Setups).</p>")

        self.motec_details.setHtml(html)

    def show_selected_motec_details(self):
        if not self.table_motec.selectedItems(): return
        row = self.table_motec.currentRow()
        lap = self.table_motec.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        track_id = lap.get("track_id")
        img_path = self._find_track_image(track_id)
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            self.motec_img_label.setPixmap(pixmap.scaled(self.motec_img_label.width(), self.motec_img_label.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.motec_img_label.clear()
            self.motec_img_label.setText(f"[Sem imagem para {track_id}]")

        total_laps = lap.get("total_laps", 0)
        session_t = lap.get("session_type", "N/A")
        t_temp = lap.get("track_temp", "N/A")
        a_temp = lap.get("ambient_temp", "N/A")
        v_weight = lap.get("vehicle_weight", "N/A")

        if not lap.get("is_valid", True):
            html = f"""
            <h3 style="color:#ff3b30;">ALERTA DE TEMPO IRREAL (GLITCH)</h3>
            <p>O tempo de <b>{lap['lap_time']}</b> em {lap['track']} e fisicamente impossivel para um carro classe GT3.<br>
            A sessao foi invalidada pelo sistema e recebeu Score 0/10.</p>
            """
            self.motec_details.setHtml(html)
            return

        cn_impact = "Baixo (Sessao curta ou inconsistente)"
        if total_laps >= 5: cn_impact = "Moderado (Sessao util para ganhar pontos iniciais de CN)"
        if total_laps >= 10: cn_impact = "Alto (Sessao excelente para fixar Rating de Consistencia)"

        html = f"""
        <h3>Telemetria MoTeC: {lap['track']}</h3>
        <p><b>Piloto:</b> {lap['driver']}<br>
        <b>Carro:</b> {lap['car']}<br>
        <b>Tipo de Sessao:</b> {session_t}<br>
        <b>Condicoes Climaticas:</b> Ar {a_temp}C | Asfalto {t_temp}C<br>
        <b>Data do Arquivo:</b> {lap['date']}</p>
        <hr>
        <p><b>Voltas Completadas:</b> {total_laps}<br>
        <b>Melhor Tempo:</b> <span style='color:#04d361; font-weight:bold;'>{lap['lap_time']}</span><br>
        <b>Score da Sessao:</b> {lap.get('score', 0)} / 10</p>
        <hr>
        <h4>Analise Tecnica e Velocidade de Apex:</h4>
        <p style='color:#a8a8b3;'>A extracao detalhada de Apex (VMin), Forca G, e Tracao exigem a leitura de arquivos binarios (.ld). Para inspecionar esses dados vitais para seu pace, carregue o arquivo de telemetria diretamente no <b>MoTeC i2 Pro</b> usando o Workspace oficial do ACC.</p>
        <hr>
        <h4>Efeito no seu Rating (ACC):</h4>
        <ul>
            <li><b>Consistencia (CN):</b> {cn_impact}.</li>
            <li><b>Car Control (CC):</b> Lembre-se que derrapar alem do angulo ideal de slip (Overdriving) nesta sessao machuca sua pontuacao CC a cada curva.</li>
        </ul>
        """
        self.motec_details.setHtml(html)

    def handle_delete_motec(self):
        if not self.table_motec.selectedItems():
            QMessageBox.warning(self, "Aviso", "Selecione uma sessao primeiro.")
            return
        row = self.table_motec.currentRow()
        lap = self.table_motec.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, "Confirmar Exclusao", f"Deseja realmente apagar a sessao de {lap['track']} permanentemente?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.motec.delete_telemetry(lap["file_path"])
                self.refresh_motec_table()
                self.motec_img_label.clear()
                self.motec_details.clear()
                QMessageBox.information(self, "Sucesso", "Sessao excluida.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

    # ==========================
    # METODOS DE SETUPS E PRESETS
    # ==========================
    def refresh_setups_filters(self):
        setups = self.setup_mgr.list_all_setups()
        self.setup_car_filter.blockSignals(True)
        self.setup_car_filter.clear(); self.setup_car_filter.addItem("Todos os carros")
        
        car_set = sorted({s["car"] for s in setups})
        for car in car_set: 
            display_name = CAR_NAMES_MAPPING.get(car.lower(), car.replace("_", " ").title())
            self.setup_car_filter.addItem(display_name, car)
            
        self.setup_car_filter.blockSignals(False)

        self.setup_track_filter.blockSignals(True)
        self.setup_track_filter.clear(); self.setup_track_filter.addItem("Todas as pistas")
        for track in sorted({s["track"] for s in setups}): self.setup_track_filter.addItem(track)
        self.setup_track_filter.blockSignals(False)

    def refresh_setups_table(self):
        car_val = self.setup_car_filter.currentData() if self.setup_car_filter.currentIndex() > 0 else "Todos os carros"
        track_val = self.setup_track_filter.currentText()
        
        setups = self.setup_mgr.get_filtered_setups(car_val, track_val)
        self.table_setups.setRowCount(len(setups))
        for row, s in enumerate(setups):
            display_car = CAR_NAMES_MAPPING.get(s["car"].lower(), s["car"].replace("_", " ").title())
            self.table_setups.setItem(row, 0, QTableWidgetItem(display_car))
            self.table_setups.setItem(row, 1, QTableWidgetItem(s["track"]))
            self.table_setups.setItem(row, 2, QTableWidgetItem(s["name"]))
            self.table_setups.item(row, 0).setData(Qt.ItemDataRole.UserRole, s)

    def show_selected_setup_details(self):
        if not self.table_setups.selectedItems(): return
        
        row = self.table_setups.currentRow()
        setup = self.table_setups.item(row, 0).data(Qt.ItemDataRole.UserRole)

        self._current_setup_path = setup["file_path"]
        self._current_setup_dict = self.setup_mgr.get_setup_details(setup["file_path"])
        
        if not self._current_setup_dict: return

        self.setup_tree.blockSignals(True)
        self.setup_tree.clear()
        root = QTreeWidgetItem(self.setup_tree)
        display_car = CAR_NAMES_MAPPING.get(setup["car"].lower(), setup["car"].replace("_", " ").title())
        root.setText(0, f"Carro: {display_car} | Pista: {setup['track']}")
        root.setExpanded(True)
        self.populate_tree(root, self._current_setup_dict)
        self.setup_tree.blockSignals(False)

        self.run_setup_analysis(display_car, setup["track"], self._current_setup_dict)

    def populate_tree(self, parent_item, data_dict):
        if not isinstance(data_dict, dict): return
        for key, value in data_dict.items():
            item = QTreeWidgetItem(parent_item)
            item.setText(0, str(key))
            if isinstance(value, dict):
                self.populate_tree(item, value)
            else:
                item.setData(1, Qt.ItemDataRole.UserRole, (data_dict, key, type(value)))
                if isinstance(value, list):
                    item.setText(1, json.dumps(value))
                else:
                    item.setText(1, str(value))
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)

    def on_tree_item_changed(self, item, column):
        if column != 1: return
        user_data = item.data(1, Qt.ItemDataRole.UserRole)
        if not user_data: return
        data_dict, key, val_type = user_data
        
        new_text = item.text(1)
        try:
            if val_type == list or val_type == dict:
                parsed_val = json.loads(new_text)
            elif val_type == bool:
                parsed_val = new_text.lower() in ['true', '1', 't', 'y', 'yes']
            else:
                parsed_val = val_type(new_text)
                
            data_dict[key] = parsed_val
            item.setForeground(1, QColor("#04d361")) 
            
            if self.table_setups.selectedItems():
                row = self.table_setups.currentRow()
                setup = self.table_setups.item(row, 0).data(Qt.ItemDataRole.UserRole)
                display_car = CAR_NAMES_MAPPING.get(setup["car"].lower(), setup["car"].replace("_", " ").title())
                self.run_setup_analysis(display_car, setup["track"], self._current_setup_dict)
                
        except Exception:
            item.setForeground(1, QColor("#ff3b30")) 

    def save_setup_edits(self):
        if not self._current_setup_path or not self._current_setup_dict:
            QMessageBox.warning(self, "Aviso", "Selecione um setup na tabela primeiro.")
            return
        try:
            self.setup_mgr.save_setup(self._current_setup_path, self._current_setup_dict)
            QMessageBox.information(self, "Sucesso", "Modificacoes no setup foram salvas.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Nao foi possivel salvar: {e}")

    def handle_delete_setup(self):
        if not self._current_setup_path:
            QMessageBox.warning(self, "Aviso", "Selecione um setup primeiro.")
            return
        reply = QMessageBox.question(self, "Confirmar Exclusao", "Deseja realmente apagar este setup permanentemente?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.setup_mgr.delete_setup(self._current_setup_path)
                self.refresh_setups_table()
                self.setup_tree.clear()
                self.setup_advisor.clear()
                self._current_setup_path = None
                self._current_setup_dict = None
                QMessageBox.information(self, "Sucesso", "Setup excluido.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

    def clone_setup(self):
        if not self._current_setup_path:
            QMessageBox.warning(self, "Aviso", "Selecione um setup primeiro.")
            return
        new_name, ok = QInputDialog.getText(self, "Clonar Setup", "Digite o nome para o clone:")
        if ok and new_name.strip():
            try:
                self.setup_mgr.clone_setup(self._current_setup_path, new_name.strip())
                self.refresh_setups_table()
                QMessageBox.information(self, "Sucesso", "Setup clonado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

    def replicate_setup(self):
        if not self._current_setup_path:
            QMessageBox.warning(self, "Aviso", "Selecione um setup primeiro.")
            return
        cars, tracks = self.setup_mgr.get_available_cars_and_tracks()
        dialog = ReplicateDialog(cars, tracks, self)
        if dialog.exec():
            target_car, target_track, new_name, adjust_19 = dialog.get_data()
            if not new_name:
                QMessageBox.warning(self, "Aviso", "O nome nao pode ser vazio.")
                return
            try:
                self.setup_mgr.replicate_setup(self._current_setup_path, target_car, target_track, new_name, adjust_19)
                self.refresh_setups_table()
                QMessageBox.information(self, "Sucesso", f"Setup replicado para {target_car} em {target_track}!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

    def apply_preset(self, preset_type):
        if not self._current_setup_path or not self._current_setup_dict:
            QMessageBox.warning(self, "Aviso", "Selecione um setup base primeiro na tabela.")
            return
            
        base_name = os.path.basename(self._current_setup_path).replace(".json", "")
        if preset_type == "qualy":
            new_data = self.setup_mgr.generate_qualy_preset(self._current_setup_dict)
            suffix = "_Q"
            msg = "criado com baixo combustivel e pastilhas 1."
        elif preset_type == "race":
            new_data = self.setup_mgr.generate_race_preset(self._current_setup_dict)
            suffix = "_R"
            msg = "criado com combustivel para stint e pastilhas 2."
        elif preset_type == "wet":
            new_data = self.setup_mgr.generate_wet_preset(self._current_setup_dict)
            suffix = "_W"
            msg = "criado com pneu de chuva, pastilhas 3 e aero alterada."
            
        new_name, ok = QInputDialog.getText(self, "Salvar Preset", "Nome do novo arquivo:", QLineEdit.EchoMode.Normal, f"{base_name}{suffix}")
        if ok and new_name.strip():
            target_dir = os.path.dirname(self._current_setup_path)
            new_path = self.setup_mgr.get_unique_filename(target_dir, new_name.strip())
            try:
                self.setup_mgr.save_setup(new_path, new_data)
                self.refresh_setups_table()
                QMessageBox.information(self, "Preset Gerado", f"Setup {msg}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

    def _update_aggr_label(self, value):
        from core.setup_creator import aggressiveness_label
        self.creator_aggr_label.setText(f"Nivel atual: {value} ({aggressiveness_label(value)})")

    def calibrate_track_speeds(self):
        laps = self.motec.get_best_laps()
        speed_suggestions = track_profile_calibrator.suggest_avg_speed_ratings(laps)
        brake_suggestions = track_profile_calibrator.suggest_brake_stress_ratings(laps)

        if not speed_suggestions and not brake_suggestions:
            QMessageBox.information(self, "Sem dados suficientes",
                                     "Nenhum tempo de volta valido encontrado no MoTeC para calibrar. "
                                     "Rode algumas sessoes primeiro.")
            return

        lines = []
        if speed_suggestions:
            lines.append("VELOCIDADE MEDIA (a partir do tempo de volta):")
            for track_id, info in sorted(speed_suggestions.items(), key=lambda kv: kv[1]["computed_kmh"], reverse=True):
                track_name = TRACKS_DATABASE.get(track_id, track_id)
                arrow = "->" if info["suggested_rating"] != info["current_rating"] else "=="
                lines.append(f"  {track_name}: {info['computed_kmh']} km/h medio -> nota atual "
                             f"{info['current_rating']} {arrow} sugerida {info['suggested_rating']}")

        if brake_suggestions:
            lines.append("")
            lines.append("EXIGENCIA DE FREIO (a partir da telemetria .ld real):")
            for track_id, info in sorted(brake_suggestions.items(), key=lambda kv: kv[1]["computed_kmh"], reverse=True):
                track_name = TRACKS_DATABASE.get(track_id, track_id)
                arrow = "->" if info["suggested_rating"] != info["current_rating"] else "=="
                lines.append(f"  {track_name}: {info['computed_kmh']} freadas fortes/volta -> nota atual "
                             f"{info['current_rating']} {arrow} sugerida {info['suggested_rating']}")
        else:
            lines.append("")
            lines.append("(Exigencia de freio nao calibrada: nenhum arquivo .ld encontrado ao lado dos .ldx.)")

        msg = "\n".join(lines) + "\n\nAplicar as sugestoes agora? (so pistas com diferenca >= 1 ponto sao alteradas)"
        reply = QMessageBox.question(self, "Calibrar Base de Pistas", msg,
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            changed = track_profile_calibrator.apply_suggestions(speed_suggestions, field="avg_speed")
            changed += track_profile_calibrator.apply_suggestions(brake_suggestions, field="brake_stress")
            QMessageBox.information(self, "Calibracao aplicada",
                                     f"{changed} atualizacao(oes) gravada(s) em core/data/tracks.json.")

    def generate_smart_setup(self):
        if not self._current_setup_path or not self._current_setup_dict:
            QMessageBox.warning(self, "Aviso", "Selecione um setup base na tabela primeiro "
                                 "(pode ser o setup padrao do carro ou qualquer setup salvo).")
            return

        row = self.table_setups.currentRow()
        setup_meta = self.table_setups.item(row, 0).data(Qt.ItemDataRole.UserRole)
        car_id = setup_meta["car"]
        track_id = self.creator_track_combo.currentData()
        condition = self.creator_condition_combo.currentData()
        aggressiveness = self.creator_aggr_slider.value()

        try:
            new_data, meta = self.setup_creator.generate_smart_setup(
                self._current_setup_dict, car_id, track_id, aggressiveness, condition
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Nao foi possivel gerar o setup: {e}")
            return

        base_name = os.path.basename(self._current_setup_path).replace(".json", "")
        suffix = f"_{track_id}_{aggressiveness}_{'W' if condition == 'wet' else 'S'}"
        suggested_name = f"{base_name}{suffix}"

        new_name, ok = QInputDialog.getText(
            self, "Salvar Setup Inteligente", "Nome do novo arquivo:",
            QLineEdit.EchoMode.Normal, suggested_name
        )
        if not (ok and new_name.strip()):
            return

        target_dir = os.path.join(self.setup_mgr.setups_folder, car_id, track_id)
        os.makedirs(target_dir, exist_ok=True)
        new_path = self.setup_mgr.get_unique_filename(target_dir, new_name.strip())

        try:
            self.setup_mgr.save_setup(new_path, new_data)
            self.refresh_setups_filters()
            self.refresh_setups_table()

            report = f"<h3>Setup Inteligente Gerado</h3>"
            report += f"<p><b>Pista:</b> {TRACKS_DATABASE.get(track_id, track_id)}<br>"
            report += f"<b>Nivel:</b> {meta['aggressiveness']} ({meta['aggressiveness_label']})<br>"
            report += f"<b>Condicao:</b> {'Molhado' if condition == 'wet' else 'Seco'}</p><hr>"
            report += "<h4>Ajustes aplicados:</h4><ul>"
            for n in meta["notes"]:
                report += f"<li>{n}</li>"
            report += "</ul>"
            self.setup_advisor.setHtml(report)

            QMessageBox.information(self, "Sucesso", f"Setup inteligente salvo em:\n{new_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def run_setup_analysis(self, car, track, setup_data):
        best_lap_time = "Nenhum tempo salvo"
        laps = self.motec.get_best_laps()
        for lap in laps:
            if lap.get("car", "").lower() == car.lower() and lap.get("track", "").lower() == track.lower():
                if lap.get("raw_time", 0) >= 70.0:
                    best_lap_time = f"<b style='color:#04d361;'>{lap['lap_time']}</b> (Feita por {lap['driver']})"
                break
        
        safety_score = 75
        pace_score = 65
        notes = []

        try:
            preload = setup_data.get("advancedSetup", {}).get("drivetrain", {}).get("preload")
            if preload is not None:
                if preload < 60:
                    safety_score -= 10
                    pace_score += 10
                    notes.append(f"<b>Diferencial (Preload={preload}):</b> Baixo. Excelente para rotacionar o carro na tangencia (lift-off oversteer). Exige cuidado com a traseira.")
                elif preload > 120:
                    safety_score += 10
                    pace_score -= 10
                    notes.append(f"<b>Diferencial (Preload={preload}):</b> Alto. Traciona de forma estavel em saida de curvas, mas pode causar subesterco cronico.")
        except: pass

        try:
            mech = setup_data.get("basicSetup", {}).get("mechanicalBalance", {})
            arb_front = mech.get("aRBFront")
            arb_rear = mech.get("aRBRear")
            if arb_front is not None and arb_rear is not None:
                if arb_front > arb_rear + 2:
                    safety_score += 5
                    notes.append(f"<b>Barras (ARB F:{arb_front} R:{arb_rear}):</b> Dianteira predominante. Evita rodar facil em curvas rapidas, a custo de perder o apex.")
                elif arb_rear > arb_front:
                    safety_score -= 15
                    pace_score += 15
                    notes.append(f"<b>Barras (ARB F:{arb_front} R:{arb_rear}):</b> Traseira rigida. Setup bastante agressivo mecanicamente, permitindo curvas de baixa velozes, mas instavel em zebras.")
        except: pass

        try:
            aero = setup_data.get("advancedSetup", {}).get("aero", {})
            ride_height = aero.get("rideHeight", [])
            if len(ride_height) == 4:
                front_avg = (ride_height[0] + ride_height[1]) / 2
                rear_avg = (ride_height[2] + ride_height[3]) / 2
                rake = rear_avg - front_avg
                if rake > 18:
                    safety_score -= 10
                    pace_score += 10
                    notes.append(f"<b>Aerodinamica (Rake={rake}mm):</b> Rake agressivo (Traseira alta). Direciona todo o downforce pro bico do carro. Pode ser escorregadio na traseira.")
                elif rake < 8:
                    safety_score += 5
                    pace_score -= 5
                    notes.append(f"<b>Aerodinamica (Rake={rake}mm):</b> Rake conservador. Carro tendera ao equilibrio aerodinamico neutro.")
        except: pass

        try:
            bbias = setup_data.get("basicSetup", {}).get("alignment", {}).get("brakeBias", None)
            if bbias is not None:
                if float(bbias) < 54.0:
                    safety_score -= 10
                    pace_score += 10
                    notes.append(f"<b>Brake Bias ({bbias}%):</b> Tendencia forte para a traseira. Ajuda na agilidade de Trail Braking no Apex, mas perigoso em reducoes longas.")
        except: pass

        try:
            camber = setup_data.get("basicSetup", {}).get("alignment", {}).get("camber", [])
            if len(camber) == 4 and camber[0] > -2.5:
                safety_score -= 5
                pace_score -= 10
                notes.append(f"<b>Camber Dianteiro ({camber[0]}):</b> Lembrete: A meta atual do ACC e usar o camber negativo no maximo permitido pelo carro para maior contato lateral.")
        except: pass
        
        try:
            pads = setup_data.get("basicSetup", {}).get("strategy", {}).get("frontBrakePadCompound")
            if pads == 0:
                notes.append(f"<b>Freios (Pad 1):</b> Uso exclusivo para Qualy/Sprint (-30min). Podem falhar em corridas longas.")
            elif pads == 2:
                notes.append(f"<b>Freios (Pad 3):</b> Pastilhas seguras para Chuva ou longa duracao.")
        except: pass

        safety_score = max(0, min(100, safety_score))
        pace_score = max(0, min(100, pace_score))

        html = f"<h3>Engenheiro Virtual de Setups</h3>"
        html += f"<p><b>Referencia (MoTeC):</b> {best_lap_time}</p><hr>"
        
        safe_color = "#04d361" if safety_score >= 70 else ("#e1e1e6" if safety_score >= 50 else "#ff3b30")
        pace_color = "#04d361" if pace_score >= 70 else ("#e1e1e6" if pace_score >= 50 else "#ff3b30")
        
        html += f"<p><b>Seguranca e Estabilidade (Rating SA/CC):</b> <span style='color:{safe_color}; font-weight:bold;'>{safety_score}/100</span><br>"
        html += f"<b>Agressividade e Pace:</b> <span style='color:{pace_color}; font-weight:bold;'>{pace_score}/100</span></p><hr>"
        
        html += "<h4>Diagnostico Tecnico:</h4><ul>"
        for n in notes:
            html += f"<li>{n}</li><br>"
        
        if not notes:
            html += "<li>Setup equilibrado, padrao para corridas gerais.</li>"
            
        html += "</ul>"

        self.setup_advisor.setHtml(html)

    def copy_setup_analysis(self):
        if hasattr(self, "setup_advisor"):
            QApplication.clipboard().setText(self.setup_advisor.toPlainText())
            QMessageBox.information(self, "Copiado", "Analise e dicas copiadas para a area de transferencia!")

    def open_setups_directory(self):
        if os.path.exists(self.setup_mgr.setups_folder): os.startfile(self.setup_mgr.setups_folder)

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setStyleSheet(DARK_STYLE)
        window = ACCManagerApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print("\n--- ERRO AO EXECUTAR ---")
        traceback.print_exc()
        input("\nPressione ENTER para fechar...")