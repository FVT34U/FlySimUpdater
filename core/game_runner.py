import subprocess
import os
from core.app_model import app_model
from utils.logger import Logger

def run_game():
    exe_path = app_model.game_exe_path

    if os.path.exists(exe_path):
        subprocess.Popen([exe_path], cwd=app_model.game_path)
    else:
        Logger.err(f"Cannot run .exe at {exe_path}, file not found")
        raise FileNotFoundError(f"Cannot run .exe at {exe_path}, file not found")