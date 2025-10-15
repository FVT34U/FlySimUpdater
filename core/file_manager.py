import os
import hashlib
from logs.logger import Logger

def file_hash(path):
    """Возвращает SHA256 хэш файла"""
    if not os.path.exists(path):
        Logger.err(f"Cannot count file hash at: {path}, file not found")
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def ensure_dirs():
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
