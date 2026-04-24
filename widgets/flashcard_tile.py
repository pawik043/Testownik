from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class FlashcardTile(QFrame):
    def __init__(self, on_click):
        super().__init__()
        self.on_click = on_click
        self.revealed = False

        self.setMinimumHeight(320)
        self.setStyleSheet(self._front_style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(12)

        self.label = QLabel("Flashcard")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            """
            color: #f2f2f7;
            font-size: 22px;
            font-weight: 700;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
            """
        )
        layout.addWidget(self.label)

    def _front_style(self) -> str:
        return """
        QFrame {
            background: #2c2c2e;
            border-radius: 24px;
            border: 2px solid #3a3a3c;
        }
        """

    def _back_style(self) -> str:
        return """
        QFrame {
            background: #0a84ff22;
            border-radius: 24px;
            border: 2px solid #0a84ff;
        }
        """

    def set_text(self, text: str, revealed: bool = False):
        self.revealed = revealed
        self.label.setText(text)
        self.setStyleSheet(self._back_style() if revealed else self._front_style())

    def mousePressEvent(self, event):
        if not self.isEnabled():
            return

        self.on_click()
