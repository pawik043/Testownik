from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

from .theme import colors


class AnswerBox(QFrame):
    def __init__(self, text: str, index: int, callback):
        super().__init__()
        self.index = index
        self.callback = callback
        self.selected = False
        self.visual_state = "default"

        self.setStyleSheet(self.default_style())
        self.setMinimumHeight(110)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            f"""
            color: {colors()["text"]};
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
        c = colors()
        return f"""
        QFrame {{
            background: {c["tile"]};
            border-radius: 22px;
            border: 2px solid transparent;
            padding: 16px;
        }}
        QLabel {{
            color: {c["text"]};
            font-size: 16px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }}
        """

    def selected_style(self) -> str:
        c = colors()
        return f"""
        QFrame {{
            background: {c["selected_bg"]};
            border-radius: 22px;
            border: 2px solid {c["selected_border"]};
            padding: 16px;
        }}
        QLabel {{
            color: {c["selected_text"]};
            font-size: 16px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }}
        """

    def mousePressEvent(self, event):
        if not self.isEnabled():
            return

        self.selected = not self.selected
        self.visual_state = "selected" if self.selected else "default"
        self.setStyleSheet(self.selected_style() if self.selected else self.default_style())
        self.callback(self.index, self.selected)

    def mark_correct(self):
        self.selected = False
        self.visual_state = "correct"
        self.refresh_theme()

    def mark_wrong(self):
        self.selected = False
        self.visual_state = "wrong"
        self.refresh_theme()

    def mark_missing(self):
        self.selected = False
        self.visual_state = "missing"
        self.refresh_theme()

    def refresh_theme(self):
        if self.visual_state == "selected":
            self.setStyleSheet(self.selected_style())
        elif self.visual_state == "correct":
            self.setStyleSheet(self.result_style("correct"))
        elif self.visual_state == "wrong":
            self.setStyleSheet(self.result_style("wrong"))
        elif self.visual_state == "missing":
            self.setStyleSheet(self.result_style("partial"))
        else:
            self.setStyleSheet(self.default_style())

    def result_style(self, color_key: str) -> str:
        c = colors()
        return f"""
        QFrame {{
            background: {c[color_key]};
            border-radius: 22px;
            border: 2px solid transparent;
            padding: 16px;
        }}
        QLabel {{
            color: {c["result_text"]};
            font-size: 16px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }}
        """
