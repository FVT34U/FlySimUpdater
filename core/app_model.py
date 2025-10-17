import json
import os, sys

from pydantic import BaseModel

class AppModel(BaseModel):
    api_url: str = ""
    api_game_suffix: str = "game"
    api_app_suffix: str = "app"
    api_game_url: str = ""
    api_app_url: str = ""

    game_path: str = ""
    game_exe_name: str = "Blocks.exe"
    game_exe_path: str = ""

    release_file_name: str = "release.ini"
    release_file_path: str = ""
    release_version: str = "0.0.0"
    release_description: str = ""


def get_cfg_dir():
    """Возвращает корректный путь к папке cfg — и при разработке, и в собранном .exe"""
    if hasattr(sys, "_MEIPASS"):
        # Приложение запущено из exe (PyInstaller)
        base_path = os.path.dirname(sys.executable)
    else:
        # Обычный запуск из исходников
        base_path = os.path.abspath(".")

    cfg_dir = os.path.join(base_path, "config")
    os.makedirs(cfg_dir, exist_ok=True)

    return cfg_dir


app_model = AppModel()
config_path = os.path.join(get_cfg_dir(), "config.json")


def connect_paths():
    global app_model, config_path

    app_model.api_game_url = f"{app_model.api_url}/{app_model.api_game_suffix}"
    app_model.api_app_url = f"{app_model.api_url}/{app_model.api_app_suffix}"

    app_model.game_exe_path = os.path.join(app_model.game_path, app_model.game_exe_name)
    app_model.release_file_path = os.path.join(app_model.game_path, app_model.release_file_name)


def load_model():
    global app_model, config_path

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            app_model = AppModel.model_validate(json.load(f))
        connect_paths()
    else:
        save_model()


def save_model():
    global app_model, config_path

    connect_paths()

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(app_model.model_dump_json(indent=4, ensure_ascii=False))