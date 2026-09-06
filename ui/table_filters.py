from PyQt6.QtWidgets import QInputDialog, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from ui.i18n import ui


class SortableTableWidgetItem(QTableWidgetItem):
    """Ordena pelo valor tipado quando ele existe."""

    def __lt__(self, other):
        left = self.data(Qt.ItemDataRole.UserRole + 1)
        right = other.data(Qt.ItemDataRole.UserRole + 1)
        if left is not None and right is not None:
            try:
                return left < right
            except TypeError:
                pass
        return super().__lt__(other)


def table_item(text, sort_value=None):
    item = SortableTableWidgetItem(str(text))
    if sort_value is not None:
        item.setData(Qt.ItemDataRole.UserRole + 1, sort_value)
    return item


def install_header_filters(table: QTableWidget) -> None:
    """Keeps single-click sorting and opens filters on double-click."""
    table.setSortingEnabled(True)
    table.setProperty("column_filters", {})
    table.horizontalHeader().sectionDoubleClicked.connect(
        lambda column: _prompt_column_filter(table, column)
    )


def apply_header_filters(table: QTableWidget) -> None:
    filters = table.property("column_filters") or {}
    for row in range(table.rowCount()):
        visible = True
        for column, value in filters.items():
            item = table.item(row, column)
            if item is None or value.casefold() not in item.text().casefold():
                visible = False
                break
        table.setRowHidden(row, not visible)


def _prompt_column_filter(table: QTableWidget, column: int) -> None:
    header = table.horizontalHeaderItem(column)
    column_name = header.text() if header else "coluna"
    filters = table.property("column_filters") or {}
    current = filters.get(column, "")
    value, accepted = QInputDialog.getText(
        table,
        ui("Filtrar tabela"),
        ui("Filtrar {column} (vazio remove):", column=column_name),
        text=current,
    )
    if not accepted:
        return

    value = value.strip()
    if value:
        filters[column] = value
    else:
        filters.pop(column, None)
    table.setProperty("column_filters", filters)
    apply_header_filters(table)
