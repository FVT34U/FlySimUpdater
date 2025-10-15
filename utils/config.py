import configparser
import os, sys


def get_cfg_dir():
    """Возвращает корректный путь к папке cfg — и при разработке, и в собранном .exe"""
    if hasattr(sys, "_MEIPASS"):
        # Приложение запущено из exe (PyInstaller)
        base_path = os.path.dirname(sys.executable)
    else:
        # Обычный запуск из исходников
        base_path = os.path.abspath(".")

    cfg_dir = os.path.join(base_path, "config")
    os.makedirs(cfg_dir, exist_ok=True)  # создаём, если нет
    return cfg_dir

config = configparser.ConfigParser(interpolation=None)
config.read(f"{get_cfg_dir()}/config.ini")