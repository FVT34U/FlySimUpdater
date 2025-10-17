import os

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from core import version_checker

from ui.style import widget_style, settings_widget_style

from core.app_model import app_model, save_model
from utils.logger import Logger


class SettingsWidget(QWidget):
    hovered = pyqtSignal(bool)

    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.setMouseTracking(True)
    
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        title = QLabel("⚙️ Настройки")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        self.local_game_dir = QLabel("Текущее расположение: ")
        self.local_game_dir.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.local_game_dir.setStyleSheet("color: #AAAAAA;")
        self.local_game_dir.setWordWrap(True)

        self.local_version_label = QLabel("Текущая версия FlySim: ")
        self.local_version_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.local_version_label.setStyleSheet("color: #AAAAAA;")

        # Компоновка
        main_layout.addWidget(title)
        main_layout.addStretch()
        main_layout.addWidget(self.local_game_dir)
        main_layout.addWidget(self.local_version_label)
        self.setLayout(main_layout)
    
    def mouseMoveEvent(self, event) -> None:
        if event.pos().x() >= self.width() - 10:
            self.hovered.emit(False)
        
        super().mouseMoveEvent(event)
    
    def update_info(self):
        p = os.path.normpath(app_model.game_path)

        self.local_game_dir.setText(f"Текущее расположение: {p}")

        self.local_version = app_model.release_version
        if self.local_version == "":
            Logger.err(f"Cannot find local version, set it to: '0.0.0'")
            self.local_version = "0.0.0"
        self.local_version_label.setText(f"Текущая версия: {self.local_version}")

class GearWidget(QWidget):
    hovered = pyqtSignal(bool)

    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.setMouseTracking(True)
    
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        gear_label = QLabel("⚙️")

        main_layout.addWidget(gear_label)
        main_layout.addStretch()

        self.setLayout(main_layout)
    
    def mouseMoveEvent(self, event) -> None:
        self.hovered.emit(True)
        super().mouseMoveEvent(event)

class SettingsDrawerWidget(QWidget):
    settings_visibility_changed = pyqtSignal(bool)

    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.setStyleSheet(settings_widget_style)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.settings_widget = SettingsWidget()
        self.settings_widget.hovered.connect(self.on_settings_widget_hovered)
        self.settings_widget.hide()

        self.gear_widget = GearWidget()
        self.gear_widget.hovered.connect(self.on_gear_widget_hovered)

        # Компоновка
        main_layout.addWidget(self.settings_widget)
        main_layout.addWidget(self.gear_widget)
        self.setLayout(main_layout)
    
    def on_gear_widget_hovered(self, value):
        if value:
            self.settings_widget.show()
            self.gear_widget.hide()

            self.settings_widget.update_info()
            self.settings_visibility_changed.emit(True)
    
    def on_settings_widget_hovered(self, value):
        if not value:
            self.settings_widget.hide()
            self.gear_widget.show()

            self.settings_visibility_changed.emit(False)
