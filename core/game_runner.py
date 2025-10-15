import subprocess
import os
from utils.config import config
from utils.logger import Logger

def run_game():
    exe_path = os.path.join(config.get("GameInfo", "local_game_dir"), config.get("GameInfo", "game_exe"))

    if os.path.exists(exe_path):
        subprocess.Popen([exe_path], cwd=config.get("GameInfo", "local_game_dir"))
    else:
        Logger.err(f"Cannot run .exe at {exe_path}, file not found")
        raise FileNotFoundError(f"Cannot run .exe at {exe_path}, file not found")