import os
import hashlib

def file_hash(path):
    """Возвращает SHA256 хэш файла"""
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def ensure_dirs():
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
