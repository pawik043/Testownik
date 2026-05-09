from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFont, QPainterPath
from PySide6.QtCore import Qt

from .theme import colors


class ProgressWidget(QWidget):
    def __init__(self, state=None, counter_label=None, counter_labels=None, show_partial=True):
        super().__init__()
        self.state = state
        self.counter_label = counter_label
        self.counter_labels = counter_labels or {
            "correct": "Correct",
            "partial": "Partial",
            "wrong": "Wrong",
        }
        self.show_partial = show_partial
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
        palette = colors()

        painter.setPen(Qt.NoPen)

        painter.setBrush(QColor(palette["progress_track"]))
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
                painter.setBrush(QColor(palette["correct"]))
                painter.drawRect(x, 0, correct_w, h)
                x += correct_w

            if partial_w > 0:
                painter.setBrush(QColor(palette["partial"]))
                painter.drawRect(x, 0, partial_w, h)
                x += partial_w

            if wrong_w > 0:
                painter.setBrush(QColor(palette["wrong"]))
                painter.drawRect(x, 0, w - x, h)

        painter.setClipping(False)

        if self.counter_label:
            if self.show_partial:
                self.counter_label.setText(
                    f'{self.counter_labels["correct"]}: {correct}  '
                    f'{self.counter_labels["partial"]}: {partial}  '
                    f'{self.counter_labels["wrong"]}: {wrong}'
                )
            else:
                self.counter_label.setText(
                    f'{self.counter_labels["correct"]}: {correct}  '
                    f'{self.counter_labels["wrong"]}: {wrong}'
                )
            self.counter_label.setFont(QFont("Helvetica", 12, QFont.Bold))
