"""Folha de estilo (tema escuro) do ACC Manager. Editar cores/espacamento aqui
nao afeta nenhuma logica - e so aparencia."""

DARK_STYLE = """
* { outline: none; }
QMainWindow, QWidget, QDialog { background-color: #0d0d10; color: #e8e8ed; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; }

QTabWidget::pane { border: 1px solid #232328; background-color: #17171b; border-radius: 10px; top: -1px; }
QTabBar::tab { background: transparent; color: #85858f; padding: 10px 22px; margin-right: 2px; border-top-left-radius: 8px; border-top-right-radius: 8px; font-weight: 600; }
QTabBar::tab:hover { color: #c7c7cf; }
QTabBar::tab:selected { background: #17171b; color: #d88a7d; border-bottom: 2px solid #d88a7d; }

QGroupBox { border: 1px solid #232328; border-radius: 10px; margin-top: 16px; padding-top: 6px; font-weight: 700; font-size: 12px; color: #d88a7d; background-color: #131316; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 2px 8px; }

QLabel { color: #c7c7cf; }

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #0a0a0c; border: 1px solid #2b2b32; border-radius: 6px;
    padding: 7px 9px; color: #ffffff; selection-background-color: #d88a7d;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus { border: 1px solid #d88a7d; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView { background-color: #17171b; border: 1px solid #2b2b32; selection-background-color: #d88a7d; selection-color: #0d0d10; outline: none; }

QTableWidget { background-color: #0a0a0c; border: 1px solid #232328; border-radius: 8px; gridline-color: #1c1c21; color: #e8e8ed; alternate-background-color: #101013; }
QTableWidget::item { padding: 4px; }
QTableWidget::item:selected { background-color: #2c2424; color: #e7b7ad; }
QHeaderView::section { background-color: #1a1a1f; color: #9a9aa4; padding: 8px; border: none; border-bottom: 1px solid #232328; font-weight: 700; }

QPushButton {
    background-color: #2d3037; color: #edf2fa; border: 1px solid #4a505d; border-radius: 8px;
    padding: 9px 18px; font-weight: 600;
}
QPushButton:hover { background-color: #3a404d; border: 1px solid #5b6478; }
QPushButton:pressed { background-color: #232833; }
QPushButton#btn_start { background-color: #9bc7ac; color: #122a1d; border: none; }
QPushButton#btn_start:hover { background-color: #a9d2b8; }
QPushButton#btn_reset, QPushButton#btn_delete { background-color: #d7a59d; color: #211514; border: none; }
QPushButton#btn_reset:hover, QPushButton#btn_delete:hover { background-color: #c9918a; }

QTreeWidget { background-color: #0a0a0c; color: #e8e8ed; border: 1px solid #2b2b32; border-radius: 8px; }
QTreeWidget::item { padding: 3px; }
QTreeWidget::item:hover { background-color: #1a1a1f; }
QTreeWidget::item:selected { background-color: #2e2729; color: #e7b7ad; }

QSplitter::handle { background-color: #1c1c21; }
QSplitter::handle:hover { background-color: #d88a7d; }

QCheckBox { spacing: 8px; color: #c7c7cf; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 1px solid #3a3a42; background-color: #0a0a0c; }
QCheckBox::indicator:checked { background-color: #d88a7d; border: 1px solid #d88a7d; }

QSlider::groove:horizontal { height: 6px; background: #232328; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #d88a7d; border-radius: 3px; }
QSlider::add-page:horizontal { background: #232328; border-radius: 3px; }
QSlider::handle:horizontal { background: #ffffff; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }
QSlider::handle:horizontal:hover { background: #d88a7d; }

QScrollBar:vertical { background: #0d0d10; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #2b2b32; border-radius: 5px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #3a3a42; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QMessageBox { background-color: #17171b; }
"""


LIGHT_STYLE = """
* { outline: none; }
QMainWindow, QWidget, QDialog { background-color: #f3f5f7; color: #1f2933; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; }

QStatusBar { background-color: #e7ebef; color: #52606d; }
QTabWidget::pane { border: 1px solid #d5dce3; background-color: #ffffff; border-radius: 10px; top: -1px; }
QTabBar::tab { background: transparent; color: #6b7785; padding: 10px 22px; margin-right: 2px; border-top-left-radius: 8px; border-top-right-radius: 8px; font-weight: 600; }
QTabBar::tab:hover { color: #1f2933; }
QTabBar::tab:selected { background: #ffffff; color: #d48f82; border-bottom: 2px solid #d48f82; }

QGroupBox { border: 1px solid #d5dce3; border-radius: 10px; margin-top: 16px; padding-top: 6px; font-weight: 700; font-size: 12px; color: #b97a70; background-color: #ffffff; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 2px 8px; background-color: #f3f5f7; }

QLabel { color: #52606d; }

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #ffffff; border: 1px solid #cbd2d9; border-radius: 6px;
    padding: 7px 9px; color: #1f2933; selection-background-color: #e9c8c1; selection-color: #1f2933;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus { border: 1px solid #d48f82; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView { background-color: #ffffff; border: 1px solid #cbd2d9; selection-background-color: #e9c8c1; selection-color: #1f2933; outline: none; }

QTableWidget { background-color: #ffffff; border: 1px solid #d5dce3; border-radius: 8px; gridline-color: #e5e9ed; color: #1f2933; alternate-background-color: #f8fafb; }
QTableWidget::item { padding: 4px; }
QTableWidget::item:selected { background-color: #f7e8e5; color: #9a514b; }
QHeaderView::section { background-color: #e9edf1; color: #52606d; padding: 8px; border: none; border-bottom: 1px solid #d5dce3; font-weight: 700; }

QPushButton {
    background-color: #f4f7fb; color: #2f4057; border: 1px solid #d6dde7; border-radius: 8px;
    padding: 9px 18px; font-weight: 600;
}
QPushButton:hover { background-color: #edf3ff; border: 1px solid #bfd1eb; }
QPushButton:pressed { background-color: #e3ebf7; }
QPushButton#btn_start { background-color: #afd6b8; color: #163225; border: none; }
QPushButton#btn_start:hover { background-color: #a1c8aa; }
QPushButton#btn_reset, QPushButton#btn_delete { background-color: #e7b8b1; color: #2a1a18; border: none; }
QPushButton#btn_reset:hover, QPushButton#btn_delete:hover { background-color: #dca39a; }

QTreeWidget { background-color: #ffffff; color: #1f2933; border: 1px solid #cbd2d9; border-radius: 8px; }
QTreeWidget::item { padding: 3px; }
QTreeWidget::item:hover { background-color: #f8e8e6; }
QTreeWidget::item:selected { background-color: #f8e2df; color: #9a514b; }

QSplitter::handle { background-color: #d5dce3; }
QSplitter::handle:hover { background-color: #d48f82; }

QCheckBox { spacing: 8px; color: #52606d; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 1px solid #aeb8c2; background-color: #ffffff; }
QCheckBox::indicator:checked { background-color: #d48f82; border: 1px solid #d48f82; }

QSlider::groove:horizontal { height: 6px; background: #d5dce3; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #d48f82; border-radius: 3px; }
QSlider::add-page:horizontal { background: #d5dce3; border-radius: 3px; }
QSlider::handle:horizontal { background: #ffffff; border: 1px solid #aeb8c2; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }
QSlider::handle:horizontal:hover { background: #d48f82; }

QProgressBar { background-color: #d5dce3; border: none; border-radius: 3px; height: 7px; }
QProgressBar::chunk { background-color: #c9473d; border-radius: 3px; }
QScrollBar:vertical { background: #e7ebef; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #b8c1ca; border-radius: 5px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #8f9ba7; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QMessageBox { background-color: #ffffff; color: #1f2933; }
"""
