import os
import requests
from requests import HTTPError
from core.app_model import app_model
from utils.logger import Logger


def get_remote_version():
    Logger.log(f"Trying get version from server")
    try:
        r = requests.get(f"{app_model.api_game_url}/version")
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
