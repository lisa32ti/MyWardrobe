import sys
import os
from PyQt5.QtWidgets import QApplication
from windows.main_window import MainWindow
from constants import STYLE_PATH
from utils.helpers import ensure_dirs

def main():
    ensure_dirs()

    app = QApplication(sys.argv)

    if os.path.exists(STYLE_PATH):
        with open(STYLE_PATH, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Файл стилей не найден: {STYLE_PATH}")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()