import os
import requests
from config.config import config

def get_local_version():
    path = os.path.join(config.get("GameInfo", "localGameDir"), config.get("GameInfo", "versionFile"))
    if not os.path.exists(path):
        return False
    with open(path, "r") as f:
        return f.read().strip()

def get_remote_version():
    r = requests.get(f"{config.get('ServerInfo', 'apiGameUrl')}/version")
    if r.status_code != 200:
        return False
    return r.json()["version"]

def is_update_needed(local_version, remote_version):
    return local_version != remote_version
