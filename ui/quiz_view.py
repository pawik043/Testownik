from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QSizePolicy
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from widgets.theme import colors, panel_style, transparent_label_style
from widgets import ProgressWidget


class QuizView(QWidget):
    def __init__(self, on_return, on_reset, on_submit):
        super().__init__()

        self.setObjectName("quizView")

        root = QHBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(20)

        # ---------- Left panel ----------
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

        self.counter_label = QLabel("Correct: 0  Partial: 0  Wrong: 0")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setFont(QFont("Helvetica", 14, QFont.Bold))

        self.progress = ProgressWidget(None, self.counter_label)

        self.left.addWidget(self.return_btn)
        self.left.addWidget(self.reset_btn)
        self.left.addStretch()
        self.left.addWidget(self.timer_label)
        self.left.addStretch()
        self.left.addWidget(self.mastery_label)
        self.left.addWidget(self.counter_label)
        self.left.addWidget(self.progress)

        # ---------- Divider ----------
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.VLine)

        # ---------- Right panel ----------
        self.right = QVBoxLayout()
        self.right.setSpacing(18)

        # Question box
        self.question_box = QFrame()
        self.question_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        question_layout = QVBoxLayout(self.question_box)
        question_layout.setContentsMargins(28, 28, 28, 28)
        question_layout.setSpacing(0)
        self.question_box.setFrameShape(QFrame.NoFrame)

        self.question_label = QLabel("Question")
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setFont(QFont("Helvetica", 22, QFont.Bold))
        question_layout.addWidget(self.question_label)

        # Answers box
        self.answers_box = QFrame()
        self.answers_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        answers_layout = QVBoxLayout(self.answers_box)
        answers_layout.setContentsMargins(24, 24, 24, 24)
        answers_layout.setSpacing(18)

        self.answers = QGridLayout()
        self.answers.setSpacing(12)
        self.answers.setColumnStretch(0, 1)
        self.answers.setColumnStretch(1, 1)

        self.submit_btn = QPushButton("Check")
        self.submit_btn.clicked.connect(on_submit)

        answers_layout.addLayout(self.answers)
        answers_layout.addSpacing(8)
        answers_layout.addWidget(self.submit_btn)

        self.right.addWidget(self.question_box)
        self.right.addWidget(self.answers_box, 1)

        root.addLayout(self.left, 1)
        root.addWidget(self.divider)
        root.addLayout(self.right, 3)
        self.refresh_theme()

    def refresh_theme(self):
        palette = colors()
        self.setStyleSheet(f"QWidget#quizView {{ background: {palette['window']}; }}")
        self.divider.setStyleSheet(f"color: {palette['panel_border']};")
        self.question_box.setStyleSheet(panel_style())
        self.answers_box.setStyleSheet(panel_style())
        self.question_label.setStyleSheet(transparent_label_style())
        self.progress.update()
