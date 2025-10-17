from PyQt5.QtCore import QThread, pyqtSignal

from utils.logger import Logger
from core import updater, version_checker


class UpdateThread(QThread):
    """Фоновый поток для обновления приложения."""
    progress_changed = pyqtSignal(int)
    finished = pyqtSignal(str)

    def run(self):
        Logger.log(f"UpdateThread is running")
        updater.update_game(ui_callback=self.update_progress)
        self.finished.emit("✅ Обновление установлено!")

    def update_progress(self, value):
        Logger.log(f"UpdateThread updating progress: {value} or {int(value * 100)}")
        self.progress_changed.emit(int(value * 100))


class VersionCheckThread(QThread):
    """Фоновый поток для запроса версии с сервера"""
    finished = pyqtSignal(object)

    def run(self):
        Logger.log(f"VersionCheckThread is running")
        self.finished.emit(version_checker.get_remote_version())