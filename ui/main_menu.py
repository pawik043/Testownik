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


class MainMenu(QWidget):
    def __init__(self, on_select_folder, on_load_recent, on_flashcards):
        super().__init__()

        self.setObjectName("mainMenu")
        self.setStyleSheet("""
            QWidget#mainMenu {
                background: #141416;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(0)

        self.hero = QFrame()
        self.hero.setObjectName("heroPanel")
        self.hero.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.hero.setStyleSheet("""
            QFrame#heroPanel {
                background: #1c1c1e;
                border: 1px solid #2f2f33;
                border-radius: 28px;
            }
        """)

        hero_layout = QVBoxLayout(self.hero)
        hero_layout.setContentsMargins(40, 34, 40, 40)
        hero_layout.setSpacing(0)

        self.title = QLabel("Testownik")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setWordWrap(True)
        self.title.setStyleSheet("""
            QLabel {
                color: #f2f2f7;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)

        self.subtitle = QLabel(
            "Choose how you want to study and continue exactly where you left off."
        )
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet("""
            QLabel {
                color: #9a9aa1;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)

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

        self.select_btn.setStyleSheet(
            self._button_style(
                background="#2f3644",
                border="#495266",
                hover_background="#394155",
                hover_border="#5b6680",
            )
        )
        self.flashcards_btn.setStyleSheet(
            self._button_style(
                background="#2d3338",
                border="#445057",
                hover_background="#373f45",
                hover_border="#56636b",
            )
        )
        self.recent_btn.setStyleSheet(
            self._button_style(
                background="#262628",
                border="#37373b",
                hover_background="#2f2f33",
                hover_border="#47474d",
            )
        )

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

    def _button_style(
        self,
        background: str,
        border: str,
        hover_background: str,
        hover_border: str,
    ) -> str:
        return f"""
        QPushButton {{
            background: {background};
            color: #f2f2f7;
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
            background: #242427;
        }}
        """
