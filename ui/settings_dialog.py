"""
Tela de Configuracoes
========================

Janela pop-up (QDialog) pra preencher o .env sem precisar abrir um editor
de texto - pensada especialmente pra quem vai rodar o .exe empacotado
(PyInstaller), que nao necessariamente tem Python/editor a mao.

Ao salvar, chama config.save_env() (grava o .env). Quem chama
config.reload_env() e reconstroi a janela principal (abas + servicos) e
o ACCManagerApp.apply_settings_changes() em ui/main_window.py - assim o
mesmo caminho e usado tanto ao salvar aqui quanto ao trocar o idioma
pelo combo do canto superior.

MODULOS (issue #4): a secao "Modulos ativos" abaixo grava a chave
ENABLED_MODULES no .env como uma string "server,telemetry,..." com os
modulos marcados. Se o usuario desmarcar tudo, o .env fica com
ENABLED_MODULES vazio - config._parse_enabled_modules trata isso caindo
de volta para "todos habilitados", entao o pior caso possivel e o app
nunca abrir sem nenhuma aba.
"""

import json

import requests
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QLabel, QFileDialog, QDialogButtonBox, QMessageBox, QGroupBox, QCheckBox, QComboBox,
    QTextEdit
)

import config
from core.version_manager import AppVersionManager
from ui.i18n import t


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("settings_dialog_title"))
        self.resize(560, 520)

        layout = QVBoxLayout(self)

        paths_box = QGroupBox(t("group_paths_title"))
        paths_form = QFormLayout()

        self.input_server_path = self._path_row(paths_form, t("label_server_path"))
        self.input_motec_path = self._path_row(paths_form, t("label_motec_path"))
        self.input_setups_path = self._path_row(paths_form, t("label_setups_path"))

        paths_box.setLayout(paths_form)
        layout.addWidget(paths_box)

        appearance_box = QGroupBox(t("group_appearance_title"))
        appearance_form = QFormLayout()
        self.combo_theme = QComboBox()
        self.combo_theme.addItem(t("theme_light"), "light")
        self.combo_theme.addItem(t("theme_dark"), "dark")
        appearance_form.addRow(t("label_theme"), self.combo_theme)
        appearance_box.setLayout(appearance_form)
        layout.addWidget(appearance_box)

        integrations_box = QGroupBox(t("group_integrations_title"))
        integ_form = QFormLayout()

        self.input_supabase_url = QLineEdit()
        self.input_supabase_url.setPlaceholderText("https://seuprojeto.supabase.co")
        integ_form.addRow(t("label_supabase_url"), self.input_supabase_url)

        self.input_supabase_key = QLineEdit()
        self.input_supabase_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_supabase_key.setPlaceholderText("anon public key")
        integ_form.addRow(t("label_supabase_key"), self.input_supabase_key)

        discord_row = QHBoxLayout()
        self.input_discord_webhook = QLineEdit()
        self.input_discord_webhook.setPlaceholderText("https://discord.com/api/webhooks/...")
        discord_row.addWidget(self.input_discord_webhook)
        btn_test_discord = QPushButton(t("btn_test_discord"))
        btn_test_discord.clicked.connect(self.test_discord_webhook)
        discord_row.addWidget(btn_test_discord)
        integ_form.addRow(t("label_discord_webhook"), discord_row)

        integrations_box.setLayout(integ_form)
        layout.addWidget(integrations_box)

        modules_box = QGroupBox(t("group_modules_title"))
        modules_layout = QVBoxLayout()
        hint = QLabel(t("modules_hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #a8a8b3; font-size: 9pt;")
        modules_layout.addWidget(hint)

        self.chk_module_server = QCheckBox(t("module_server"))
        self.chk_module_telemetry = QCheckBox(t("module_telemetry"))
        self.chk_module_setups = QCheckBox(t("module_setups"))
        self.chk_module_leaderboard = QCheckBox(t("module_leaderboard"))
        for chk in (self.chk_module_server, self.chk_module_telemetry,
                    self.chk_module_setups, self.chk_module_leaderboard):
            modules_layout.addWidget(chk)

        modules_box.setLayout(modules_layout)
        layout.addWidget(modules_box)

        version_box = QGroupBox(t("group_version_title"))
        version_layout = QVBoxLayout()

        self.version_status = QLabel(t("version_checking"))
        self.version_status.setWordWrap(True)
        version_layout.addWidget(self.version_status)

        self.version_details = QTextEdit()
        self.version_details.setReadOnly(True)
        self.version_details.setMaximumHeight(140)
        version_layout.addWidget(self.version_details)

        btn_refresh_version = QPushButton(t("btn_validate_version"))
        btn_refresh_version.clicked.connect(self.refresh_version_status)
        version_layout.addWidget(btn_refresh_version)

        version_box.setLayout(version_layout)
        layout.addWidget(version_box)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(t("btn_save"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(t("btn_cancel"))
        buttons.accepted.connect(self.save_and_close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._load_current_values()

    def _path_row(self, form: QFormLayout, label: str) -> QLineEdit:
        row = QHBoxLayout()
        field = QLineEdit()
        row.addWidget(field)
        btn = QPushButton(t("btn_browse"))
        btn.clicked.connect(lambda: self._browse_folder(field))
        row.addWidget(btn)
        form.addRow(f"{label}:", row)
        return field

    def _browse_folder(self, field: QLineEdit):
        folder = QFileDialog.getExistingDirectory(self, t("browse_dialog_title"), field.text() or "")
        if folder:
            field.setText(folder)

    def _load_current_values(self):
        env = config.load_or_create_env()
        self.input_server_path.setText(env.get("ACC_SERVER_PATH", ""))
        self.input_motec_path.setText(env.get("ACC_MOTEC_PATH", ""))
        self.input_setups_path.setText(env.get("ACC_SETUPS_PATH", ""))
        self.input_supabase_url.setText(env.get("SUPABASE_URL", ""))
        self.input_supabase_key.setText(env.get("SUPABASE_KEY", ""))
        self.input_discord_webhook.setText(env.get("DISCORD_WEBHOOK_URL", ""))
        theme_index = self.combo_theme.findData(env.get("APP_THEME", config.DEFAULT_THEME))
        self.combo_theme.setCurrentIndex(theme_index if theme_index >= 0 else 0)

        enabled = set(config._parse_enabled_modules(env.get("ENABLED_MODULES", "")))
        self.chk_module_server.setChecked("server" in enabled)
        self.chk_module_telemetry.setChecked("telemetry" in enabled)
        self.chk_module_setups.setChecked("setups" in enabled)
        self.chk_module_leaderboard.setChecked("leaderboard" in enabled)
        self.refresh_version_status()

    def test_discord_webhook(self):
        url = self.input_discord_webhook.text().strip()
        if not url:
            self.status_label.setText(t("discord_test_empty_url"))
            self.status_label.setStyleSheet("color: #ff4b3e;")
            return
        try:
            resp = requests.post(url, json={"content": t("discord_test_message_body")}, timeout=8)
            if resp.status_code in (200, 204):
                self.status_label.setText(t("discord_test_success"))
                self.status_label.setStyleSheet("color: #04d361;")
            else:
                self.status_label.setText(t("discord_test_bad_status", status=resp.status_code, body=resp.text[:150]))
                self.status_label.setStyleSheet("color: #ff4b3e;")
        except Exception as e:
            self.status_label.setText(t("discord_test_exception", error=e))
            self.status_label.setStyleSheet("color: #ff4b3e;")

    def refresh_version_status(self):
        manager = AppVersionManager()
        manifest = manager.validate_update()
        branch = manifest.get("branch", "unknown")
        current = manifest.get("current_version", "unknown")
        next_version = manifest.get("next_version", current)
        needs_update = manifest.get("needs_update", False)
        channel = manifest.get("channel", "development")

        if needs_update:
            self.version_status.setText(
                t("version_update_pending", current=current, next_version=next_version, channel=channel)
            )
            self.version_status.setStyleSheet("color: #f7b731;")
        else:
            self.version_status.setText(t("version_current", current=current, channel=channel))
            self.version_status.setStyleSheet("color: #04d361;")

        summary = {
            "branch": branch,
            "current_version": current,
            "next_version": next_version,
            "channel": channel,
            "needs_update": needs_update,
            "commit": manifest.get("commit", "unknown"),
            "changed_files": manifest.get("changed_files", []),
            "new_files": manifest.get("new_files", []),
        }
        self.version_details.setPlainText(json.dumps(summary, ensure_ascii=False, indent=2))

    def save_and_close(self):
        selected_modules = []
        if self.chk_module_server.isChecked():
            selected_modules.append("server")
        if self.chk_module_telemetry.isChecked():
            selected_modules.append("telemetry")
        if self.chk_module_setups.isChecked():
            selected_modules.append("setups")
        if self.chk_module_leaderboard.isChecked():
            selected_modules.append("leaderboard")

        config.save_env({
            "ACC_SERVER_PATH": self.input_server_path.text().strip(),
            "ACC_MOTEC_PATH": self.input_motec_path.text().strip(),
            "ACC_SETUPS_PATH": self.input_setups_path.text().strip(),
            "SUPABASE_URL": self.input_supabase_url.text().strip(),
            "SUPABASE_KEY": self.input_supabase_key.text().strip(),
            "DISCORD_WEBHOOK_URL": self.input_discord_webhook.text().strip(),
            "ENABLED_MODULES": ",".join(selected_modules),
            "APP_THEME": self.combo_theme.currentData(),
        })
        self.accept()
