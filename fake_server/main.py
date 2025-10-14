from fastapi import FastAPI
from fastapi.responses import FileResponse
import os, hashlib, json
import configparser

app = FastAPI()

GAME_DIR = "./fake_game_files"
RELEASE_FILE = "./fake_game_files/release.ini"

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

@app.get("/api/game/version")
def get_version():
    config = configparser.ConfigParser()
    config.read(RELEASE_FILE)
    return {"version": config.get("Release", "version")}

@app.get("/api/game/files")
def get_files():
    files = []
    for root, _, filenames in os.walk(GAME_DIR):
        for fn in filenames:
            rel_path = os.path.relpath(os.path.join(root, fn), GAME_DIR)
            files.append({"path": rel_path, "hash": file_hash(os.path.join(root, fn))})
    return files

@app.get("/api/game/files/{file_path:path}")
def download_file(file_path: str):
    return FileResponse(os.path.join(GAME_DIR, file_path))
