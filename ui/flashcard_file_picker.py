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
    def __init__(self, files: list[dict], review_file: dict | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Flashcard Sets")
        self.resize(420, 520)
        self.checkboxes = []
        self.review_checkbox = None

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

        if review_file is not None:
            review_label = QLabel("Review file")
            review_label.setStyleSheet("font-weight: bold; margin-bottom: 4px;")
            content_layout.addWidget(review_label)

            review_checkbox = QCheckBox(f"{review_file['label']} ({review_file['file']})")
            review_checkbox.setChecked(True)
            review_checkbox.file_info = review_file
            self.review_checkbox = review_checkbox
            content_layout.addWidget(review_checkbox)

            separator = QLabel("")
            separator.setFixedHeight(8)
            content_layout.addWidget(separator)

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
        files = [checkbox.file_info for checkbox in self.checkboxes if checkbox.isChecked()]
        if self.review_checkbox is not None and self.review_checkbox.isChecked():
            files.insert(0, self.review_checkbox.file_info)
        return files

    def select_all(self):
        if self.review_checkbox is not None:
            self.review_checkbox.setChecked(True)
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)

    def deselect_all(self):
        if self.review_checkbox is not None:
            self.review_checkbox.setChecked(False)
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
