from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFont, QPainterPath
from PySide6.QtCore import Qt


class ProgressWidget(QWidget):
    def __init__(self, state=None, counter_label=None):
        super().__init__()
        self.state = state
        self.counter_label = counter_label
        self.setFixedHeight(30)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.state:
            return

        statuses = list(self.state.get("status", {}).values())
        total = len(statuses)
        if total == 0:
            return

        correct = sum(1 for s in statuses if s == "correct")
        partial = sum(1 for s in statuses if s == "partial")
        wrong = sum(1 for s in statuses if s == "wrong")
        answered = correct + partial + wrong

        w = self.width()
        h = self.height()
        radius = h / 2

        painter.setPen(Qt.NoPen)

        painter.setBrush(QColor("#3a3a3c"))
        painter.drawRoundedRect(0, 0, w, h, radius, radius)

        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, radius, radius)
        painter.setClipPath(path)

        if answered > 0:
            correct_w = w * correct / answered
            partial_w = w * partial / answered
            wrong_w = w * wrong / answered

            x = 0

            if correct_w > 0:
                painter.setBrush(QColor("#30d158"))
                painter.drawRect(x, 0, correct_w, h)
                x += correct_w

            if partial_w > 0:
                painter.setBrush(QColor("#ff9f0a"))
                painter.drawRect(x, 0, partial_w, h)
                x += partial_w

            if wrong_w > 0:
                painter.setBrush(QColor("#ff453a"))
                painter.drawRect(x, 0, w - x, h)

        painter.setClipping(False)

        if self.counter_label:
            self.counter_label.setText(
                f"Correct: {correct}  Partial: {partial}  Wrong: {wrong}"
            )
            self.counter_label.setFont(QFont("Helvetica", 12, QFont.Bold))