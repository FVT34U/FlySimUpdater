import os
import requests
from requests import HTTPError
from utils.config import config
from utils.logger import Logger

import configparser

cfg = configparser.ConfigParser(interpolation=None)

def get_local_version():
    path = os.path.join(config.get("GameInfo", "local_game_dir"), config.get("GameInfo", "version_file"))
    if not os.path.exists(path):
        Logger.err(f"Cannot find 'release.ini' file at {path}")
        return None
    
    cfg.read(path)
    ver = cfg.get("Release", "version")
    Logger.log(f"Local FlySim version is: {ver}")
    return ver

def get_remote_version():
    Logger.log(f"Trying get version from server")
    try:
        r = requests.get(f"{config.get('ServerInfo', 'api_game_url')}/version")
        r.raise_for_status()
        ver = r.json()["version"]
        Logger.log(f"Remote FlySim version is: {ver}")
        return ver
    except HTTPError as e:
        Logger.err(f"Cannot get remote version from server: {e}")
        return None
    except Exception as e:
        Logger.err(f"Unexpected error: {e}")
        return None

def is_update_needed(local_version, remote_version):
    Logger.log(f"Is update needed: {local_version != remote_version}")
    return local_version != remote_version
