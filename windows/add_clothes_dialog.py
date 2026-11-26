import os

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from database.db_manager import DatabaseManager
from constants import (
    CATEGORIES,
    COLORS,
    SEASONS,
    PLACEHOLDER_IMAGE,
)
from utils.helpers import copy_image_to_storage, delete_image_if_exists


class AddClothesDialog(QDialog):

    PREVIEW_SIZE = 150

    def __init__(
        self,
        db: DatabaseManager,
        parent=None,
        clothes_id: int = None,
    ) -> None:
        super().__init__(parent)

        ui_path = os.path.join(
            os.path.dirname(__file__), "..", "ui", "add_clothes.ui"
        )
        uic.loadUi(ui_path, self)

        self.db = db
        self.clothes_id = clothes_id
        self.selected_image_path = ""  
        self.current_image_name = ""  

        self._fill_combos()
        self._connect_signals()
        self.setAcceptDrops(True)

        if self.clothes_id is not None:
            self.setWindowTitle("Редактировать вещь")
            self._load_existing()


    def _fill_combos(self) -> None:
        self.categoryCombo.addItems(CATEGORIES)
        self.colorCombo.addItems(COLORS)
        self.seasonCombo.addItems(SEASONS)

    def _connect_signals(self) -> None:
        self.btnSelectImage.clicked.connect(self._select_image)
        self.btnSave.clicked.connect(self._save)
        self.btnCancel.clicked.connect(self.reject)

    def _load_existing(self) -> None:
        row = self.db.get_clothes(self.clothes_id)
        if row is None:
            QMessageBox.critical(
                self, "Ошибка", "Вещь не найдена в базе данных."
            )
            self.reject()
            return

        self.nameEdit.setText(row["name"])
        self.categoryCombo.setCurrentText(row["category"])
        self.colorCombo.setCurrentText(row["color"])
        self.seasonCombo.setCurrentText(row["season"])

        self.current_image_name = row["image"] or ""
        if self.current_image_name:
            image_path = self._storage_path(self.current_image_name)
            self._show_preview(image_path)


    @staticmethod
    def _storage_path(image_name: str) -> str:
        from constants import CLOTHES_IMAGES_DIR
        return os.path.join(CLOTHES_IMAGES_DIR, image_name)

    def _select_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите фото вещи",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)",
        )
        if path:
            self._set_new_image(path)

    def _set_new_image(self, path: str) -> None:
        self.selected_image_path = path
        self._show_preview(path)

    def _show_preview(self, path: str) -> None:
        pixmap = QPixmap(path)
        if pixmap.isNull():
            pixmap = QPixmap(PLACEHOLDER_IMAGE)

        pixmap = pixmap.scaled(
            self.PREVIEW_SIZE,
            self.PREVIEW_SIZE,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.imageLabel.setPixmap(pixmap)


    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                self._set_new_image(path)
                break

    def _save(self) -> None:
        name = self.nameEdit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название вещи.")
            self.nameEdit.setFocus()
            return

        category = self.categoryCombo.currentText()
        color = self.colorCombo.currentText()
        season = self.seasonCombo.currentText()

        new_image_name = self._prepare_image()

        try:
            if self.clothes_id is None:
                self.db.add_clothes(
                    name, category, color, season, new_image_name
                )
            else:
                self.db.update_clothes(
                    self.clothes_id,
                    name,
                    category,
                    color,
                    season,
                    new_image_name,
                )
        except Exception as exc:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось сохранить вещь:\n{exc}"
            )
            return

        self.accept()

    def _prepare_image(self) -> str:
        if not self.selected_image_path:
            return self.current_image_name

        if self.current_image_name:
            delete_image_if_exists(self.current_image_name)

        new_name = copy_image_to_storage(self.selected_image_path)
        return new_name