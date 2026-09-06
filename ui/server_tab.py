"""
Aba 1: Servidor
==================
Cria a UI da aba de Servidor LAN e os handlers de iniciar/parar o
accServer.exe, alem da pre-visualizacao da imagem da pista escolhida.

E um Mixin: nao funciona sozinho, so faz sentido junto de ACCManagerApp
(ver ui/main_window.py), que fornece self.server, self.discord, os widgets
de outras abas etc. Mixins deixam cada arquivo pequeno e focado, sem mudar
o comportamento de nada em relacao ao main.py monolitico original.
"""

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
    QLineEdit, QSpinBox, QDoubleSpinBox, QMessageBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont

from config import (
    TRACKS_DATABASE, CAR_NAMES_MAPPING, ASSETS_DIR, SUPPORTED_IMAGE_EXTENSIONS
)
from ui.i18n import t


class ServerTabMixin:

    def create_server_tab(self):
        tab = QWidget()
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        box_general = QGroupBox(t("box_general_title"))
        gen_layout = QVBoxLayout()
        gen_layout.addWidget(QLabel(t("label_server_name")))
        self.input_name = QLineEdit("LAN Radmin Session")
        gen_layout.addWidget(self.input_name)
        gen_layout.addWidget(QLabel(t("label_password")))
        self.input_pass = QLineEdit()
        gen_layout.addWidget(self.input_pass)
        gen_layout.addWidget(QLabel(t("label_select_track")))
        self.combo_track = QComboBox()
        for track_id, track_display in TRACKS_DATABASE.items():
            self.combo_track.addItem(track_display, track_id)
        self.combo_track.currentIndexChanged.connect(self.update_track_preview)
        gen_layout.addWidget(self.combo_track)
        box_general.setLayout(gen_layout)
        left_layout.addWidget(box_general)

        sessions_weather_layout = QHBoxLayout()
        box_sessions = QGroupBox(t("box_sessions_title"))
        sess_layout = QVBoxLayout()

        lbl_q = QHBoxLayout(); lbl_q.addWidget(QLabel(t("label_qualy")))
        self.spin_q = QSpinBox(); self.spin_q.setRange(5, 180); self.spin_q.setValue(15)
        lbl_q.addWidget(self.spin_q); sess_layout.addLayout(lbl_q)

        lbl_r = QHBoxLayout(); lbl_r.addWidget(QLabel(t("label_race")))
        self.spin_r = QSpinBox(); self.spin_r.setRange(5, 360); self.spin_r.setValue(20)
        lbl_r.addWidget(self.spin_r); sess_layout.addLayout(lbl_r)

        lbl_h = QHBoxLayout(); lbl_h.addWidget(QLabel(t("label_race_hour")))
        self.spin_hour = QSpinBox(); self.spin_hour.setRange(0, 23); self.spin_hour.setValue(14)
        lbl_h.addWidget(self.spin_hour); sess_layout.addLayout(lbl_h)

        box_sessions.setLayout(sess_layout)
        sessions_weather_layout.addWidget(box_sessions)

        box_weather = QGroupBox(t("box_weather_title"))
        weather_layout = QVBoxLayout()

        lbl_temp = QHBoxLayout(); lbl_temp.addWidget(QLabel(t("label_temperature")))
        self.spin_temp = QSpinBox(); self.spin_temp.setRange(10, 40); self.spin_temp.setValue(22)
        lbl_temp.addWidget(self.spin_temp); weather_layout.addLayout(lbl_temp)

        lbl_cloud = QHBoxLayout(); lbl_cloud.addWidget(QLabel(t("label_clouds")))
        self.spin_cloud = QDoubleSpinBox(); self.spin_cloud.setRange(0.0, 1.0); self.spin_cloud.setSingleStep(0.1); self.spin_cloud.setValue(0.1)
        lbl_cloud.addWidget(self.spin_cloud); weather_layout.addLayout(lbl_cloud)

        lbl_rain = QHBoxLayout(); lbl_rain.addWidget(QLabel(t("label_rain")))
        self.spin_rain = QDoubleSpinBox(); self.spin_rain.setRange(0.0, 1.0); self.spin_rain.setSingleStep(0.1); self.spin_rain.setValue(0.0)
        lbl_rain.addWidget(self.spin_rain); weather_layout.addLayout(lbl_rain)

        lbl_rnd = QHBoxLayout(); lbl_rnd.addWidget(QLabel(t("label_randomness")))
        self.spin_random = QSpinBox(); self.spin_random.setRange(0, 7); self.spin_random.setValue(1)
        lbl_rnd.addWidget(self.spin_random); weather_layout.addLayout(lbl_rnd)

        box_weather.setLayout(weather_layout)
        sessions_weather_layout.addWidget(box_weather)
        left_layout.addLayout(sessions_weather_layout)

        box_rules = QGroupBox(t("box_rules_title"))
        rules_layout = QVBoxLayout()
        slots_rating_layout = QHBoxLayout()
        slots_rating_layout.addWidget(QLabel(t("label_slots")))
        self.spin_slots = QSpinBox(); self.spin_slots.setRange(1, 30); self.spin_slots.setValue(30)
        slots_rating_layout.addWidget(self.spin_slots)
        slots_rating_layout.addWidget(QLabel(t("label_tm")))
        self.spin_track_medal = QSpinBox(); self.spin_track_medal.setRange(0, 3); self.spin_track_medal.setValue(0)
        slots_rating_layout.addWidget(self.spin_track_medal)
        slots_rating_layout.addWidget(QLabel(t("label_sa")))
        self.spin_safety = QSpinBox(); self.spin_safety.setRange(0, 99); self.spin_safety.setValue(0)
        slots_rating_layout.addWidget(self.spin_safety)
        rules_layout.addLayout(slots_rating_layout)

        self.chk_register_to_lobby = QCheckBox(t("chk_lobby"))
        rules_layout.addWidget(self.chk_register_to_lobby)
        self.chk_reset_current = QCheckBox(t("chk_reset"))
        self.chk_reset_current.setChecked(True)
        rules_layout.addWidget(self.chk_reset_current)
        box_rules.setLayout(rules_layout)
        left_layout.addWidget(box_rules)

        buttons_layout = QHBoxLayout()
        self.btn_save = QPushButton(t("btn_save_settings"))
        self.btn_save.clicked.connect(self.save_ui_settings)
        buttons_layout.addWidget(self.btn_save)
        self.btn_start = QPushButton(t("btn_start_server"))
        self.btn_start.setObjectName("btn_start")
        self.btn_start.clicked.connect(self.handle_start_server)
        buttons_layout.addWidget(self.btn_start)
        left_layout.addLayout(buttons_layout)
        self.btn_reset = QPushButton(t("btn_stop_server"))
        self.btn_reset.setObjectName("btn_reset")
        self.btn_reset.clicked.connect(self.handle_reset_server)
        left_layout.addWidget(self.btn_reset)
        left_layout.addStretch()
        main_layout.addLayout(left_layout, stretch=1)

        right_layout = QVBoxLayout()
        box_preview = QGroupBox(t("box_circuit_title"))
        preview_layout = QVBoxLayout()
        self.track_img_label = ResizableImageLabel()
        self.track_img_label.setStyleSheet("background-color: #09090a; border: 1px dashed #323238; border-radius: 6px;")
        self.track_title_label = QLabel()
        self.track_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.track_title_label.setStyleSheet("color: #ff3b30; margin-top: 8px; font-size: 13pt; font-weight: bold;")
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
                        self, t("public_server_warning_title"),
                        t("public_server_warning_message"),
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
            QMessageBox.information(self, t("server_start_success_title"), t("server_start_success_message", track=track_id.upper()))
            self.discord.notify_server_started(
                server_name=self.input_name.text() or "Servidor LAN",
                track_display=TRACKS_DATABASE.get(track_id, track_id),
                slots=max_slots,
            )
        except Exception as e:
            QMessageBox.critical(self, t("server_start_error_title"), str(e))

    def handle_reset_server(self):
        try:
            self.server.stop_server()
            QMessageBox.information(self, t("server_closed_title"), t("server_closed_message"))
            self.discord.notify_server_stopped(server_name=self.input_name.text() or "Servidor LAN")
        except Exception as e:
            QMessageBox.critical(self, t("server_stop_error_title"), str(e))

    def update_track_preview(self):
        track_id = self.combo_track.currentData()
        self.track_title_label.setText(self.combo_track.currentText().upper())
        img_path = self._find_track_image(track_id)
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                self.track_img_label.setPixmap(pixmap)
                return
        self.track_img_label.setPixmap(QPixmap())
        self.track_img_label.setText(t("no_track_image", track=track_id))

    def _find_track_image(self, track_id):
        if not track_id: return None
        for ext in SUPPORTED_IMAGE_EXTENSIONS:
            cand = os.path.join(ASSETS_DIR, f"{track_id}{ext}")
            if os.path.exists(cand): return cand

            # Adiciona busca em "pistas" caso o usuario tenha colocado lá
            cand2 = os.path.join(ASSETS_DIR, "pistas", f"{track_id}{ext}")
            if os.path.exists(cand2): return cand2
        return None
class ResizableImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 150)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pixmap = None

    def setPixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap
        if pixmap and not pixmap.isNull():
            self.update_image()
        else:
            super().clear()

    def update_image(self):
        if self._pixmap and not self._pixmap.isNull():
            scaled_pixmap = self._pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            super().setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        if self._pixmap and not self._pixmap.isNull():
            self.update_image()
        super().resizeEvent(event)
    # ==========================
    # METODOS MOTEC E TELEMETRIA
    # ==========================
