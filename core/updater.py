import os
import requests
from core import file_manager
from config.config import config


def download_file(file_info, progress_callback=None, current_index=0, total=1):
    """Скачивает один файл"""
    url = f"{config.get('ServerInfo', 'apiGameUrl')}/files/{file_info['path']}"
    local_path = os.path.join(config.get("GameInfo", "localGameDir"), file_info['path'])
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_bytes = int(r.headers.get("content-length", 0))
        downloaded = 0

        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_bytes:
                        progress_callback((current_index + downloaded / total_bytes) / total)

def update_game(ui_callback=None):
    """Проверяет и обновляет файлы"""
    r = requests.get(f"{config.get('ServerInfo', 'apiGameUrl')}/files")
    r.raise_for_status()
    files = r.json()

    # фильтруем только изменённые файлы
    files_to_update = []
    for f in files:
        local_path = os.path.join(config.get("GameInfo", "localGameDir"), f["path"])
        local_hash = file_manager.file_hash(local_path)
        if local_hash != f["hash"]:
            files_to_update.append(f)

    total = len(files_to_update)
    for i, f in enumerate(files_to_update):
        download_file(f, progress_callback=ui_callback, current_index=i, total=total)

    # обновляем версию после завершения
    new_version = requests.get(f"{config.get('ServerInfo', 'apiGameUrl')}/version").json()["version"]
    with open(os.path.join(config.get("GameInfo", "localGameDir"), config.get("GameInfo", "versionFile")), "w") as vf:
        vf.write(new_version)
