"""
Janela Principal (ACCManagerApp)
====================================

Junta as 4 abas via heranca multipla de Mixins (um arquivo por aba, cada
um cuidando so da sua propria UI e handlers). Esse e o UNICO lugar que
"conhece" todas as abas ao mesmo tempo - por isso e tambem onde vive
save_ui_settings/load_ui_settings, que persistem campos de mais de uma aba
(ex.: nome do servidor da aba Servidor + nome de piloto da aba Ranking).

Por que Mixins e nao Signals/Slots entre widgets separados? Porque isso e um
refactor de ORGANIZACAO DE ARQUIVOS, nao uma reescrita de arquitetura: cada
metodo continua identico ao main.py original, so mudou de arquivo. Isso
deixa o risco de quebrar algo bem baixo. Se no futuro cada aba precisar
virar de fato independente (por exemplo, para reordenar/remover abas
dinamicamente), da pra evoluir os Mixins para QWidget proprios depois -
mas isso e um passo maior e nao foi necessario so para "arrumar a casa".
"""

import json
import os

from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QPushButton

import config
from config import (
    UI_SETTINGS_FILE, SERVER_PATH, DEFAULT_MOTEC_PATH, DEFAULT_SETUPS_PATH,
    SUPABASE_URL, SUPABASE_KEY, DISCORD_WEBHOOK_URL,
    ServerController, MotecParser, SetupManager, SetupCreator,
    LeaderboardClient, DiscordNotifier,
)
from ui.server_tab import ServerTabMixin
from ui.telemetry_tab import TelemetryTabMixin
from ui.setups_tab import SetupsTabMixin
from ui.leaderboard_tab import LeaderboardTabMixin
from ui.settings_dialog import SettingsDialog


class ACCManagerApp(QMainWindow, ServerTabMixin, TelemetryTabMixin, SetupsTabMixin, LeaderboardTabMixin):
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
            msg += "\n\nClique no botao '⚙ Configuracoes' (canto superior direito) para ajustar os caminhos."
            QMessageBox.warning(self, "Atencao - Configuracao Necessaria", msg)

    def init_ui(self):
        tabs = QTabWidget()
        tabs.addTab(self.create_server_tab(), "Servidor LAN / Radmin")
        tabs.addTab(self.create_telemetry_tab(), "Telemetria e Rating (MoTeC)")
        tabs.addTab(self.create_setups_tab(), "Gerenciador de Setups")
        tabs.addTab(self.create_leaderboard_tab(), "Ranking dos Amigos")

        btn_settings = QPushButton("⚙ Configuracoes")
        btn_settings.clicked.connect(self.open_settings_dialog)
        tabs.setCornerWidget(btn_settings)

        self.setCentralWidget(tabs)

    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.reload_services()
            QMessageBox.information(self, "Configuracoes salvas",
                                     "As novas configuracoes ja foram aplicadas - nao precisa reiniciar o programa.")

    def reload_services(self):
        """Reconstroi os servicos (servidor, MoTeC, setups, ranking, Discord)
        com os valores atualizados do .env, sem precisar fechar o app."""
        config.reload_env()
        self.server = ServerController(config.SERVER_PATH)
        self.motec = MotecParser(config.DEFAULT_MOTEC_PATH)
        self.setup_mgr = SetupManager(config.DEFAULT_SETUPS_PATH)
        self.leaderboard = LeaderboardClient(config.SUPABASE_URL, config.SUPABASE_KEY)
        self.discord = DiscordNotifier(config.DISCORD_WEBHOOK_URL)

        if hasattr(self, "leaderboard_status_label"):
            connected = self.leaderboard.enabled
            self.leaderboard_status_label.setText(f"Ranking: {'Conectado' if connected else 'Nao configurado'}")
            self.leaderboard_status_label.setStyleSheet(f"color: {'#04d361' if connected else '#ff4b3e'}; font-weight: bold;")
        if hasattr(self, "discord_status_label"):
            connected = self.discord.enabled
            self.discord_status_label.setText("Discord conectado" if connected else "Discord nao configurado")
            self.discord_status_label.setStyleSheet(f"color: {'#04d361' if connected else '#a8a8b3'}; font-weight: bold;")

        self.refresh_motec_filters()
        self.refresh_motec_table()
        self.refresh_setups_filters()
        self.refresh_setups_table()

    # ==========================
    # ABA 1: SERVIDOR
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
