from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtCore import Qt


class AnswerBox(QFrame):
    def __init__(self, text: str, index: int, callback):
        super().__init__()
        self.index = index
        self.callback = callback
        self.selected = False

        self.setStyleSheet(self.default_style())
        self.setMinimumHeight(110)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            """
            color: #e5e5e7;
            font-size: 16px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
            """
        )

        layout.addWidget(self.label)
        self.setLayout(layout)

    def default_style(self) -> str:
        return """
        QFrame {
            background: #2c2c2e;
            border-radius: 22px;
            border: 2px solid transparent;
            padding: 16px;
        }
        QLabel {
            color: #e5e5e7;
            font-size: 16px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }
        """

    def selected_style(self) -> str:
        return """
        QFrame {
            background: #0a84ff33;
            border-radius: 22px;
            border: 2px solid #0a84ff;
            padding: 16px;
        }
        QLabel {
            color: #e5e5e7;
            font-size: 16px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }
        """

    def mousePressEvent(self, event):
        if not self.isEnabled():
            return

        self.selected = not self.selected
        self.setStyleSheet(self.selected_style() if self.selected else self.default_style())
        self.callback(self.index, self.selected)

    def mark_correct(self):
        self.selected = False
        self.setStyleSheet(
            """
            QFrame {
                background: #30d158;
                border-radius: 22px;
                border: 2px solid transparent;
                padding: 16px;
            }
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: 600;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
            """
        )

    def mark_wrong(self):
        self.selected = False
        self.setStyleSheet(
            """
            QFrame {
                background: #ff453a;
                border-radius: 22px;
                border: 2px solid transparent;
                padding: 16px;
            }
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: 600;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
            """
        )

    def mark_missing(self):
        self.selected = False
        self.setStyleSheet(
            """
            QFrame {
                background: #ffd60a;
                border-radius: 22px;
                border: 2px solid transparent;
                padding: 16px;
            }
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: 600;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
            """
        )