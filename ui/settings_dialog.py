"""
Tela de Configuracoes
========================

Janela pop-up (QDialog) pra preencher o .env sem precisar abrir um editor
de texto - pensada especialmente pra quem vai rodar o .exe empacotado
(PyInstaller), que nao necessariamente tem Python/editor a mao.

Ao salvar, chama config.save_env() (grava o .env) e config.reload_env()
(atualiza as constantes em memoria), e o main_window.py reconstroi os
servicos (ServerController, MotecParser, etc.) na hora - sem precisar
fechar e abrir o app de novo.
"""

import requests
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QLabel, QFileDialog, QDialogButtonBox, QMessageBox, QGroupBox
)

import config


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuracoes")
        self.resize(560, 420)

        layout = QVBoxLayout(self)

        paths_box = QGroupBox("Pastas do ACC")
        paths_form = QFormLayout()

        self.input_server_path = self._path_row(paths_form, "Servidor Dedicado (accServer.exe)")
        self.input_motec_path = self._path_row(paths_form, "Pasta do MoTeC")
        self.input_setups_path = self._path_row(paths_form, "Pasta de Setups")

        paths_box.setLayout(paths_form)
        layout.addWidget(paths_box)

        integrations_box = QGroupBox("Integracoes (opcionais)")
        integ_form = QFormLayout()

        self.input_supabase_url = QLineEdit()
        self.input_supabase_url.setPlaceholderText("https://seuprojeto.supabase.co")
        integ_form.addRow("Supabase URL:", self.input_supabase_url)

        self.input_supabase_key = QLineEdit()
        self.input_supabase_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_supabase_key.setPlaceholderText("chave anon public")
        integ_form.addRow("Supabase Key:", self.input_supabase_key)

        discord_row = QHBoxLayout()
        self.input_discord_webhook = QLineEdit()
        self.input_discord_webhook.setPlaceholderText("https://discord.com/api/webhooks/...")
        discord_row.addWidget(self.input_discord_webhook)
        btn_test_discord = QPushButton("Testar")
        btn_test_discord.clicked.connect(self.test_discord_webhook)
        discord_row.addWidget(btn_test_discord)
        integ_form.addRow("Discord Webhook:", discord_row)

        integrations_box.setLayout(integ_form)
        layout.addWidget(integrations_box)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Salvar")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        buttons.accepted.connect(self.save_and_close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._load_current_values()

    def _path_row(self, form: QFormLayout, label: str) -> QLineEdit:
        row = QHBoxLayout()
        field = QLineEdit()
        row.addWidget(field)
        btn = QPushButton("Procurar...")
        btn.clicked.connect(lambda: self._browse_folder(field))
        row.addWidget(btn)
        form.addRow(f"{label}:", row)
        return field

    def _browse_folder(self, field: QLineEdit):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta", field.text() or "")
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

    def test_discord_webhook(self):
        url = self.input_discord_webhook.text().strip()
        if not url:
            self.status_label.setText("Preencha a URL do webhook antes de testar.")
            self.status_label.setStyleSheet("color: #ff4b3e;")
            return
        try:
            resp = requests.post(url, json={"content": "🔧 Teste de configuracao do ACC Manager - webhook funcionando!"}, timeout=8)
            if resp.status_code in (200, 204):
                self.status_label.setText("Mensagem enviada! Confira o canal do Discord.")
                self.status_label.setStyleSheet("color: #04d361;")
            else:
                self.status_label.setText(f"Discord respondeu {resp.status_code}: {resp.text[:150]}")
                self.status_label.setStyleSheet("color: #ff4b3e;")
        except Exception as e:
            self.status_label.setText(f"Falha ao conectar: {e}")
            self.status_label.setStyleSheet("color: #ff4b3e;")

    def save_and_close(self):
        config.save_env({
            "ACC_SERVER_PATH": self.input_server_path.text().strip(),
            "ACC_MOTEC_PATH": self.input_motec_path.text().strip(),
            "ACC_SETUPS_PATH": self.input_setups_path.text().strip(),
            "SUPABASE_URL": self.input_supabase_url.text().strip(),
            "SUPABASE_KEY": self.input_supabase_key.text().strip(),
            "DISCORD_WEBHOOK_URL": self.input_discord_webhook.text().strip(),
        })
        config.reload_env()
        self.accept()
