import configparser
import os
import sys
import asyncio
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QTextEdit, QMessageBox, QDialog,
    QLineEdit, QFileDialog,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from core import version_checker, updater, game_runner
from config.config import config
from logs.logger import Logger


class InstallPathDialog(QDialog):
    def __init__(self, current_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выберите папку для установки")
        self.setFixedSize(500, 180)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.selected_path = current_path

        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #E0E0E0;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QDialog {
                background-color: #1E1E1E;
                color: #E0E0E0;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QPushButton {
                background-color: #3C3C3C;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QLineEdit {
                background-color: #2A2A2A;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 4px;
                color: white;
            }
        """)

        layout = QVBoxLayout()

        label = QLabel("Выберите папку для установки FlySim:")
        layout.addWidget(label)

        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(current_path)
        self.browse_btn = QPushButton("📁 Обзор")
        self.browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)

        layout.addLayout(path_layout)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("✅ Ок")
        cancel_btn = QPushButton("❌ Отмена")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def browse_folder(self):
        Logger.log(f"Opening choose file dialog")
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку", self.selected_path)
        if folder:
            Logger.log(f"Text edit widget text setted from dialog window: {os.path.join(os.path.normpath(folder), "FlySim")}")
            self.path_edit.setText(os.path.join(os.path.normpath(folder), "FlySim"))

    def accept(self):
        Logger.log(f"Selected path setted from text edit widget")
        self.selected_path = self.path_edit.text()
        super().accept()


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


class FlySimLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlySim Центр")
        self.setFixedSize(700, 400)
        self.setWindowIcon(QIcon("icons/flysim_icon.png"))  # можно добавить свою иконку

        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #E0E0E0;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QPushButton {
                background-color: #3C3C3C;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QProgressBar {
                background-color: #2A2A2A;
                border: 1px solid #444;
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #3A8EF6;
                border-radius: 5px;
            }
            QTextEdit {
                background-color: #252526;
                border: 1px solid #3C3C3C;
                border-radius: 6px;
                color: #DCDCDC;
                font-family: Consolas;
                font-size: 13px;
            }
        """)

        self.setup_ui()

        if config.getboolean("AppInfo", "first_launch"):
            Logger.log(f"Detected first launch, showing installation window")
            self.show_installation_window()
        
        self.update_info()

    def setup_ui(self):
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # --- Левая часть (контроль лаунчера) ---
        title = QLabel("🚀 FlySim Центр")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc = QLabel("Поддержка обновлений и запуск приложения")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #AAAAAA;")

        self.check_button = QPushButton("🔄 Проверить наличие обновлений")
        self.check_button.clicked.connect(self.check_for_updates)

        self.install_button = QPushButton("⬇️ Установить обновление")
        self.install_button.clicked.connect(self.install_update)
        self.install_button.hide()

        self.local_game_dir = QLabel("Текущее расположение: ")
        self.local_game_dir.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.local_game_dir.setStyleSheet("color: #AAAAAA;")
        self.local_game_dir.setWordWrap(True)

        self.local_version_label = QLabel("Текущая версия FlySim: ")
        self.local_version_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.local_version_label.setStyleSheet("color: #AAAAAA;")

        self.launch_button = QPushButton("▶️ Запустить FlySim")
        self.launch_button.clicked.connect(self.launch_game)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.hide()

        left_layout.addWidget(title)
        left_layout.addWidget(desc)

        left_layout.addStretch()
        left_layout.addWidget(self.check_button)
        left_layout.addWidget(self.install_button)
        left_layout.addWidget(self.progress)

        left_layout.addStretch()
        left_layout.addWidget(self.local_game_dir)
        left_layout.addWidget(self.local_version_label)
        left_layout.addWidget(self.launch_button)

        # --- Правая часть (лог) ---
        log_label = QLabel("📜 Лог")
        log_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        log_label.setFont(QFont("Segoe UI", 12, QFont.Bold))

        desc_label = QLabel("Дополнительная информация")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("color: #AAAAAA;")

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)

        self.clear_button = QPushButton("🧹 Очистить Лог")
        self.clear_button.clicked.connect(self.clear_log)

        right_layout.addWidget(log_label)
        right_layout.addWidget(desc_label)
        right_layout.addWidget(self.log_view)
        right_layout.addWidget(self.clear_button)

        # --- Компоновка ---
        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 3)

        self.setLayout(main_layout)
    
    def show_installation_window(self):
        Logger.log(f"Creating PathDialog")
        dialog = InstallPathDialog(config.get("GameInfo", "local_game_dir"))
        if dialog.exec_() == QDialog.Accepted:
            Logger.log(f"Selected path: {dialog.selected_path}")
            config.set("GameInfo", "local_game_dir", os.path.normpath(dialog.selected_path))
            self.log(f"📂 Установочная папка: {dialog.selected_path}")
            config.set("AppInfo", "first_launch", "false")
            with open("config/config.ini", "w") as f:
                Logger.log(f"Writing new values to 'config.ini': local_game_dir: {dialog.selected_path}, first_launch: {False}")
                config.write(f)
        else:
            Logger.log(f"Directory choosing was rejected")
            self.log("❌ Выбор папки был отменен")
        
        self.update_info()

    def update_info(self):
        p = os.path.normpath(config.get("GameInfo", "local_game_dir"))
        vf = os.path.normpath(config.get("GameInfo", "version_file"))

        self.local_game_dir.setText(f"Текущее расположение: {p}")

        self.local_version = version_checker.get_local_version()
        if self.local_version is None:
            Logger.err(f"Cannot find local version, set it to: '0.0.0'")
            self.local_version = "0.0.0"
        self.local_version_label.setText(f"Текущая версия: {self.local_version}")

    def log(self, text):
        """Добавление текста в лог"""
        self.log_view.append(text)
        print(text)
        Logger.log(f"LogView got new text: {text}")

    def clear_log(self):
        """Очистка лога"""
        self.log_view.clear()
        Logger.log(f"LogView was cleared")

    def check_for_updates(self):
        """Проверка наличия обновлений"""
        Logger.log(f"Checking for updates")
        Logger.log(f"Trying to get local FlySim version")
        self.local_version = version_checker.get_local_version()

        if self.local_version is None:
            Logger.err(f"Cannot find local version, set it to: '0.0.0'")
            self.local_version = "0.0.0"
        Logger.log(f"Local version: {self.local_version}")
        self.log(f"🟦 Установленная версия: {self.local_version}")
        self.log("🔄 Проверка наличия обновлений...")

        self.block_all_buttons()

        Logger.log(f"Creating VersionCheckThread")
        self.async_thread = VersionCheckThread()
        self.async_thread.finished.connect(self.on_get_remote_version)
        Logger.log(f"Starting VersionCheckThread")
        self.async_thread.start()
    
    def on_get_remote_version(self, version):
        Logger.log(f"Got remote version: {version}")
        self.remote_version = version

        if self.remote_version is None:
            Logger.err(f"Remote version is None")
            Logger.err(f"Updating error, cannot get remote version from server, try again later")
            self.log("❌ Невозмодно получить версию приложения с сервера, попробуйте позже")
            QMessageBox.warning(self, "❌ Ошибка обновления", "❌ Невозможно получить версию приложения с сервера, попробуйте позже.")
            return

        if version_checker.is_update_needed(self.local_version, self.remote_version):
            Logger.log(f"New version is available: {self.remote_version}")
            self.log(f"🆕 Новая версия {self.remote_version} доступна! Нажмите 'Установить обновление' для установки!")
            Logger.log(f"Showing 'Install update' button")
            self.install_button.show()   
        else:
            Logger.log(f"Latest FlySim version is installed")
            self.log("✅ У вас установлена последняя версия FlySim.")
            QMessageBox.information(self, "🔄 Обновление", "✅ У вас уже установлена последняя версия!")
        
        self.update_info()

        self.unblock_all_buttons()

    def install_update(self):
        Logger.log(f"Updating")
        self.log("🔄 Обновление...")
        Logger.log(f"Showing progress bar")
        self.progress.show()

        self.block_all_buttons()

        Logger.log(f"Creating UpdateThread")
        self.update_thread = UpdateThread()
        self.update_thread.progress_changed.connect(self.progress.setValue)
        self.update_thread.finished.connect(self.on_update_finished)
        Logger.log(f"Starting UpdateThread")
        self.update_thread.start()

        Logger.log(f"Hiding 'Install update' button")
        self.install_button.hide()

    def on_update_finished(self, message):
        Logger.log(f"Update finished")
        self.log(message)
        Logger.log(f"Hiding progress bar")
        self.progress.hide()
        QMessageBox.information(self, "🔄 Обновление", "✅ Обновление успешно завершено!")

        self.update_info()
        self.unblock_all_buttons()

    def block_all_buttons(self):
        Logger.log(f"All buttons blocked")
        self.check_button.setDisabled(True)
        self.launch_button.setDisabled(True)
        self.clear_button.setDisabled(True)

    def unblock_all_buttons(self):
        Logger.log(f"All buttons unblocked")
        self.check_button.setDisabled(False)
        self.launch_button.setDisabled(False)
        self.clear_button.setDisabled(False)

    def launch_game(self):
        Logger.log(f"Launching FlySim")
        self.log("▶️ Запуск FlySim...")
        try:
            game_runner.run_game()
            Logger.log(f"FlySim was successfully launched")
            self.log("✅ FlySim запущен успешно.")
        except Exception as e:
            Logger.err(f"FlySim launching error: {e}")
            self.log(f"❌ Ошибка запуска приложения: {e}")
            QMessageBox.critical(self, "❌ Ошибка запуска", str(e))


def start_launcher():
    Logger.log("Starting launcher")
    app = QApplication(sys.argv)
    launcher = FlySimLauncher()
    launcher.show()
    sys.exit(app.exec_())
