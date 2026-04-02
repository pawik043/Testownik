import os
import sys
import random
import json
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QHBoxLayout, QProgressBar, QFrame
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
        self.setLineWidth(2)
        self.setStyleSheet("background-color: lightgray; padding: 10px;")

        layout = QVBoxLayout()
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        self.selected = not self.selected
        self.update_style()
        self.callback(self.index, self.selected)

    def update_style(self):
        if self.selected:
            self.setStyleSheet("background-color: #87CEFA; padding: 10px;")
        else:
            self.setStyleSheet("background-color: lightgray; padding: 10px;")

    def mark_correct(self):
        self.setStyleSheet("background-color: lightgreen; padding: 10px;")

    def mark_wrong(self):
        self.setStyleSheet("background-color: lightcoral; padding: 10px;")

    def mark_missing(self):
        self.setStyleSheet("background-color: khaki; padding: 10px;")


class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quiz Trainer")

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # LEFT PANEL (timer)
        self.left_panel = QVBoxLayout()
        self.timer_label = QLabel("Time: 0s")
        self.left_panel.addWidget(self.timer_label)
        self.progress = QProgressBar()
        self.left_panel.addWidget(self.progress)

        main_layout.addLayout(self.left_panel, 1)

        # RIGHT PANEL (quiz)
        self.right_panel = QVBoxLayout()
        main_layout.addLayout(self.right_panel, 3)

        self.load_btn = QPushButton("Select Question Folder")
        self.load_btn.clicked.connect(self.load_folder)
        self.right_panel.addWidget(self.load_btn)

        self.question_label = QLabel("Load a folder to start")
        self.question_label.setWordWrap(True)
        self.right_panel.addWidget(self.question_label)

        self.answers_layout = QVBoxLayout()
        self.right_panel.addLayout(self.answers_layout)

        self.submit_btn = QPushButton("Check Answer")
        self.submit_btn.clicked.connect(self.check_answer)
        self.right_panel.addWidget(self.submit_btn)

        self.questions = []
        self.queue = []
        self.current = None
        self.config_path = None
        self.state = {}

        self.selected_answers = set()
        self.answer_boxes = []

        # TIMER
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

        self.start_timer()

        self.config_path = os.path.join(folder, CONFIG_NAME)
        self.questions = self.load_questions(folder)

        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                self.state = json.load(f)
            self.queue = self.state["queue"]
        else:
            self.state = {
                "status": {q["file"]: "new" for q in self.questions},
                "queue": [q["file"] for q in self.questions]
            }
            self.queue = self.state["queue"]
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
            self.question_label.setText("Done!")
            return

        self.selected_answers.clear()

        file = self.queue.pop(0)
        self.current = next(q for q in self.questions if q["file"] == file)

        self.display_question()
        self.save_state()

    def display_question(self):
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

    def save_state(self):
        self.state["queue"] = self.queue
        with open(self.config_path, "w") as f:
            json.dump(self.state, f, indent=2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuizApp()
    window.resize(1920, 1080)
    window.show()
    sys.exit(app.exec())