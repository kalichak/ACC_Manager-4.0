"""
Aba 2: Telemetria (MoTeC)
============================
Lista as sessoes gravadas pelo MoTeC, mostra detalhes de uma sessao e
gera o relatorio de Telemetria Avancada (.ld binario, ver
core/ld_telemetry_parser.py).
"""

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap

from core import ld_telemetry_parser
from ui.server_tab import ResizableImageLabel
from ui.i18n import ui

class TelemetryTabMixin:

    def create_telemetry_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        btn_refresh = QPushButton(ui("Recarregar Tempos MoTeC"))
        btn_refresh.clicked.connect(self.refresh_motec_table)
        top_bar.addWidget(btn_refresh)

        btn_del_motec = QPushButton(ui("Deletar Sessao Selecionada"))
        btn_del_motec.setObjectName("btn_delete")
        btn_del_motec.clicked.connect(self.handle_delete_motec)
        top_bar.addWidget(btn_del_motec)

        btn_advanced = QPushButton(ui("Telemetria Avancada (.ld)"))
        btn_advanced.setStyleSheet("background-color: #007aff; color: #fff;")
        btn_advanced.clicked.connect(self.show_advanced_telemetry)
        top_bar.addWidget(btn_advanced)

        self.motec_car_filter = QComboBox()
        self.motec_car_filter.addItem(ui("Todos os carros"))
        self.motec_car_filter.currentIndexChanged.connect(self.refresh_motec_table)
        top_bar.addWidget(QLabel(ui("Carro:")))
        top_bar.addWidget(self.motec_car_filter)
        self.motec_track_filter = QComboBox()
        self.motec_track_filter.addItem(ui("Todas as pistas"))
        self.motec_track_filter.currentIndexChanged.connect(self.refresh_motec_table)
        top_bar.addWidget(QLabel(ui("Pista:")))
        top_bar.addWidget(self.motec_track_filter)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.table_motec = QTableWidget(0, 6)
        self.table_motec.setHorizontalHeaderLabels([ui("Pista"), ui("Piloto"), ui("Carro"), ui("Melhor Volta"), ui("Score"), ui("Data")])
        self.table_motec.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_motec.itemSelectionChanged.connect(self.show_selected_motec_details)
        splitter.addWidget(self.table_motec)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)

        self.motec_img_label = ResizableImageLabel()
        self.motec_img_label.setStyleSheet("background-color: #09090a; border: 1px dashed #323238; border-radius: 6px;")
        right_layout.addWidget(self.motec_img_label)

        self.motec_details = QTextEdit()
        self.motec_details.setReadOnly(True)
        self.motec_details.setStyleSheet("background-color: #09090a; border: 1px solid #323238; border-radius: 6px; padding: 10px; font-size: 13px;")
        self.motec_details.setHtml(f"<p>{ui('Selecione uma volta para visualizar os detalhes da sessao.')}</p>")
        right_layout.addWidget(self.motec_details)

        splitter.addWidget(right_panel)
        splitter.setSizes([600, 400])
        layout.addWidget(splitter)

        tab.setLayout(layout)
        return tab

    # ==========================
    # ABA 3: SETUPS E ANALISE
    # ==========================
    def refresh_motec_filters(self):
        laps = self.motec.get_best_laps()
        self.motec_car_filter.blockSignals(True)
        self.motec_car_filter.clear(); self.motec_car_filter.addItem(ui("Todos os carros"))
        for car in sorted({lap["car"] for lap in laps}): self.motec_car_filter.addItem(car)
        self.motec_car_filter.blockSignals(False)

        self.motec_track_filter.blockSignals(True)
        self.motec_track_filter.clear(); self.motec_track_filter.addItem(ui("Todas as pistas"))
        for track in sorted({lap["track"] for lap in laps}): self.motec_track_filter.addItem(track)
        self.motec_track_filter.blockSignals(False)

    def refresh_motec_table(self):
        laps = self.motec.get_best_laps()
        c_val = self.motec_car_filter.currentText()
        t_val = self.motec_track_filter.currentText()
        if c_val != ui("Todos os carros"): laps = [l for l in laps if l["car"] == c_val]
        if t_val != ui("Todas as pistas"): laps = [l for l in laps if l["track"] == t_val]

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
            QMessageBox.warning(self, ui("Aviso"), ui("Selecione uma sessao na tabela primeiro."))
            return

        row = self.table_motec.currentRow()
        lap = self.table_motec.item(row, 0).data(Qt.ItemDataRole.UserRole)
        ldx_path = lap.get("file_path")
        ld_path = ld_telemetry_parser.get_ld_path(ldx_path) if ldx_path else None

        if not ld_path or not os.path.exists(ld_path):
            QMessageBox.warning(self, ui("Arquivo .ld nao encontrado"),
                                 f"Nao encontrei o arquivo binario de telemetria ao lado do .ldx:\n{ld_path}\n\n"
                                 "Ele e gerado automaticamente pelo ACC junto com o .ldx - confira se nao foi movido/apagado.")
            return

        try:
            analysis = ld_telemetry_parser.analyze_session(ld_path, ldx_path)
        except Exception as e:
            QMessageBox.critical(self, ui("Erro ao ler telemetria"), str(e))
            return

        laps = analysis["laps"]
        if not laps:
            QMessageBox.information(self, ui("Sem dados"), ui("Nao foi possivel extrair voltas dessa sessao."))
            return

        # Ordena pelas voltas mais rapidas primeiro pra facilitar comparacao
        laps_sorted = sorted(laps, key=lambda l: l["lap_time_s"])

        html = f"<h3>{ui('Telemetria Avancada: {track}', track=lap['track'])}</h3>"
        html += f"<p style='color:#a8a8b3;'>{ui('Extraido diretamente do arquivo binario .ld (nao e estimativa) - {laps} volta(s) detectada(s), {channels} canais disponiveis.', laps=len(laps), channels=len(analysis['channels_available']))}</p><hr>"
        html += "<table cellspacing='6' style='width:100%; font-size:12px;'>"
        html += (f"<tr style='color:#a8a8b3;'><th align='left'>{ui('Volta')}</th><th>{ui('Tempo')}</th><th>{ui('Vel.Max')}</th>"
             f"<th>{ui('%Full Throttle')}</th><th>{ui('Freadas Fortes')}</th><th>{ui('Lat. G (p99)')}</th><th>{ui('Freio G (p99)')}</th>"
             f"<th>{ui('Temp.Pneu')}</th><th>{ui('Temp.Freio')}</th></tr>")
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
        html += (f"<p style='color:#a8a8b3; font-size:12px;'>{ui('Freadas fortes = numero de vezes que o freio passou de {threshold}% na volta. Lat./Freio G no percentil 99 (evita que um unico pico de zebra/impacto distorca o numero). Use isso pra comparar seu estilo de pilotagem entre voltas ou pra calibrar a base de pistas com dados reais (botao na aba de Setups).', threshold=f'{ld_telemetry_parser.HARD_BRAKE_THRESHOLD_PCT:.0f}')}</p>")

        self.motec_details.setHtml(html)

    def show_selected_motec_details(self):
        if not self.table_motec.selectedItems(): return
        row = self.table_motec.currentRow()
        lap = self.table_motec.item(row, 0).data(Qt.ItemDataRole.UserRole)

        track_id = lap.get("track_id")
        img_path = self._find_track_image(track_id)
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            self.motec_img_label.setPixmap(pixmap)
        else:
            self.motec_img_label.setPixmap(QPixmap())
            self.motec_img_label.setText(f"[{ui('Sem imagem para {track}', track=track_id)}]")

        total_laps = lap.get("total_laps", 0)
        session_t = lap.get("session_type", "N/A")
        t_temp = lap.get("track_temp", "N/A")
        a_temp = lap.get("ambient_temp", "N/A")
        v_weight = lap.get("vehicle_weight", "N/A")

        if not lap.get("is_valid", True):
            glitch_message = ui(
                "O tempo de {lap_time} em {track} e fisicamente impossivel para um "
                "carro classe GT3.\nA sessao foi invalidada pelo sistema e recebeu "
                "Score 0/10.",
                lap_time=lap["lap_time"],
                track=lap["track"],
            ).replace("\n", "<br>")
            html = f"""
            <h3 style="color:#ff3b30;">{ui('ALERTA DE TEMPO IRREAL (GLITCH)')}</h3>
            <p>{glitch_message}</p>
            """
            self.motec_details.setHtml(html)
            return

        cn_impact = ui("Baixo (Sessao curta ou inconsistente)")
        if total_laps >= 5: cn_impact = ui("Moderado (Sessao util para ganhar pontos iniciais de CN)")
        if total_laps >= 10: cn_impact = ui("Alto (Sessao excelente para fixar Rating de Consistencia)")

        html = f"""
        <h3>{ui('Telemetria MoTeC: {track}', track=lap['track'])}</h3>
        <p><b>{ui('Piloto:')}</b> {lap['driver']}<br>
        <b>{ui('Carro:')}</b> {lap['car']}<br>
        <b>{ui('Tipo de Sessao:')}</b> {session_t}<br>
        <b>{ui('Condicoes Climaticas:')}</b> Air {a_temp}C | Track {t_temp}C<br>
        <b>{ui('Data do Arquivo:')}</b> {lap['date']}</p>
        <hr>
        <p><b>{ui('Voltas Completadas:')}</b> {total_laps}<br>
        <b>{ui('Melhor Tempo:')}</b> <span style='color:#04d361; font-weight:bold;'>{lap['lap_time']}</span><br>
        <b>{ui('Score da Sessao:')}</b> {lap.get('score', 0)} / 10</p>
        <hr>
        <h4>{ui('Analise Tecnica e Velocidade de Apex:')}</h4>
        <p style='color:#a8a8b3;'>{ui('A extracao detalhada de Apex (VMin), Forca G, e Tracao exigem a leitura de arquivos binarios (.ld). Para inspecionar esses dados vitais para seu pace, carregue o arquivo de telemetria diretamente no MoTeC i2 Pro usando o Workspace oficial do ACC.')}</p>
        <hr>
        <h4>{ui('Efeito no seu Rating (ACC):')}</h4>
        <ul>
            <li><b>{ui('Consistencia (CN):')}</b> {cn_impact}.</li>
            <li><b>{ui('Car Control (CC):')}</b> {ui('Lembre-se que derrapar alem do angulo ideal de slip (Overdriving) nesta sessao machuca sua pontuacao CC a cada curva.')}</li>
        </ul>
        """
        self.motec_details.setHtml(html)

    def handle_delete_motec(self):
        if not self.table_motec.selectedItems():
            QMessageBox.warning(self, ui("Aviso"), ui("Selecione uma sessao primeiro."))
            return
        row = self.table_motec.currentRow()
        lap = self.table_motec.item(row, 0).data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(self, ui("Confirmar Exclusao"), f"{ui('Deseja realmente apagar a sessao de {track} permanentemente?', track=lap['track'])}", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.motec.delete_telemetry(lap["file_path"])
                self.refresh_motec_table()
                self.motec_img_label.clear()
                self.motec_details.clear()
                QMessageBox.information(self, ui("Sucesso"), ui("Sessao excluida."))
            except Exception as e:
                QMessageBox.critical(self, ui("Erro"), str(e))

    # ==========================
    # METODOS DE SETUPS E PRESETS
    # ==========================
