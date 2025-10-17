import os

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QDialog, QLineEdit, QFileDialog
)
from PyQt5.QtCore import Qt

from utils.logger import Logger

from ui.style import widget_style


class InstallPathDialog(QDialog):
    def __init__(self, current_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выберите папку для установки")
        self.setFixedSize(500, 180)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.selected_path = current_path

        self.setStyleSheet(widget_style)

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
    
    def reject(self) -> None:
        print("reject")
        super().reject()