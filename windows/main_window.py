import os

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QDialog,
    QProgressBar,
    QLabel,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap

from database.db_manager import DatabaseManager
from constants import CATEGORIES, PLACEHOLDER_IMAGE, CLOTHES_IMAGES_DIR
from utils.helpers import delete_image_if_exists
from windows.add_clothes_dialog import AddClothesDialog
from windows.create_outfit_dialog import CreateOutfitDialog


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        ui_path = os.path.join(
            os.path.dirname(__file__), "..", "ui", "main_window.ui"
        )
        uic.loadUi(ui_path, self)

        self.db = DatabaseManager()

        self._setup_table()
        self._setup_filters()
        self._connect_signals()

        self.load_clothes()
        self.load_outfits()
        self.load_stats()


    def _setup_table(self) -> None:
        self.clothesTable.setColumnCount(6)
        self.clothesTable.setHorizontalHeaderLabels(
            ["ID", "Название", "Категория", "Цвет", "Сезон", "★"]
        )
        self.clothesTable.setEditTriggers(
            self.clothesTable.NoEditTriggers
        )
        self.clothesTable.setSelectionBehavior(
            self.clothesTable.SelectRows
        )
        self.clothesTable.setSelectionMode(
            self.clothesTable.SingleSelection
        )
        
        self.clothesTable.setIconSize(QSize(40, 40))
        
        header = self.clothesTable.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.clothesTable.setColumnWidth(0, 40)
        self.clothesTable.setColumnWidth(5, 40)

    def _setup_filters(self) -> None:
        self.categoryFilter.clear()
        self.categoryFilter.addItem("Все категории")
        self.categoryFilter.addItems(CATEGORIES)

    def _connect_signals(self) -> None:
        self.btnSearch.clicked.connect(self.load_clothes)
        self.btnReset.clicked.connect(self._reset_filters)
        self.searchEdit.returnPressed.connect(self.load_clothes)

        self.btnAddClothes.clicked.connect(self._add_clothes)
        self.btnEditClothes.clicked.connect(self._edit_clothes)
        self.btnDeleteClothes.clicked.connect(self._delete_clothes)
        self.btnFavoriteClothes.clicked.connect(self._toggle_favorite_clothes)

        self.btnCreateOutfit.clicked.connect(self._create_outfit)
        self.btnDeleteOutfit.clicked.connect(self._delete_outfit)
        self.btnFavoriteOutfit.clicked.connect(self._toggle_favorite_outfit)
        self.btnRandomOutfit.clicked.connect(self._random_outfit)
        self.outfitsList.itemSelectionChanged.connect(self._on_outfit_selected)


    def load_clothes(self) -> None:
        query = self.searchEdit.text().strip()

        category = ""
        if self.categoryFilter.currentIndex() > 0:
            category = self.categoryFilter.currentText()

        items = self.db.search_clothes(query, category)

        self.clothesTable.setRowCount(0)

        for row_idx, item in enumerate(items):
            self.clothesTable.insertRow(row_idx)

            id_item = QTableWidgetItem(str(item["id"]))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.clothesTable.setItem(row_idx, 0, id_item)

            name_item = QTableWidgetItem(item["name"])
            
            if item["image"]:
                image_path = os.path.join(CLOTHES_IMAGES_DIR, item["image"])
                if os.path.exists(image_path):
                    pixmap = QPixmap(image_path)
                    icon = QIcon(pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    name_item.setIcon(icon)
            else:
                pixmap = QPixmap(PLACEHOLDER_IMAGE)
                if not pixmap.isNull():
                    icon = QIcon(pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    name_item.setIcon(icon)
            
            self.clothesTable.setItem(row_idx, 1, name_item)

            self.clothesTable.setItem(
                row_idx, 2, QTableWidgetItem(item["category"])
            )
            
            self.clothesTable.setItem(
                row_idx, 3, QTableWidgetItem(item["color"])
            )
            
            self.clothesTable.setItem(
                row_idx, 4, QTableWidgetItem(item["season"])
            )

            star = "★" if item["favorite"] else "☆"
            star_item = QTableWidgetItem(star)
            star_item.setTextAlignment(Qt.AlignCenter)
            if item["favorite"]:
                star_item.setForeground(Qt.red)
            self.clothesTable.setItem(row_idx, 5, star_item)

    def _reset_filters(self) -> None:
        self.searchEdit.clear()
        self.categoryFilter.setCurrentIndex(0)
        self.load_clothes()

    def _selected_clothes_id(self):
        row = self.clothesTable.currentRow()
        if row < 0:
            return None
        item = self.clothesTable.item(row, 0)
        if item is None:
            return None
        return int(item.text())

    def _add_clothes(self) -> None:
        dialog = AddClothesDialog(self.db, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_clothes()
            self.load_stats()

    def _edit_clothes(self) -> None:
        clothes_id = self._selected_clothes_id()
        if clothes_id is None:
            QMessageBox.information(
                self, "Внимание", "Сначала выберите вещь в таблице."
            )
            return

        dialog = AddClothesDialog(self.db, self, clothes_id=clothes_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_clothes()
            self.load_stats()

    def _delete_clothes(self) -> None:
        clothes_id = self._selected_clothes_id()
        if clothes_id is None:
            QMessageBox.information(
                self, "Внимание", "Сначала выберите вещь в таблице."
            )
            return

        answer = QMessageBox.question(
            self,
            "Удаление",
            "Удалить выбранную вещь?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        row = self.db.get_clothes(clothes_id)
        if row is not None and row["image"]:
            delete_image_if_exists(row["image"])

        self.db.delete_clothes(clothes_id)
        self.load_clothes()
        self.load_stats()

    def _toggle_favorite_clothes(self) -> None:
        clothes_id = self._selected_clothes_id()
        if clothes_id is None:
            return
        self.db.toggle_clothes_favorite(clothes_id)
        self.load_clothes()


    def load_outfits(self) -> None:
        self.outfitsList.clear()
        outfits = self.db.get_all_outfits()
        for row in outfits:
            star = "★ " if row["favorite"] else ""
            item_text = f'{star}{row["name"]}'
            self.outfitsList.addItem(item_text)
            item = self.outfitsList.item(self.outfitsList.count() - 1)
            item.setData(Qt.UserRole, row["id"])

    def _on_outfit_selected(self) -> None:
        items = self.outfitsList.selectedItems()
        if not items:
            return

        outfit_id = items[0].data(Qt.UserRole)
        if outfit_id is None:
            return

        outfit = self.db.get_outfit(outfit_id)
        if not outfit:
            return

        self.outfitNameLabel.setText(outfit["name"])
        self.outfitDescLabel.setText(outfit["description"] or "—")

        self.outfitItemsList.clear()
        for clothes_row in self.db.get_outfit_clothes(outfit_id):
            self.outfitItemsList.addItem(
                f'{clothes_row["name"]} — {clothes_row["category"]}'
            )

    def _create_outfit(self) -> None:
        dialog = CreateOutfitDialog(self.db, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_outfits()
            self.load_stats()

    def _delete_outfit(self) -> None:
        items = self.outfitsList.selectedItems()
        if not items:
            QMessageBox.information(
                self, "Внимание", "Сначала выберите образ."
            )
            return

        answer = QMessageBox.question(
            self,
            "Удаление",
            "Удалить выбранный образ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        outfit_id = items[0].data(Qt.UserRole)
        self.db.delete_outfit(outfit_id)
        self.load_outfits()
        self.load_stats()
        self.outfitNameLabel.setText("Название образа")
        self.outfitDescLabel.setText("Описание")
        self.outfitItemsList.clear()

    def _toggle_favorite_outfit(self) -> None:
        items = self.outfitsList.selectedItems()
        if not items:
            return
        outfit_id = items[0].data(Qt.UserRole)
        self.db.toggle_outfit_favorite(outfit_id)
        self.load_outfits()

    def _random_outfit(self) -> None:
        outfit = self.db.get_random_outfit()
        if not outfit:
            QMessageBox.information(
                self, "Пусто", "Пока нет ни одного образа."
            )
            return

        for i in range(self.outfitsList.count()):
            item = self.outfitsList.item(i)
            if item.data(Qt.UserRole) == outfit["id"]:
                item.setSelected(True)
                self._on_outfit_selected()
                break


    def load_stats(self) -> None:
        clothes_count, outfits_count = self.db.get_total_counts()
        self.statsTotalLabel.setText(
            f"Всего вещей: {clothes_count} | Образов: {outfits_count}"
        )

        self._fill_stats_group(
            self.categoryStatsLayout, self.db.get_count_by_category()
        )
        self._fill_stats_group(
            self.seasonStatsLayout, self.db.get_count_by_season()
        )
        self._fill_stats_group(
            self.colorStatsLayout, self.db.get_count_by_color()
        )

    def _fill_stats_group(self, layout, rows) -> None:
        while layout.count():
            child = layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()

        if not rows:
            layout.addWidget(QLabel("Нет данных"))
            return

        max_count = max(row["cnt"] for row in rows) or 1

        for row in rows:
            line = QHBoxLayout()
            label = QLabel(str(row[0]))
            label.setMinimumWidth(120)
            bar = QProgressBar()
            bar.setMaximum(max_count)
            bar.setValue(row["cnt"])
            bar.setFormat(f"{row['cnt']}")
            line.addWidget(label)
            line.addWidget(bar)
            layout.addLayout(line)


    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Delete:
            self._delete_clothes()
        elif event.key() == Qt.Key_F5:
            self.load_clothes()
            self.load_outfits()
            self.load_stats()
        else:
            super().keyPressEvent(event)


    def closeEvent(self, event) -> None:
        self.db.close()
        event.accept()