import os
import sys
import random
import json
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QHBoxLayout, QProgressBar, QFrame, QStackedLayout
)
from PySide6.QtCore import QTimer, Qt

CONFIG_NAME = "session.json"

class AnswerBox(QFrame):
    def __init__(self, text, index, callback):
        super().__init__()
        self.index = index
        self.callback = callback
        self.selected = False

        self.setFrameShape(QFrame.Box)
        self.setLineWidth(1)
        self.setStyleSheet(self.default_style())

        layout = QVBoxLayout()
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #222; font-size: 14px;")
        layout.addWidget(self.label)
        self.setLayout(layout)

    def default_style(self):
        return """
        QFrame {
            background-color: #f5f5f5;
            border-radius: 10px;
            border: 1px solid #ccc;
            padding: 12px;
        }
        """

    def selected_style(self):
        return """
        QFrame {
            background-color: #cce5ff;
            border-radius: 10px;
            border: 2px solid #3399ff;
            padding: 12px;
        }
        """

    def mousePressEvent(self, event):
        self.selected = not self.selected
        self.setStyleSheet(self.selected_style() if self.selected else self.default_style())
        self.callback(self.index, self.selected)

    def mark_correct(self):
        self.setStyleSheet("background-color: #c8f7c5; border-radius: 10px; padding: 12px;")

    def mark_wrong(self):
        self.setStyleSheet("background-color: #f7c5c5; border-radius: 10px; padding: 12px;")

    def mark_missing(self):
        self.setStyleSheet("background-color: #fff3b0; border-radius: 10px; padding: 12px;")


class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testo!")

        self.stack = QStackedLayout()
        self.setLayout(self.stack)

        self.init_main_menu()
        self.init_quiz_ui()

        self.stack.setCurrentWidget(self.main_menu)

    def init_main_menu(self):
        self.main_menu = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Testo!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        btn = QPushButton("Select Question Folder")
        btn.clicked.connect(self.load_folder)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(btn)
        layout.addStretch()

        self.main_menu.setLayout(layout)
        self.stack.addWidget(self.main_menu)

    def init_quiz_ui(self):
        self.quiz_widget = QWidget()
        main_layout = QHBoxLayout()
        self.quiz_widget.setLayout(main_layout)

        # LEFT PANEL
        self.left_panel = QVBoxLayout()
        self.timer_label = QLabel("Time: 0s")
        self.counter_label = QLabel("Question 0/0")
        self.progress = QProgressBar()

        self.left_panel.addWidget(self.timer_label)
        self.left_panel.addWidget(self.counter_label)
        self.left_panel.addWidget(self.progress)

        main_layout.addLayout(self.left_panel, 1)

        # RIGHT PANEL
        self.right_panel = QVBoxLayout()
        main_layout.addLayout(self.right_panel, 3)

        self.question_label = QLabel("")
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("font-size: 16px;")

        self.answers_layout = QVBoxLayout()

        self.submit_btn = QPushButton("Check Answer")
        self.submit_btn.clicked.connect(self.check_answer)

        self.right_panel.addWidget(self.question_label)
        self.right_panel.addLayout(self.answers_layout)
        self.right_panel.addWidget(self.submit_btn)

        self.stack.addWidget(self.quiz_widget)

        # state
        self.questions = []
        self.queue = []
        self.current = None
        self.config_path = None
        self.state = {}
        self.selected_answers = set()
        self.answer_boxes = []
        self.current_index = 0

        # timer
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

    def start_timer(self):
        self.start_time = time.time()
        self.timer.start(1000)

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.timer_label.setText(f"Time: {elapsed}s")

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not folder:
            return

        self.stack.setCurrentWidget(self.quiz_widget)
        self.start_timer()

        self.config_path = os.path.join(folder, CONFIG_NAME)
        self.questions = self.load_questions(folder)

        self.state = {
            "status": {q["file"]: "new" for q in self.questions},
            "queue": [q["file"] for q in self.questions]
        }
        self.queue = self.state["queue"]
        self.current_index = 0

        self.save_state()
        self.next_question()

    def load_questions(self, folder):
        questions = []
        for file in os.listdir(folder):
            if file.endswith(".txt"):
                path = os.path.join(folder, file)
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                q = ""
                answers = []
                correct = []

                for line in lines:
                    line = line.strip()
                    if line.startswith("?"):
                        q = line[1:].strip()
                    elif line.startswith("*"):
                        answers.append(line[1:].strip())
                        correct.append(len(answers)-1)
                    elif line.startswith("-"):
                        answers.append(line[1:].strip())

                questions.append({
                    "file": file,
                    "question": q,
                    "answers": answers,
                    "correct": correct
                })
        return questions

    def next_question(self):
        if not self.queue:
            self.finish_quiz()
            return

        self.selected_answers.clear()

        file = self.queue.pop(0)
        self.current = next(q for q in self.questions if q["file"] == file)
        self.current_index += 1

        self.display_question()
        self.save_state()

    def display_question(self):
        total = len(self.questions)
        self.counter_label.setText(f"Question {self.current_index}/{total}")
        self.question_label.setText(self.current["question"])

        for i in reversed(range(self.answers_layout.count())):
            self.answers_layout.itemAt(i).widget().setParent(None)

        self.answer_boxes = []

        for i, ans in enumerate(self.current["answers"]):
            box = AnswerBox(ans, i, self.on_select)
            self.answers_layout.addWidget(box)
            self.answer_boxes.append(box)

        self.update_progress()

    def on_select(self, index, selected):
        if selected:
            self.selected_answers.add(index)
        else:
            self.selected_answers.discard(index)

    def check_answer(self):
        correct_set = set(self.current["correct"])

        for i, box in enumerate(self.answer_boxes):
            if i in correct_set and i in self.selected_answers:
                box.mark_correct()
            elif i in correct_set and i not in self.selected_answers:
                box.mark_missing()
            elif i not in correct_set and i in self.selected_answers:
                box.mark_wrong()

        is_correct = self.selected_answers == correct_set
        file = self.current["file"]

        if is_correct:
            self.state["status"][file] = "correct"
        else:
            self.state["status"][file] = "wrong"
            self.queue += [file, file]
            random.shuffle(self.queue)

        self.save_state()
        QTimer.singleShot(1500, self.next_question)

    def update_progress(self):
        total = len(self.state["status"])
        correct = sum(1 for s in self.state["status"].values() if s == "correct")

        self.progress.setMaximum(total)
        self.progress.setValue(correct)

    def finish_quiz(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

        self.timer.stop()
        self.stack.setCurrentWidget(self.main_menu)

    def save_state(self):
        self.state["queue"] = self.queue
        with open(self.config_path, "w") as f:
            json.dump(self.state, f, indent=2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuizApp()
    window.resize(800, 500)
    window.show()
    sys.exit(app.exec())