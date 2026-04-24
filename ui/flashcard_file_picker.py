from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class FlashcardFilePickerDialog(QDialog):
    def __init__(self, files: list[dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Flashcard Sets")
        self.resize(420, 520)
        self.checkboxes = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        description = QLabel("Choose which CSV files should be included in the flashcards session.")
        description.setWordWrap(True)
        layout.addWidget(description)

        actions = QHBoxLayout()

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all)

        actions.addWidget(select_all_btn)
        actions.addWidget(deselect_all_btn)
        actions.addStretch()
        layout.addLayout(actions)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        for file_info in files:
            checkbox = QCheckBox(file_info["label"])
            checkbox.setChecked(True)
            checkbox.file_info = file_info
            self.checkboxes.append(checkbox)
            content_layout.addWidget(checkbox)

        content_layout.addStretch()
        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_files(self) -> list[dict]:
        return [checkbox.file_info for checkbox in self.checkboxes if checkbox.isChecked()]

    def select_all(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)

    def deselect_all(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
