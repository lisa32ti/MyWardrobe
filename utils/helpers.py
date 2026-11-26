import os
import shutil
import uuid

from constants import CLOTHES_IMAGES_DIR


def ensure_dirs() -> None:
    os.makedirs(CLOTHES_IMAGES_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.join(CLOTHES_IMAGES_DIR, "..", "database")), exist_ok=True)


def copy_image_to_storage(source_path: str) -> str:
    if not source_path or not os.path.isfile(source_path):
        return ""

    ext = os.path.splitext(source_path)[1].lower() or ".png"
    new_name = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(CLOTHES_IMAGES_DIR, new_name)
    shutil.copy2(source_path, dest)
    return new_name


def delete_image_if_exists(image_name: str) -> None:
    if not image_name:
        return
    path = os.path.join(CLOTHES_IMAGES_DIR, image_name)
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            pass