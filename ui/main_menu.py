from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class MainMenu(QWidget):
    def __init__(self, on_select_folder, on_load_recent, on_flashcards):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Testownik")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Helvetica", 26, QFont.Bold))

        select_btn = QPushButton("Select Question Folder")
        select_btn.clicked.connect(on_select_folder)

        recent_btn = QPushButton("Load Recent Folder")
        recent_btn.clicked.connect(on_load_recent)

        flashcards_btn = QPushButton("Flashcards Mode")
        flashcards_btn.clicked.connect(on_flashcards)

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(select_btn)
        layout.addWidget(recent_btn)
        layout.addWidget(flashcards_btn)
        layout.addStretch()
