"""
ACC Manager - ponto de entrada
=================================

Este arquivo faz UMA coisa: sobe a aplicacao. Toda a logica real esta
dividida em:
  config.py       -> .env, caminhos, base de carros/pistas, imports de core/
  ui/styles.py     -> tema visual (DARK_STYLE)
  ui/dialogs.py    -> janelas pop-up auxiliares
  ui/server_tab.py, telemetry_tab.py, setups_tab.py, leaderboard_tab.py
                   -> uma aba cada, cada uma um Mixin
  ui/main_window.py -> junta os Mixins na janela principal (ACCManagerApp)
"""

import os
from PyQt6.QtGui import QIcon

from ui.styles import DARK_STYLE
from ui.main_window import ACCManagerApp


try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    print("\n[ERRO CRITICO] PyQt6 nao esta instalado no ambiente atual!")
    print("Execute no terminal: pip install -r requirements.txt\n")
    sys.exit(1)

from ui.styles import DARK_STYLE
from ui.main_window import ACCManagerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = ACCManagerApp()
    window.show()
    sys.exit(app.exec())
