import os
import sys

CATEGORIES = [
    "Верхняя одежда",
    "Футболки и топы",
    "Брюки и джинсы",
    "Юбки и платья",
    "Обувь",
    "Аксессуары",
]

COLORS = [
    "Чёрный",
    "Белый",
    "Серый",
    "Бежевый",
    "Коричневый",
    "Красный",
    "Розовый",
    "Синий",
    "Зелёный",
    "Жёлтый",
]

SEASONS = ["Весна", "Лето", "Осень", "Зима", "Всесезон"]


def _base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))


def _resource_dir() -> str:
    return getattr(sys, "_MEIPASS", _base_dir())


BASE_DIR = _base_dir()
RESOURCE_DIR = _resource_dir()

DB_PATH = os.path.join(BASE_DIR, "database", "wardrobe.db")
CLOTHES_IMAGES_DIR = os.path.join(BASE_DIR, "assets", "clothes")

PLACEHOLDER_IMAGE = os.path.join(RESOURCE_DIR, "assets", "placeholder.png")
STYLE_PATH = os.path.join(RESOURCE_DIR, "styles", "style.qss")