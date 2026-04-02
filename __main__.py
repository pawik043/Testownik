import os
import sys
import random
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QRadioButton, QButtonGroup, QHBoxLayout, QProgressBar
)

CONFIG_NAME = "session.json"

class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quiz Trainer")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.load_btn = QPushButton("Select Question Folder")
        self.load_btn.clicked.connect(self.load_folder)
        self.layout.addWidget(self.load_btn)

        self.question_label = QLabel("Load a folder to start")
        self.layout.addWidget(self.question_label)

        self.answers_layout = QVBoxLayout()
        self.layout.addLayout(self.answers_layout)

        self.button_group = QButtonGroup()

        self.submit_btn = QPushButton("Submit Answer")
        self.submit_btn.clicked.connect(self.check_answer)
        self.layout.addWidget(self.submit_btn)

        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

        self.questions = []
        self.queue = []
        self.current = None
        self.config_path = None
        self.state = {}

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not folder:
            return

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

        file = self.queue.pop(0)
        self.current = next(q for q in self.questions if q["file"] == file)

        self.display_question()
        self.save_state()

    def display_question(self):
        self.question_label.setText(self.current["question"])

        # clear old
        for i in reversed(range(self.answers_layout.count())):
            self.answers_layout.itemAt(i).widget().setParent(None)

        self.button_group = QButtonGroup()

        for i, ans in enumerate(self.current["answers"]):
            btn = QRadioButton(ans)
            self.button_group.addButton(btn, i)
            self.answers_layout.addWidget(btn)

        self.update_progress()

    def check_answer(self):
        selected = self.button_group.checkedId()
        if selected == -1:
            return

        correct = selected in self.current["correct"]

        file = self.current["file"]

        if correct:
            self.state["status"][file] = "correct"
        else:
            self.state["status"][file] = "wrong"
            # repeat twice
            self.queue += [file, file]
            random.shuffle(self.queue)

        self.save_state()
        self.next_question()

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
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
