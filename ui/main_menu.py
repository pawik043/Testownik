from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from widgets.theme import colors


class MainMenu(QWidget):
    def __init__(self, on_select_folder, on_load_recent, on_flashcards):
        super().__init__()

        self.setObjectName("mainMenu")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(0)

        self.hero = QFrame()
        self.hero.setObjectName("heroPanel")
        self.hero.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        hero_layout = QVBoxLayout(self.hero)
        hero_layout.setContentsMargins(40, 34, 40, 40)
        hero_layout.setSpacing(0)

        self.title = QLabel("Testownik")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setWordWrap(True)

        self.subtitle = QLabel(
            "Choose how you want to study and continue exactly where you left off."
        )
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)

        self.select_btn = QPushButton("Quiz Mode")
        self.select_btn.clicked.connect(on_select_folder)

        self.flashcards_btn = QPushButton("Flashcards Mode")
        self.flashcards_btn.clicked.connect(on_flashcards)

        self.recent_btn = QPushButton("Continue Last Session")
        self.recent_btn.clicked.connect(on_load_recent)

        self.buttons = [
            self.select_btn,
            self.flashcards_btn,
            self.recent_btn,
        ]

        for button in self.buttons:
            button.setMinimumHeight(88)
            button.setCursor(Qt.PointingHandCursor)
            button.setFocusPolicy(Qt.NoFocus)

        hero_layout.addStretch()
        hero_layout.addWidget(self.title)
        hero_layout.addSpacing(10)
        hero_layout.addWidget(self.subtitle)
        hero_layout.addSpacing(36)
        hero_layout.addWidget(self.select_btn)
        hero_layout.addSpacing(18)
        hero_layout.addWidget(self.flashcards_btn)
        hero_layout.addSpacing(18)
        hero_layout.addWidget(self.recent_btn)
        hero_layout.addStretch()

        layout.addWidget(self.hero)

        self._update_fonts()
        self.refresh_theme()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_fonts()

    def _update_fonts(self):
        width = max(900, self.width())
        height = max(650, self.height())
        scale_base = min(width, height)

        title_size = min(max(int(scale_base * 0.055), 30), 54)
        subtitle_size = min(max(int(scale_base * 0.018), 12), 18)
        button_size = min(max(int(scale_base * 0.024), 16), 26)

        self.title.setFont(QFont("Helvetica", title_size, QFont.Bold))
        self.subtitle.setFont(QFont("Helvetica", subtitle_size))

        for button in self.buttons:
            button.setFont(QFont("Helvetica", button_size, QFont.Bold))

    def refresh_theme(self):
        palette = colors()
        self.setStyleSheet(f"""
            QWidget#mainMenu {{
                background: {palette["window"]};
            }}
        """)
        self.hero.setStyleSheet(f"""
            QFrame#heroPanel {{
                background: {palette["panel"]};
                border: 1px solid {palette["panel_border"]};
                border-radius: 28px;
            }}
        """)
        self.title.setStyleSheet(f"""
            QLabel {{
                color: {palette["text"]};
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }}
        """)
        self.subtitle.setStyleSheet(f"""
            QLabel {{
                color: {palette["muted_text"]};
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }}
        """)
        self.select_btn.setStyleSheet(
            self._button_style(
                background=palette["button_primary"],
                border=palette["button_primary_border"],
                hover_background=palette["button_primary_hover"],
                hover_border=palette["button_primary_hover_border"],
                pressed_background=palette["button_pressed"],
                text=palette["button_text"],
            )
        )
        self.flashcards_btn.setStyleSheet(
            self._button_style(
                background=palette["button_secondary"],
                border=palette["button_secondary_border"],
                hover_background=palette["button_secondary_hover"],
                hover_border=palette["button_secondary_hover_border"],
                pressed_background=palette["button_pressed"],
                text=palette["button_text"],
            )
        )
        self.recent_btn.setStyleSheet(
            self._button_style(
                background=palette["button_neutral"],
                border=palette["button_neutral_border"],
                hover_background=palette["button_neutral_hover"],
                hover_border=palette["button_neutral_hover_border"],
                pressed_background=palette["button_pressed"],
                text=palette["button_text"],
            )
        )

    def _button_style(
        self,
        background: str,
        border: str,
        hover_background: str,
        hover_border: str,
        pressed_background: str,
        text: str,
    ) -> str:
        return f"""
        QPushButton {{
            background: {background};
            color: {text};
            border: 1px solid {border};
            border-radius: 22px;
            padding: 20px 24px;
            text-align: center;
            outline: none;
        }}
        QPushButton:hover {{
            background: {hover_background};
            border: 1px solid {hover_border};
        }}
        QPushButton:focus {{
            background: {background};
            border: 1px solid {border};
            outline: none;
        }}
        QPushButton:pressed {{
            background: {pressed_background};
        }}
        """
