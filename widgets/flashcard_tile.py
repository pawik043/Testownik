import math

from PySide6.QtCore import Qt, QRect, QTimer
from PySide6.QtGui import QColor, QFont, QFontMetrics
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from .theme import colors, is_dark_mode


class FlashcardTile(QFrame):
    def __init__(self, on_click):
        super().__init__()
        self.on_click = on_click
        self.revealed = False
        self.current_text = "Flashcard"
        self.base_font_family = "Helvetica"
        self.base_font_weight = QFont.Bold
        self.min_font_size = 18
        self.feedback_timer = None
        self.feedback_step = 0
        self.feedback_steps = 30
        self.feedback_done = None

        self.setMinimumHeight(320)
        self.setStyleSheet(self._front_style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(12)

        self.label = QLabel("Flashcard")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            f"""
            color: {colors()["text"]};
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
            """
        )
        layout.addWidget(self.label)
        self._update_font_size()

    def _front_style(self) -> str:
        c = colors()
        return self._tile_style(c["tile"], c["tile_border"])

    def _back_style(self) -> str:
        c = colors()
        return self._tile_style(c["selected_bg"], c["selected_border"])

    def _tile_style(self, background: str, border: str) -> str:
        return f"""
        QFrame {{
            background: {background};
            border-radius: 24px;
            border: 2px solid {border};
        }}
        """

    def set_text(self, text: str, revealed: bool = False):
        self.revealed = revealed
        self.current_text = text or ""
        self.label.setText(self.current_text)
        self.refresh_theme()
        self._update_font_size()

    def refresh_theme(self):
        if self.feedback_timer is not None and self.feedback_timer.isActive():
            return

        self.setStyleSheet(self._back_style() if self.revealed else self._front_style())
        self.label.setStyleSheet(
            f"""
            color: {colors()["text"]};
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
            """
        )

    def play_feedback(self, status: str, on_finished=None, duration_ms: int = 500):
        if self.feedback_timer is not None:
            self.feedback_timer.stop()

        self.feedback_step = 0
        self.feedback_done = on_finished
        self.feedback_steps = 30
        interval = max(1, duration_ms // self.feedback_steps)
        target_key = "correct" if status == "correct" else "wrong"

        self.feedback_timer = QTimer(self)
        self.feedback_timer.timeout.connect(lambda: self._advance_feedback(target_key))
        self.feedback_timer.start(interval)

    def _advance_feedback(self, target_key: str):
        self.feedback_step += 1
        progress = min(1.0, self.feedback_step / self.feedback_steps)
        strength = 0.5 - 0.5 * math.cos(2 * math.pi * progress)

        background_start, background_end, border_start, border_end = self._feedback_colors(target_key)
        background = self._mix_color(background_start, background_end, strength)
        border = self._mix_color(border_start, border_end, strength)
        self.setStyleSheet(self._tile_style(background, border))

        if self.feedback_step >= self.feedback_steps:
            self.feedback_timer.stop()
            self.refresh_theme()
            done = self.feedback_done
            self.feedback_done = None
            if done is not None:
                done()

    def _mix_color(self, start: str, end: str, amount: float) -> str:
        start_color = QColor(start)
        end_color = QColor(end)
        amount = max(0.0, min(1.0, amount))
        red = round(start_color.red() + (end_color.red() - start_color.red()) * amount)
        green = round(start_color.green() + (end_color.green() - start_color.green()) * amount)
        blue = round(start_color.blue() + (end_color.blue() - start_color.blue()) * amount)
        return QColor(red, green, blue).name()

    def _feedback_colors(self, target_key: str):
        if is_dark_mode():
            if target_key == "correct":
                return "#173820", "#2f7d46", "#30d158", "#30d158"
            return "#3a1716", "#8f2520", "#ff453a", "#ff453a"

        if target_key == "correct":
            return "#eefbf1", "#b9efc5", "#34c759", "#34c759"

        return "#fff0ef", "#ffc8c4", "#ff453a", "#ff453a"

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
