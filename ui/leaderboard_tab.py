"""
Aba 4: Ranking dos Amigos
============================
Envia seus melhores tempos (lidos do MoTeC) para o Supabase compartilhado
(ver core/leaderboard_client.py) e mostra o ranking do grupo. Dispara
notificacao no Discord quando um tempo enviado bate o recorde do grupo.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox
)

from config import TRACKS_DATABASE, CAR_NAMES_MAPPING
from ui.i18n import ui, t


class LeaderboardTabMixin:

    def create_leaderboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        config_box = QGroupBox(ui("Sua Identidade"))
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel(ui("Seu nome de piloto:")))
        self.input_driver_name = QLineEdit()
        self.input_driver_name.setPlaceholderText("Ex: Joao Silva")
        self.input_driver_name.editingFinished.connect(lambda: self.save_ui_settings(silent=True))
        config_layout.addWidget(self.input_driver_name, stretch=1)

        status_text = t("leaderboard_status_connected") if self.leaderboard.enabled else t("leaderboard_status_disconnected")
        status_color = "#04d361" if self.leaderboard.enabled else "#ff4b3e"
        self.leaderboard_status_label = QLabel(status_text)
        self.leaderboard_status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        config_layout.addWidget(self.leaderboard_status_label)

        discord_text = t("discord_status_connected") if self.discord.enabled else t("discord_status_disconnected")
        discord_color = "#04d361" if self.discord.enabled else "#a8a8b3"
        self.discord_status_label = QLabel(discord_text)
        self.discord_status_label.setStyleSheet(f"color: {discord_color}; font-weight: bold;")
        config_layout.addWidget(self.discord_status_label)
        config_box.setLayout(config_layout)
        layout.addWidget(config_box)

        top_bar = QHBoxLayout()
        btn_refresh_lb = QPushButton(ui("Atualizar Ranking"))
        btn_refresh_lb.clicked.connect(self.refresh_leaderboard_table)
        top_bar.addWidget(btn_refresh_lb)

        btn_submit_lb = QPushButton(ui("Enviar Meus Melhores Tempos (MoTeC)"))
        btn_submit_lb.setStyleSheet("background-color: #04d361; color: #000;")
        btn_submit_lb.clicked.connect(self.submit_my_best_laps)
        top_bar.addWidget(btn_submit_lb)

        self.lb_car_filter = QComboBox()
        self.lb_car_filter.addItem(ui("Todos os carros"), None)
        for car_display in sorted(set(CAR_NAMES_MAPPING.values())):
            self.lb_car_filter.addItem(car_display, car_display)
        self.lb_car_filter.currentIndexChanged.connect(self.refresh_leaderboard_table)
        top_bar.addWidget(QLabel(ui("Carro:")))
        top_bar.addWidget(self.lb_car_filter)

        self.lb_track_filter = QComboBox()
        self.lb_track_filter.addItem(ui("Todas as pistas"), None)
        for track_id, track_display in TRACKS_DATABASE.items():
            self.lb_track_filter.addItem(track_display, track_id)
        self.lb_track_filter.currentIndexChanged.connect(self.refresh_leaderboard_table)
        top_bar.addWidget(QLabel(ui("Pista:")))
        top_bar.addWidget(self.lb_track_filter)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        self.table_leaderboard = QTableWidget(0, 6)
        self.table_leaderboard.setHorizontalHeaderLabels(
            ["#", ui("Piloto"), ui("Carro"), ui("Pista"), ui("Melhor Volta"), ui("Enviado em")]
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
            QMessageBox.warning(self, ui("Ranking nao configurado"),
                                 "Defina SUPABASE_URL e SUPABASE_KEY no arquivo .env para usar o ranking compartilhado.\n"
                                 "Veja as instrucoes em core/leaderboard_client.py.")
            return

        driver_name = self.input_driver_name.text().strip()
        if not driver_name:
            QMessageBox.warning(self, ui("Aviso"), ui("Preencha seu nome de piloto antes de enviar."))
            return

        laps = self.motec.get_best_laps()
        if not laps:
            QMessageBox.information(self, ui("Sem dados"), ui("Nenhuma volta encontrada na pasta do MoTeC."))
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
        QMessageBox.information(self, ui("Envio concluido"),
                                 f"{sent} tempo(s) enviado(s) com sucesso.\n{failed} falha(s).")

    def refresh_leaderboard_table(self):
        if not self.leaderboard.enabled:
            return
        car_id = self.lb_car_filter.currentData()
        track_id = self.lb_track_filter.currentData()
        try:
            rows = self.leaderboard.fetch_raw(track_id=track_id, car_id=car_id)
        except Exception as e:
            QMessageBox.critical(self, ui("Erro ao buscar ranking"), str(e))
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
