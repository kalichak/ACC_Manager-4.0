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

MODULOS OPCIONAIS (issue #4)
-----------------------------
As 4 abas continuam SEMPRE importadas (nunca comente/apague os imports
dos Mixins abaixo - a classe ACCManagerApp herda deles e quebra se
sumirem). O que liga/desliga cada aba e a lista config.ENABLED_MODULES,
lida do .env (chave ENABLED_MODULES, editavel pela tela de
Configuracoes). init_ui() so chama create_xxx_tab() para os modulos
habilitados, e por isso os widgets daquele modulo (self.input_name,
self.spin_q etc.) so existem se a aba foi criada.

IMPORTANTE - por que usamos "modulo in self.enabled_modules" e NAO
hasattr(self, "input_name") pra checar se uma aba existe: depois que a
janela e reconstruida uma vez (troca de idioma ou de modulos), um
atributo Python como self.leaderboard_status_label continua existindo
mesmo que aquela aba tenha sido desabilitada - ele so aponta para um
QLabel cujo objeto C++ ja foi destruido quando setCentralWidget trocou
o QTabWidget antigo. hasattr() retorna True mesmo assim (o atributo
existe, so que "morto"), e usar esse widget da RuntimeError: "wrapped
C/C++ object has been deleted". self.enabled_modules e reatribuido do
zero em toda chamada de init_ui(), entao ele sempre reflete o que
existe de verdade nesta reconstrucao - por isso e a fonte da verdade
usada em save_ui_settings/load_ui_settings/reload_services, no lugar de
checar os widgets diretamente.

Trocar os modulos habilitados ou o idioma reconstroi a janela chamando
init_ui() de novo (self.setCentralWidget troca o QTabWidget inteiro) -
por isso funciona sem reiniciar o programa.
"""

import json
import os

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QPushButton, QWidget, QHBoxLayout,
    QComboBox, QLabel,
)
from PyQt6.QtCore import Qt

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
from ui.i18n import t, set_language, get_language, LANGUAGES


class ACCManagerApp(QMainWindow, ServerTabMixin, TelemetryTabMixin, SetupsTabMixin, LeaderboardTabMixin):
    def __init__(self):
        super().__init__()

        set_language(config.APP_LANGUAGE)

        self.server = ServerController(SERVER_PATH)
        self.motec = MotecParser(DEFAULT_MOTEC_PATH)
        self.setup_mgr = SetupManager(DEFAULT_SETUPS_PATH)
        self.setup_creator = SetupCreator()
        self.leaderboard = LeaderboardClient(SUPABASE_URL, SUPABASE_KEY)
        self.discord = DiscordNotifier(DISCORD_WEBHOOK_URL)

        self._current_setup_path = None
        self._current_setup_dict = None

        self.resize(1200, 850)

        self.init_ui()
        self.load_ui_settings()
        self.validate_paths()

        self.refresh_enabled_modules_data()

    def refresh_enabled_modules_data(self):
        """Atualiza as tabelas/filtros dos modulos que dependem de dados
        em disco (MoTeC e Setups) - so faz sentido chamar se a aba
        correspondente estiver habilitada e, portanto, existir."""
        if "telemetry" in self.enabled_modules:
            self.refresh_motec_filters()
            self.refresh_motec_table()
        if "setups" in self.enabled_modules:
            self.refresh_setups_filters()
            self.refresh_setups_table()

    def validate_paths(self):
        warnings = []
        if "server" in self.enabled_modules and not os.path.exists(SERVER_PATH):
            warnings.append(f"{t('path_label_server')}: {SERVER_PATH}")
        if "telemetry" in self.enabled_modules and not os.path.exists(DEFAULT_MOTEC_PATH):
            warnings.append(f"{t('path_label_motec')}: {DEFAULT_MOTEC_PATH}")
        if "setups" in self.enabled_modules and not os.path.exists(DEFAULT_SETUPS_PATH):
            warnings.append(f"{t('path_label_setups')}: {DEFAULT_SETUPS_PATH}")

        if warnings:
            msg = t("paths_warning_intro") + "\n\n"
            msg += "\n".join(warnings)
            msg += "\n\n" + t("paths_warning_footer")
            QMessageBox.warning(self, t("paths_warning_title"), msg)

    def init_ui(self):
        self.setWindowTitle(t("app_title"))

        tabs = QTabWidget()
        self.enabled_modules = set(config.ENABLED_MODULES)

        if "server" in self.enabled_modules:
            tabs.addTab(self.create_server_tab(), t("tab_server"))
        if "telemetry" in self.enabled_modules:
            tabs.addTab(self.create_telemetry_tab(), t("tab_telemetry"))
        if "setups" in self.enabled_modules:
            tabs.addTab(self.create_setups_tab(), t("tab_setups"))
        if "leaderboard" in self.enabled_modules:
            tabs.addTab(self.create_leaderboard_tab(), t("tab_leaderboard"))

        if tabs.count() == 0:
            placeholder = QLabel(t("no_modules_message"))
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tabs.addTab(placeholder, t("no_modules_tab_title"))

        tabs.setCornerWidget(self._build_corner_widget())

        self.setCentralWidget(tabs)

    def _build_corner_widget(self):
        """Widget no canto superior direito do QTabWidget: seletor de
        idioma + botao de Configuracoes (issue #4)."""
        corner = QWidget()
        corner_layout = QHBoxLayout(corner)
        corner_layout.setContentsMargins(0, 0, 8, 0)
        corner_layout.setSpacing(6)

        self.combo_language = QComboBox()
        for code, label in LANGUAGES.items():
            self.combo_language.addItem(label, code)
        idx = self.combo_language.findData(get_language())
        if idx >= 0:
            self.combo_language.setCurrentIndex(idx)
        self.combo_language.currentIndexChanged.connect(self.handle_language_changed)
        corner_layout.addWidget(self.combo_language)

        btn_settings = QPushButton(t("btn_settings"))
        btn_settings.clicked.connect(self.open_settings_dialog)
        corner_layout.addWidget(btn_settings)

        return corner

    def handle_language_changed(self):
        """Chamado quando o usuario troca o idioma no combo do canto.
        Persiste no .env, atualiza o dict global de traducao e
        reconstroi a janela (mesmo mecanismo usado ao salvar
        Configuracoes) para que todo texto ja renderizado seja atualizado
        sem precisar reiniciar o app."""
        lang = self.combo_language.currentData()
        if lang == get_language():
            return
        config.save_env({"APP_LANGUAGE": lang})
        self.apply_settings_changes()

    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.apply_settings_changes()
            QMessageBox.information(self, t("settings_saved_title"), t("settings_saved_message"))

    def apply_settings_changes(self):
        """Ponto unico chamado depois que .env muda (Configuracoes salvas
        OU idioma trocado no combo do canto). Reconstroi a janela do zero
        para refletir modulos habilitados/idioma, restaura os valores
        salvos e recria os servicos com os caminhos/chaves atuais -
        tudo sem fechar e abrir o programa de novo."""
        config.reload_env()
        set_language(config.APP_LANGUAGE)
        self.init_ui()
        self.load_ui_settings()
        self.reload_services()

    def reload_services(self):
        """Reconstroi os servicos (servidor, MoTeC, setups, ranking, Discord)
        com os valores atualizados do .env, sem precisar fechar o app."""
        self.server = ServerController(config.SERVER_PATH)
        self.motec = MotecParser(config.DEFAULT_MOTEC_PATH)
        self.setup_mgr = SetupManager(config.DEFAULT_SETUPS_PATH)
        self.leaderboard = LeaderboardClient(config.SUPABASE_URL, config.SUPABASE_KEY)
        self.discord = DiscordNotifier(config.DISCORD_WEBHOOK_URL)

        if "leaderboard" in self.enabled_modules:
            connected = self.leaderboard.enabled
            self.leaderboard_status_label.setText(
                t("leaderboard_status_connected") if connected else t("leaderboard_status_disconnected")
            )
            self.leaderboard_status_label.setStyleSheet(f"color: {'#04d361' if connected else '#ff4b3e'}; font-weight: bold;")
            connected = self.discord.enabled
            self.discord_status_label.setText(
                t("discord_status_connected") if connected else t("discord_status_disconnected")
            )
            self.discord_status_label.setStyleSheet(f"color: {'#04d361' if connected else '#a8a8b3'}; font-weight: bold;")

        self.refresh_enabled_modules_data()

    # ==========================
    # PERSISTENCIA DE CAMPOS DA UI (varias abas)
    # ==========================
    # Cada bloco abaixo so mexe nos widgets da sua propria aba, e so se
    # o modulo dela estiver em self.enabled_modules (nao usamos hasattr
    # aqui - ver docstring do topo do arquivo para o motivo). Se um
    # modulo estiver desabilitado, o valor anteriormente salvo pra ele e
    # preservado no arquivo (nao e apagado so porque a aba nao foi
    # recriada nesta sessao).

    def save_ui_settings(self, silent=False):
        settings = {}

        if "server" in self.enabled_modules:
            settings.update({
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
            })

        if "leaderboard" in self.enabled_modules:
            settings["driver_name"] = self.input_driver_name.text()

        # Preserva no arquivo os campos de modulos que nao existem nesta
        # sessao (desabilitados), em vez de sobrescrever o JSON inteiro.
        existing = {}
        if os.path.exists(UI_SETTINGS_FILE):
            try:
                with open(UI_SETTINGS_FILE, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = {}
        existing.update(settings)

        try:
            with open(UI_SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=4)
            if not silent:
                QMessageBox.information(self, t("ui_settings_save_success_title"), t("ui_settings_save_success_message"))
        except Exception as e:
            if not silent:
                QMessageBox.warning(self, t("ui_settings_save_error_title"), t("ui_settings_save_error_message", error=e))

    def load_ui_settings(self):
        if not os.path.exists(UI_SETTINGS_FILE):
            return
        try:
            with open(UI_SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception:
            return

        if "server" in self.enabled_modules:
            self.input_name.setText(settings.get("server_name", "LAN Radmin Session"))
            self.input_pass.setText(settings.get("password", ""))
            track = settings.get("track", "monza")
            idx = self.combo_track.findData(track)
            if idx >= 0:
                self.combo_track.setCurrentIndex(idx)
                #Configurações padrões ao inicializar o app.
            self.spin_q.setValue(settings.get("q_min", 10))
            self.spin_r.setValue(settings.get("r_min", 15))
            self.spin_hour.setValue(settings.get("hour", 14))
            self.spin_temp.setValue(settings.get("temp", 22))
            self.spin_cloud.setValue(settings.get("cloud", 0.1))
            self.spin_rain.setValue(settings.get("rain", 0.0))
            self.spin_random.setValue(settings.get("random", 1))
            self.spin_slots.setValue(settings.get("slots", 10))
            self.spin_track_medal.setValue(settings.get("tm", 0))
            self.spin_safety.setValue(settings.get("sa", 0))
            self.chk_register_to_lobby.setChecked(settings.get("lobby", False))
            self.chk_reset_current.setChecked(settings.get("reset", True))

        if "leaderboard" in self.enabled_modules:
            self.input_driver_name.setText(settings.get("driver_name", ""))
