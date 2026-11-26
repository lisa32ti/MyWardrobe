import os

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QMessageBox
from PyQt5.QtCore import Qt

from database.db_manager import DatabaseManager


class CreateOutfitDialog(QDialog):
    def __init__(self, db: DatabaseManager, parent=None) -> None:
        super().__init__(parent)

        ui_path = os.path.join(
            os.path.dirname(__file__), "..", "ui", "create_outfit.ui"
        )
        uic.loadUi(ui_path, self)

        self.db = db
        self.created_outfit_id = None

        self._load_clothes()
        self._connect_signals()

    def _load_clothes(self) -> None:
        self.clothesList.clear()

        items = self.db.get_all_clothes()
        if not items:
            item = QListWidgetItem("В гардеробе пока нет вещей")
            item.setFlags(Qt.NoItemFlags)
            self.clothesList.addItem(item)
            return

        for row in items:
            text = f'{row["name"]} — {row["category"]} ({row["color"]})'
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, row["id"])
            self.clothesList.addItem(item)

    def _connect_signals(self) -> None:
        self.btnSave.clicked.connect(self._save_outfit)
        self.btnCancel.clicked.connect(self.reject)

    def _save_outfit(self) -> None:
        name = self.nameEdit.text().strip()
        description = self.descEdit.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название образа.")
            self.nameEdit.setFocus()
            return

        selected_items = self.clothesList.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Ошибка", "Выберите хотя бы одну вещь для образа."
            )
            return

        clothes_ids = [
            item.data(Qt.UserRole)
            for item in selected_items
            if item.data(Qt.UserRole) is not None
        ]

        if not clothes_ids:
            QMessageBox.warning(
                self, "Ошибка", "Выберите хотя бы одну вещь для образа."
            )
            return

        try:
            self.created_outfit_id = self.db.add_outfit(
                name, description, clothes_ids
            )
        except Exception as exc:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось сохранить образ:\n{exc}"
            )
            return

        self.accept()