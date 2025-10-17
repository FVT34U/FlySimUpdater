import os, sys

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QTextEdit, QMessageBox, QDialog, QSpacerItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from core import version_checker, game_runner
from core.app_model import app_model, load_model, save_model
from utils.logger import Logger

from ui.threads import UpdateThread, VersionCheckThread
from ui.install_path_dialog import InstallPathDialog
from ui.settings_widget import SettingsDrawerWidget
from ui.style import widget_style


class FlySimLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlySim Центр")
        self.setFixedSize(700, 400)
        self.setWindowIcon(QIcon("icons/flysim_icon.png"))

        self.setStyleSheet(widget_style)

        self.drawer_shown = False

        self.setup_ui()

        if not os.path.exists(app_model.game_path):
            Logger.log(f"Detected first launch, showing installation window")
            self.show_installation_window()

        self.setMouseTracking(True)

    def setup_ui(self):
        self.main_layout = QHBoxLayout()
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
        left_layout.addWidget(self.launch_button)

        # --- Правая часть (лог) ---
        log_label = QLabel("📜 Лог")
        log_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        log_label.setFont(QFont("Segoe UI", 16, QFont.Bold))

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

        # Настройки
        settings_widget = SettingsDrawerWidget()
        settings_widget.settings_visibility_changed.connect(self.on_settings_visibility_changed)

        # Компоновка
        self.main_layout.addWidget(settings_widget)
        self.main_layout.addLayout(left_layout, 1)
        self.main_layout.addLayout(right_layout, 1)

        self.setLayout(self.main_layout)
    
    def on_settings_visibility_changed(self, value: bool):
        if value: 
            self.drawer_shown = True
            Logger.log("Drawer was shown")
        else:
            self.drawer_shown = False
            Logger.log("Drawer was hidden")

    def show_installation_window(self):
        Logger.log(f"Creating InstallPathDialog")
        dialog = InstallPathDialog(app_model.game_path)

        if dialog.exec() == 1:
            Logger.log(f"Selected path: {dialog.selected_path}")
            app_model.game_path = os.path.normpath(dialog.selected_path)
            self.log(f"📂 Установочная папка: {dialog.selected_path}")
            save_model()
        else:
            Logger.log(f"Directory choosing was rejected")
            self.log("❌ Выбор папки был отменен")

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
        self.local_version = app_model.release_version

        if self.local_version == "":
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
            self.unblock_all_buttons()
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
    load_model()
    app = QApplication(sys.argv)
    launcher = FlySimLauncher()
    launcher.show()
    sys.exit(app.exec_())
