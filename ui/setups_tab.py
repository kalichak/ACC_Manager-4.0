"""
Aba 3: Gerenciador de Setups
===============================
A maior aba do app: listar/filtrar setups salvos, editar campos na arvore,
clonar/replicar entre carro-pista, aplicar presets prontos (qualy/corrida/
chuva), o Criador de Setups Inteligente (ver core/setup_creator.py) e o
Engenheiro Virtual (analise comparando o setup com o melhor tempo do MoTeC).
"""

import json
import os

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QTreeWidget, QTreeWidgetItem, QSplitter, QSlider, QMessageBox,
    QGroupBox, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from config import TRACKS_DATABASE, CAR_NAMES_MAPPING, track_profile_calibrator
from ui.dialogs import ReplicateDialog
from ui.i18n import ui
from ui.table_filters import apply_header_filters, install_header_filters, table_item


class SetupsTabMixin:

    def create_setups_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        btn_refresh = QPushButton(ui("Recarregar Pasta"))
        btn_refresh.clicked.connect(self.refresh_setups_table)
        top_bar.addWidget(btn_refresh)

        btn_del_setup = QPushButton(ui("Deletar Setup Selecionado"))
        btn_del_setup.setObjectName("btn_delete")
        btn_del_setup.clicked.connect(self.handle_delete_setup)
        top_bar.addWidget(btn_del_setup)

        self.setup_car_filter = QComboBox()
        self.setup_car_filter.addItem(ui("Todos os carros"))
        self.setup_car_filter.currentIndexChanged.connect(self.refresh_setups_table)
        top_bar.addWidget(QLabel(ui("Carro:")))
        top_bar.addWidget(self.setup_car_filter)

        self.setup_track_filter = QComboBox()
        self.setup_track_filter.addItem(ui("Todas as pistas"))
        self.setup_track_filter.currentIndexChanged.connect(self.refresh_setups_table)
        top_bar.addWidget(QLabel(ui("Pista:")))
        top_bar.addWidget(self.setup_track_filter)

        btn_open = QPushButton(ui("Abrir Pasta"))
        btn_open.clicked.connect(self.open_setups_directory)
        top_bar.addWidget(btn_open)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        main_splitter = QSplitter(Qt.Orientation.Vertical)

        self.table_setups = QTableWidget(0, 3)
        self.table_setups.setHorizontalHeaderLabels([ui("Carro"), ui("Pista"), ui("Nome do Setup")])
        self.table_setups.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        install_header_filters(self.table_setups)
        self.table_setups.itemSelectionChanged.connect(self.show_selected_setup_details)
        main_splitter.addWidget(self.table_setups)

        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        tree_container = QVBoxLayout()

        factory_box = QGroupBox(ui("Fabrica de Setups (Quick Presets)"))
        factory_layout = QHBoxLayout()

        btn_q = QPushButton(ui("Gerar Qualy"))
        btn_q.setStyleSheet("background-color: #ff3b30; color: #fff;")
        btn_q.clicked.connect(lambda: self.apply_preset("qualy"))
        factory_layout.addWidget(btn_q)

        btn_r = QPushButton(ui("Gerar Corrida"))
        btn_r.setStyleSheet("background-color: #04d361; color: #000;")
        btn_r.clicked.connect(lambda: self.apply_preset("race"))
        factory_layout.addWidget(btn_r)

        btn_w = QPushButton(ui("Gerar Chuva"))
        btn_w.setStyleSheet("background-color: #007aff; color: #fff;")
        btn_w.clicked.connect(lambda: self.apply_preset("wet"))
        factory_layout.addWidget(btn_w)

        factory_box.setLayout(factory_layout)
        tree_container.addWidget(factory_box)

        creator_box = QGroupBox(ui("Criador de Setups Inteligente (Pista + Carro + Agressividade)"))
        creator_layout = QVBoxLayout()

        creator_row1 = QHBoxLayout()
        creator_row1.addWidget(QLabel(ui("Pista alvo:")))
        self.creator_track_combo = QComboBox()
        for track_id, track_display in TRACKS_DATABASE.items():
            self.creator_track_combo.addItem(track_display, track_id)
        creator_row1.addWidget(self.creator_track_combo, stretch=1)

        creator_row1.addWidget(QLabel(ui("Condicao:")))
        self.creator_condition_combo = QComboBox()
        self.creator_condition_combo.addItem(ui("Seco"), "dry")
        self.creator_condition_combo.addItem(ui("Molhado"), "wet")
        creator_row1.addWidget(self.creator_condition_combo)
        creator_layout.addLayout(creator_row1)

        creator_row2 = QHBoxLayout()
        creator_row2.addWidget(QLabel(ui("Conservador")))
        self.creator_aggr_slider = QSlider(Qt.Orientation.Horizontal)
        self.creator_aggr_slider.setRange(0, 100)
        self.creator_aggr_slider.setValue(50)
        self.creator_aggr_slider.valueChanged.connect(self._update_aggr_label)
        creator_row2.addWidget(self.creator_aggr_slider, stretch=1)
        creator_row2.addWidget(QLabel(ui("Agressivo")))
        creator_layout.addLayout(creator_row2)

        self.creator_aggr_label = QLabel(ui("Nivel atual: 50 (Equilibrado)"))
        self.creator_aggr_label.setStyleSheet("font-weight: bold; color: #ff3b30;")
        creator_layout.addWidget(self.creator_aggr_label)

        btn_generate_smart = QPushButton(ui("Gerar Setup Inteligente a partir do Selecionado"))
        btn_generate_smart.setStyleSheet("background-color: #ff3b30; color: #fff;")
        btn_generate_smart.clicked.connect(self.generate_smart_setup)
        creator_layout.addWidget(btn_generate_smart)

        btn_calibrate = QPushButton(ui("Calibrar Pistas com Meus Dados Reais (MoTeC)"))
        btn_calibrate.clicked.connect(self.calibrate_track_speeds)
        creator_layout.addWidget(btn_calibrate)

        creator_box.setLayout(creator_layout)
        tree_container.addWidget(creator_box)

        tree_buttons = QHBoxLayout()
        btn_save_setup = QPushButton(ui("Salvar Edicoes"))
        btn_save_setup.clicked.connect(self.save_setup_edits)
        tree_buttons.addWidget(btn_save_setup)

        btn_clone = QPushButton(ui("Clonar"))
        btn_clone.clicked.connect(self.clone_setup)
        tree_buttons.addWidget(btn_clone)

        btn_replicate = QPushButton(ui("Replicar p/ Carro"))
        btn_replicate.clicked.connect(self.replicate_setup)
        tree_buttons.addWidget(btn_replicate)
        tree_container.addLayout(tree_buttons)

        self.setup_tree = QTreeWidget()
        self.setup_tree.setHeaderLabels([ui("Parametro do Setup"), ui("Valor Editavel")])
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
        self.setup_advisor.setHtml(f"<h3>{ui('Engenheiro de Pista Virtual')}</h3><p>{ui('Selecione um setup para avaliar o impacto aerodinamico e mecanico na sua seguranca vs pace.')}</p>")
        advisor_container.addWidget(self.setup_advisor)

        btn_copy_tips = QPushButton(ui("Copiar Relatorio e Dicas"))
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
        self.table_setups.setSortingEnabled(False)
        try:
            self.table_setups.setRowCount(len(setups))
            for row, s in enumerate(setups):
                display_car = CAR_NAMES_MAPPING.get(s["car"].lower(), s["car"].replace("_", " ").title())
                self.table_setups.setItem(row, 0, table_item(display_car))
                self.table_setups.setItem(row, 1, table_item(s["track"]))
                self.table_setups.setItem(row, 2, table_item(s["name"]))
                self.table_setups.item(row, 0).setData(Qt.ItemDataRole.UserRole, s)
        finally:
            self.table_setups.setSortingEnabled(True)

        apply_header_filters(self.table_setups)

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
            QMessageBox.warning(self, ui("Aviso"), ui("Selecione um setup na tabela primeiro."))
            return
        try:
            self.setup_mgr.save_setup(self._current_setup_path, self._current_setup_dict)
            QMessageBox.information(self, ui("Sucesso"), ui("Modificacoes no setup foram salvas."))
        except Exception as e:
            QMessageBox.critical(self, ui("Erro"), ui("Nao foi possivel salvar: {error}", error=e))

    def handle_delete_setup(self):
        if not self._current_setup_path:
            QMessageBox.warning(self, ui("Aviso"), ui("Selecione um setup primeiro."))
            return
        reply = QMessageBox.question(self, ui("Confirmar Exclusao"), ui("Deseja realmente apagar este setup permanentemente?"), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.setup_mgr.delete_setup(self._current_setup_path)
                self.refresh_setups_table()
                self.setup_tree.clear()
                self.setup_advisor.clear()
                self._current_setup_path = None
                self._current_setup_dict = None
                QMessageBox.information(self, ui("Sucesso"), ui("Setup excluido."))
            except Exception as e:
                QMessageBox.critical(self, ui("Erro"), str(e))

    def clone_setup(self):
        if not self._current_setup_path:
            QMessageBox.warning(self, ui("Aviso"), ui("Selecione um setup primeiro."))
            return
        new_name, ok = QInputDialog.getText(self, ui("Clonar Setup"), ui("Digite o nome para o clone:"))
        if ok and new_name.strip():
            try:
                self.setup_mgr.clone_setup(self._current_setup_path, new_name.strip())
                self.refresh_setups_table()
                QMessageBox.information(self, ui("Sucesso"), ui("Setup clonado com sucesso!"))
            except Exception as e:
                QMessageBox.critical(self, ui("Erro"), str(e))

    def replicate_setup(self):
        if not self._current_setup_path:
            QMessageBox.warning(self, ui("Aviso"), ui("Selecione um setup primeiro."))
            return
        cars, tracks = self.setup_mgr.get_available_cars_and_tracks()
        dialog = ReplicateDialog(cars, tracks, self)
        if dialog.exec():
            target_car, target_track, new_name, adjust_19 = dialog.get_data()
            if not new_name:
                QMessageBox.warning(self, ui("Aviso"), ui("O nome nao pode ser vazio."))
                return
            try:
                self.setup_mgr.replicate_setup(self._current_setup_path, target_car, target_track, new_name, adjust_19)
                self.refresh_setups_table()
                QMessageBox.information(self, ui("Sucesso"), ui("Setup replicado para {car} em {track}!", car=target_car, track=target_track))
            except Exception as e:
                QMessageBox.critical(self, ui("Erro"), str(e))

    def apply_preset(self, preset_type):
        if not self._current_setup_path or not self._current_setup_dict:
            QMessageBox.warning(self, ui("Aviso"), ui("Selecione um setup base primeiro na tabela."))
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

        new_name, ok = QInputDialog.getText(self, ui("Salvar Preset"), ui("Nome do novo arquivo:"), QLineEdit.EchoMode.Normal, f"{base_name}{suffix}")
        if ok and new_name.strip():
            target_dir = os.path.dirname(self._current_setup_path)
            new_path = self.setup_mgr.get_unique_filename(target_dir, new_name.strip())
            try:
                self.setup_mgr.save_setup(new_path, new_data)
                self.refresh_setups_table()
                QMessageBox.information(self, ui("Preset Gerado"), ui("Setup {message}", message=msg))
            except Exception as e:
                QMessageBox.critical(self, ui("Erro"), str(e))

    def _update_aggr_label(self, value):
        from core.setup_creator import aggressiveness_label
        self.creator_aggr_label.setText(ui("Nivel atual: {value} ({label})", value=value, label=aggressiveness_label(value)))

    def calibrate_track_speeds(self):
        laps = self.motec.get_best_laps()
        speed_suggestions = track_profile_calibrator.suggest_avg_speed_ratings(laps)
        brake_suggestions = track_profile_calibrator.suggest_brake_stress_ratings(laps)

        if not speed_suggestions and not brake_suggestions:
            QMessageBox.information(self, ui("Sem dados suficientes"),
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
        reply = QMessageBox.question(self, ui("Calibrar Base de Pistas"), msg,
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            changed = track_profile_calibrator.apply_suggestions(speed_suggestions, field="avg_speed")
            changed += track_profile_calibrator.apply_suggestions(brake_suggestions, field="brake_stress")
            QMessageBox.information(self, ui("Calibracao aplicada"),
                                     f"{changed} atualizacao(oes) gravada(s) em core/data/tracks.json.")

    def generate_smart_setup(self):
        if not self._current_setup_path or not self._current_setup_dict:
            QMessageBox.warning(self, ui("Aviso"), ui("Selecione um setup base na tabela primeiro "
                                 "(pode ser o setup padrao do carro ou qualquer setup salvo)."))
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
            QMessageBox.critical(self, ui("Erro"), ui("Nao foi possivel gerar o setup: {error}", error=e))
            return

        base_name = os.path.basename(self._current_setup_path).replace(".json", "")
        suffix = f"_{track_id}_{aggressiveness}_{'W' if condition == 'wet' else 'S'}"
        suggested_name = f"{base_name}{suffix}"

        new_name, ok = QInputDialog.getText(
            self, ui("Salvar Setup Inteligente"), ui("Nome do novo arquivo:"),
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

            report = f"<h3>{ui('Setup Inteligente Gerado')}</h3>"
            report += f"<p><b>{ui('Pista:')}</b> {TRACKS_DATABASE.get(track_id, track_id)}<br>"
            report += f"<b>{ui('Nivel:')}</b> {meta['aggressiveness']} ({meta['aggressiveness_label']})<br>"
            report += f"<b>{ui('Condicao:')}</b> {ui('Molhado') if condition == 'wet' else ui('Seco')}</p><hr>"
            report += f"<h4>{ui('Ajustes aplicados:')}</h4><ul>"
            for n in meta["notes"]:
                report += f"<li>{n}</li>"
            report += "</ul>"
            self.setup_advisor.setHtml(report)

            QMessageBox.information(self, ui("Sucesso"), ui("Setup inteligente salvo em:\n{path}", path=new_path))
        except Exception as e:
            QMessageBox.critical(self, ui("Erro"), str(e))

    def run_setup_analysis(self, car, track, setup_data):
        best_lap_time = ui("Nenhum tempo salvo")
        laps = self.motec.get_best_laps()
        for lap in laps:
            if lap.get("car", "").lower() == car.lower() and lap.get("track", "").lower() == track.lower():
                if lap.get("raw_time", 0) >= 70.0:
                    best_lap_time = f"<b style='color:#04d361;'>{lap['lap_time']}</b> ({ui('Feita por {driver}', driver=lap['driver'])})"
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
                    notes.append(f"<b>{ui('Diferencial (Preload={value}): Baixo. Excelente para rotacionar o carro na tangencia (lift-off oversteer). Exige cuidado com a traseira.', value=preload)}</b>")
                elif preload > 120:
                    safety_score += 10
                    pace_score -= 10
                    notes.append(f"<b>{ui('Diferencial (Preload={value}): Alto. Traciona de forma estavel em saida de curvas, mas pode causar subesterco cronico.', value=preload)}</b>")
        except: pass

        try:
            mech = setup_data.get("basicSetup", {}).get("mechanicalBalance", {})
            arb_front = mech.get("aRBFront")
            arb_rear = mech.get("aRBRear")
            if arb_front is not None and arb_rear is not None:
                if arb_front > arb_rear + 2:
                    safety_score += 5
                    notes.append(f"<b>{ui('Barras (ARB F:{front} R:{rear}): Dianteira predominante. Evita rodar facil em curvas rapidas, a custo de perder o apex.', front=arb_front, rear=arb_rear)}</b>")
                elif arb_rear > arb_front:
                    safety_score -= 15
                    pace_score += 15
                    notes.append(f"<b>{ui('Barras (ARB F:{front} R:{rear}): Traseira rigida. Setup bastante agressivo mecanicamente, permitindo curvas de baixa velozes, mas instavel em zebras.', front=arb_front, rear=arb_rear)}</b>")
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
                    notes.append(f"<b>{ui('Aerodinamica (Rake={value}mm): Rake agressivo (Traseira alta). Direciona todo o downforce pro bico do carro. Pode ser escorregadio na traseira.', value=rake)}</b>")
                elif rake < 8:
                    safety_score += 5
                    pace_score -= 5
                    notes.append(f"<b>{ui('Aerodinamica (Rake={value}mm): Rake conservador. Carro tendera ao equilibrio aerodinamico neutro.', value=rake)}</b>")
        except: pass

        try:
            bbias = setup_data.get("basicSetup", {}).get("alignment", {}).get("brakeBias", None)
            if bbias is not None:
                if float(bbias) < 54.0:
                    safety_score -= 10
                    pace_score += 10
                    notes.append(f"<b>{ui('Brake Bias ({value}%): Tendencia forte para a traseira. Ajuda na agilidade de Trail Braking no Apex, mas perigoso em reducoes longas.', value=bbias)}</b>")
        except: pass

        try:
            camber = setup_data.get("basicSetup", {}).get("alignment", {}).get("camber", [])
            if len(camber) == 4 and camber[0] > -2.5:
                safety_score -= 5
                pace_score -= 10
                notes.append(f"<b>{ui('Camber Dianteiro ({value}): Lembrete: A meta atual do ACC e usar o camber negativo no maximo permitido pelo carro para maior contato lateral.', value=camber[0])}</b>")
        except: pass

        try:
            pads = setup_data.get("basicSetup", {}).get("strategy", {}).get("frontBrakePadCompound")
            if pads == 0:
                notes.append(f"<b>{ui('Freios (Pad 1): Uso exclusivo para Qualy/Sprint (-30min). Podem falhar em corridas longas.')}</b>")
            elif pads == 2:
                notes.append(f"<b>{ui('Freios (Pad 3): Pastilhas seguras para Chuva ou longa duracao.')}</b>")
        except: pass

        safety_score = max(0, min(100, safety_score))
        pace_score = max(0, min(100, pace_score))

        html = f"<h3>{ui('Engenheiro Virtual de Setups')}</h3>"
        html += f"<p><b>{ui('Referencia (MoTeC):')}</b> {best_lap_time}</p><hr>"

        safe_color = "#04d361" if safety_score >= 70 else ("#e1e1e6" if safety_score >= 50 else "#ff3b30")
        pace_color = "#04d361" if pace_score >= 70 else ("#e1e1e6" if pace_score >= 50 else "#ff3b30")

        html += f"<p><b>{ui('Seguranca e Estabilidade (Rating SA/CC):')}</b> <span style='color:{safe_color}; font-weight:bold;'>{safety_score}/100</span><br>"
        html += f"<b>{ui('Agressividade e Pace:')}</b> <span style='color:{pace_color}; font-weight:bold;'>{pace_score}/100</span></p><hr>"

        html += f"<h4>{ui('Diagnostico Tecnico:')}</h4><ul>"
        for n in notes:
            html += f"<li>{n}</li><br>"

        if not notes:
            html += f"<li>{ui('Setup equilibrado, padrao para corridas gerais.')}</li>"

        html += "</ul>"

        self.setup_advisor.setHtml(html)

    def copy_setup_analysis(self):
        if hasattr(self, "setup_advisor"):
            QApplication.clipboard().setText(self.setup_advisor.toPlainText())
            QMessageBox.information(self, ui("Copiado"), ui("Analise e dicas copiadas para a area de transferencia!"))

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
