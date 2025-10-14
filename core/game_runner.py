import subprocess
import os
from config.config import config

def run_game():
    exe_path = os.path.join(config.get("GameInfo", "localGameDir"), config.get("GameInfo", "gameExe"))
    subprocess.Popen([exe_path], cwd=config.get("GameInfo", "localGameDir"))