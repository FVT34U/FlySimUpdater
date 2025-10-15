import os
import requests
from requests import HTTPError
from core import file_manager
from utils.config import config
from utils.logger import Logger


def download_file(file_info, progress_callback=None, current_index=0, total=1):
    """Скачивает один файл"""
    url = f"{config.get('ServerInfo', 'api_game_url')}/files/{file_info['path']}"
    Logger.log(f"File's server url: {url}")

    local_path = os.path.join(config.get("GameInfo", "local_game_dir"), file_info['path'])
    Logger.log(f"File's local path: {local_path}")

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    Logger.log(f"Directory {os.path.dirname(local_path)} created")

    Logger.log(f"Trying to open file stream by url")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_bytes = int(r.headers.get("content-length", 0))
            downloaded = 0
            Logger.log(f"Downloaded elements: {downloaded}")

            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_bytes:
                            progress_callback((current_index + downloaded / total_bytes) / total)
    except HTTPError as e:
        Logger.err(f"Cannot get file from server, HTTP exception: {e}, status code: {r.status_code}")
    except Exception as e:
        Logger.err(f"Unexpected error: {e}")

def update_game(ui_callback=None):
    """Проверяет и обновляет файлы"""
    try:
        r = requests.get(f"{config.get('ServerInfo', 'api_game_url')}/files")
        r.raise_for_status()
        files = r.json()
        Logger.log(f"Got files from server: {files}")
    except HTTPError as e:
        Logger.err(f"Cannot update game, HTTP exception: {e}, status code: {r.status_code}")
    except Exception as e:
        Logger.err(f"Unexpected error: {e}")

    game_dir = config.get("GameInfo", "local_game_dir")
    # Пути всех файлов, которые должны существовать (нормализуем для ОС)
    all_files_paths = [os.path.normpath(os.path.join(game_dir, f["path"])) for f in files]

    # Собираем все локальные файлы в папке игры
    Logger.log("Deleting all irrelevant local files")
    for root, dirs, filenames in os.walk(game_dir):
        for name in filenames:
            local_path = os.path.normpath(os.path.join(root, name))
            # Если файла нет в списке из JSON — удаляем
            if local_path not in all_files_paths:
                try:
                    os.remove(local_path)
                    Logger.log(f"File was deleted: {local_path}")
                except Exception as e:
                    Logger.err(f"Cannot delete file {local_path}: {e}")

    # (опционально) удаляем пустые папки
    Logger.log("Deleting all irrelevant local directories")
    for root, dirs, files_in_dir in os.walk(game_dir, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root, d)
            if not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path)
                    Logger.log(f"Empty directory was deleted: {dir_path}")
                except Exception as e:
                    Logger.err(f"Cannot delete directory {dir_path}: {e}")

    # фильтруем только изменённые файлы
    Logger.log("Filtering changed files")
    files_to_update = []
    for f in files:
        local_path = os.path.join(game_dir, f["path"])
        local_hash = file_manager.file_hash(local_path)
        if local_hash != f["hash"]:
            Logger.log(f"File '{f['path']}' will be dowloaded from server")
            files_to_update.append(f)

    total = len(files_to_update)
    for i, f in enumerate(files_to_update):
        Logger.log(f"Downloading file '{f['path']}'")
        download_file(f, progress_callback=ui_callback, current_index=i, total=total)
        Logger.log(f"File '{f['path']}' was downloaded!")
