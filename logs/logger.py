from datetime import datetime
import os
from config.config import config
import configparser

class Logger:
    path = f"logs/log_{str(datetime.now()).split(".")[0].replace(" ", "_").replace(":", "-")}.txt"
    with open(path, "x", encoding="utf-8") as f:
        p = os.path.join(config.get("GameInfo", "local_game_dir"), config.get("GameInfo", "version_file"))
        if os.path.exists(p):
            cfg = configparser.ConfigParser(interpolation=None)
            cfg.read(p)
            f.write(f"[{str(datetime.now()).split(".")[0]}] Flysim v.{cfg.get("Release", "version")} opened!\n")
        else:
            f.write(f"[{str(datetime.now()).split(".")[0]}][ERROR] Cannot find 'release.ini' file at {p}\n")

    @staticmethod
    def log(text: str):
        ftext = f"[{str(datetime.now()).split(".")[0]}] {text}\n"
        print(ftext)
        with open(Logger.path, "a", encoding="utf-8") as f:
            f.write(ftext)
    
    @staticmethod
    def err(text: str):
        ftext = f"[{str(datetime.now()).split(".")[0]}][ERROR] {text}\n"
        print(ftext)
        with open(Logger.path, "a", encoding="utf-8") as f:
            f.write(ftext)