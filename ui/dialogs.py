"""Dialogo auxiliar (janela pop-up) usado pela aba de Setups para escolher
carro/pista de destino ao replicar um setup."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLineEdit, QCheckBox, QFormLayout, QDialogButtonBox

from config import CAR_NAMES_MAPPING
from ui.i18n import ui

class ReplicateDialog(QDialog):
    def __init__(self, cars, tracks, parent=None):
        super().__init__(parent)
        self.setWindowTitle(ui("Replicar Setup"))
        self.resize(400, 200)

        layout = QVBoxLayout(self)
        self.car_combo = QComboBox()
        for c in cars:
            display_name = CAR_NAMES_MAPPING.get(c.lower(), c.replace("_", " ").title())
            self.car_combo.addItem(display_name, c)

        self.track_combo = QComboBox()
        self.track_combo.addItems(tracks)

        self.name_input = QLineEdit("Setup_Replicado")
        self.chk_19 = QCheckBox(ui("Adequar pressoes de pneu para ACC v1.9 (-1.0 psi)"))
        self.chk_19.setChecked(True)

        form = QFormLayout()
        form.addRow(ui("Carro Destino:"), self.car_combo)
        form.addRow(ui("Pista Destino:"), self.track_combo)
        form.addRow(ui("Novo Nome:"), self.name_input)

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
