from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class FlashcardTile(QFrame):
    def __init__(self, on_click):
        super().__init__()
        self.on_click = on_click
        self.revealed = False
        self.current_text = "Flashcard"
        self.base_font_family = "Helvetica"
        self.base_font_weight = QFont.Bold
        self.min_font_size = 18

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
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
            """
        )
        layout.addWidget(self.label)
        self._update_font_size()

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
        self.current_text = text or ""
        self.label.setText(self.current_text)
        self.setStyleSheet(self._back_style() if revealed else self._front_style())
        self._update_font_size()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_font_size()

    def _update_font_size(self):
        available_width = max(120, self.label.width() or self.width() - 56)
        available_height = max(120, self.label.height() or self.height() - 56)
        dynamic_max_font_size = max(
            self.min_font_size,
            min(
                int(available_height * 0.22),
                int(available_width * 0.12),
                120,
            ),
        )

        best_size = self.min_font_size

        for font_size in range(dynamic_max_font_size, self.min_font_size - 1, -1):
            font = QFont(self.base_font_family, font_size, self.base_font_weight)
            metrics = QFontMetrics(font)
            bounds = metrics.boundingRect(
                QRect(0, 0, available_width, available_height),
                Qt.AlignCenter | Qt.TextWordWrap,
                self.current_text,
            )

            if bounds.width() <= available_width and bounds.height() <= available_height:
                best_size = font_size
                break

        self.label.setFont(QFont(self.base_font_family, best_size, self.base_font_weight))

    def mousePressEvent(self, event):
        if not self.isEnabled():
            return

        self.on_click()
