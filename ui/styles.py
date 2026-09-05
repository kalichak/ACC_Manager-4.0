"""Folha de estilo (tema escuro) do ACC Manager. Editar cores/espacamento aqui
nao afeta nenhuma logica - e so aparencia."""

DARK_STYLE = """
* { outline: none; }
QMainWindow, QWidget, QDialog { background-color: #0d0d10; color: #e8e8ed; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; }

QTabWidget::pane { border: 1px solid #232328; background-color: #17171b; border-radius: 10px; top: -1px; }
QTabBar::tab { background: transparent; color: #85858f; padding: 10px 22px; margin-right: 2px; border-top-left-radius: 8px; border-top-right-radius: 8px; font-weight: 600; }
QTabBar::tab:hover { color: #c7c7cf; }
QTabBar::tab:selected { background: #17171b; color: #ff4b3e; border-bottom: 2px solid #ff4b3e; }

QGroupBox { border: 1px solid #232328; border-radius: 10px; margin-top: 16px; padding-top: 6px; font-weight: 700; font-size: 12px; color: #ff4b3e; background-color: #131316; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 2px 8px; }

QLabel { color: #c7c7cf; }

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #0a0a0c; border: 1px solid #2b2b32; border-radius: 6px;
    padding: 7px 9px; color: #ffffff; selection-background-color: #ff4b3e;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus { border: 1px solid #ff4b3e; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView { background-color: #17171b; border: 1px solid #2b2b32; selection-background-color: #ff4b3e; selection-color: #0d0d10; outline: none; }

QTableWidget { background-color: #0a0a0c; border: 1px solid #232328; border-radius: 8px; gridline-color: #1c1c21; color: #e8e8ed; alternate-background-color: #101013; }
QTableWidget::item { padding: 4px; }
QTableWidget::item:selected { background-color: #2a1613; color: #ff4b3e; }
QHeaderView::section { background-color: #1a1a1f; color: #9a9aa4; padding: 8px; border: none; border-bottom: 1px solid #232328; font-weight: 700; }

QPushButton {
    background-color: #232328; color: #f0f0f4; border: 1px solid #2f2f36; border-radius: 8px;
    padding: 9px 18px; font-weight: 600;
}
QPushButton:hover { background-color: #2c2c33; border: 1px solid #3a3a42; }
QPushButton:pressed { background-color: #1c1c20; }
QPushButton#btn_start { background-color: #04d361; color: #062910; border: none; }
QPushButton#btn_start:hover { background-color: #05e86b; }
QPushButton#btn_reset, QPushButton#btn_delete { background-color: #ff4b3e; color: #ffffff; border: none; }
QPushButton#btn_reset:hover, QPushButton#btn_delete:hover { background-color: #e8382b; }

QTreeWidget { background-color: #0a0a0c; color: #e8e8ed; border: 1px solid #2b2b32; border-radius: 8px; }
QTreeWidget::item { padding: 3px; }
QTreeWidget::item:hover { background-color: #1a1a1f; }
QTreeWidget::item:selected { background-color: #2a1613; color: #ff4b3e; }

QSplitter::handle { background-color: #1c1c21; }
QSplitter::handle:hover { background-color: #ff4b3e; }

QCheckBox { spacing: 8px; color: #c7c7cf; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 1px solid #3a3a42; background-color: #0a0a0c; }
QCheckBox::indicator:checked { background-color: #ff4b3e; border: 1px solid #ff4b3e; }

QSlider::groove:horizontal { height: 6px; background: #232328; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #ff4b3e; border-radius: 3px; }
QSlider::add-page:horizontal { background: #232328; border-radius: 3px; }
QSlider::handle:horizontal { background: #ffffff; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }
QSlider::handle:horizontal:hover { background: #ff4b3e; }

QScrollBar:vertical { background: #0d0d10; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #2b2b32; border-radius: 5px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #3a3a42; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QMessageBox { background-color: #17171b; }
"""
