from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..widgets import FlashcardTile, ProgressWidget


class FlashcardView(QWidget):
    def __init__(self, on_return, on_reset, on_flip, on_known, on_review, on_next):
        super().__init__()

        root = QHBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(20)

        self.left = QVBoxLayout()
        self.left.setSpacing(16)

        self.return_btn = QPushButton("Return to Main Menu")
        self.return_btn.clicked.connect(on_return)

        self.reset_btn = QPushButton("Reset Session")
        self.reset_btn.clicked.connect(on_reset)

        self.timer_label = QLabel("0 min 00 sec")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setFont(QFont("Helvetica", 16, QFont.Bold))

        self.mastery_label = QLabel("0 / 0")
        self.mastery_label.setAlignment(Qt.AlignCenter)
        self.mastery_label.setFont(QFont("Helvetica", 16, QFont.Bold))

        self.counter_label = QLabel("Known: 0  Needs Review: 0")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setFont(QFont("Helvetica", 14, QFont.Bold))

        self.progress = ProgressWidget(
            None,
            self.counter_label,
            counter_labels={"correct": "Known", "wrong": "Needs Review"},
            show_partial=False,
        )

        self.left.addWidget(self.return_btn)
        self.left.addWidget(self.reset_btn)
        self.left.addStretch()
        self.left.addWidget(self.timer_label)
        self.left.addStretch()
        self.left.addWidget(self.mastery_label)
        self.left.addWidget(self.counter_label)
        self.left.addWidget(self.progress)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("color:#3a3a3c")

        self.right = QVBoxLayout()
        self.right.setSpacing(18)

        self.header_box = QFrame()
        self.header_box.setStyleSheet("""
            QFrame {
                background: #1c1c1e;
                border: 1px solid #3a3a3c;
                border-radius: 24px;
            }
        """)
        self.header_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        header_layout = QVBoxLayout(self.header_box)
        header_layout.setContentsMargins(28, 28, 28, 28)
        header_layout.setSpacing(8)

        self.question_label = QLabel("Flashcard")
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setFont(QFont("Helvetica", 22, QFont.Bold))
        self.question_label.setStyleSheet("color: #f2f2f7; background: transparent; border: none; padding: 0px; margin: 0px;")

        self.subtitle_label = QLabel("Tap the card to reveal the answer")
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setFont(QFont("Helvetica", 13))
        self.subtitle_label.setStyleSheet("color: #8e8e93; background: transparent; border: none; padding: 0px; margin: 0px;")

        header_layout.addWidget(self.question_label)
        header_layout.addWidget(self.subtitle_label)

        self.card_box = QFrame()
        self.card_box.setStyleSheet("""
            QFrame {
                background: #1c1c1e;
                border: 1px solid #3a3a3c;
                border-radius: 24px;
            }
        """)
        self.card_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        card_layout = QVBoxLayout(self.card_box)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(18)

        self.card = FlashcardTile(on_flip)

        self.actions = QHBoxLayout()
        self.actions.setSpacing(12)

        self.known_btn = QPushButton("I Knew It")
        self.known_btn.clicked.connect(on_known)

        self.review_btn = QPushButton("Needs Review")
        self.review_btn.clicked.connect(on_review)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(on_next)

        self.actions.addWidget(self.known_btn)
        self.actions.addWidget(self.review_btn)
        self.actions.addWidget(self.next_btn)

        card_layout.addWidget(self.card, 1)
        card_layout.addLayout(self.actions)

        self.right.addWidget(self.header_box)
        self.right.addWidget(self.card_box, 1)

        root.addLayout(self.left, 1)
        root.addWidget(line)
        root.addLayout(self.right, 3)
