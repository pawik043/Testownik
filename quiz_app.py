import os
import random
import time

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QFileDialog,
    QMessageBox,
    QInputDialog,
)

from .ui import MainMenu, QuizView
from .widgets import AnswerBox
from .services import load_questions, load_session, save_session
from .models import QuizState


CONFIG_NAME = "quiz_state.json"
RECENT_FILE = "recent_folder.txt"


class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testownik")

        self.questions = []
        self.queue = []
        self.current = None
        self.answer_mapping = {}
        self.selected = set()
        self.boxes = []
        self.invalid_question_files = []
        self.waiting_next = False
        self.start_time = time.time()
        self.config_path = ""
        self.current_folder = ""
        self.state = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.stack = QStackedWidget()

        self.main_menu = MainMenu(
            on_select_folder=self.load_folder,
            on_load_recent=self.load_recent_folder,
        )

        self.quiz_view = QuizView(
            on_return=self.return_to_menu,
            on_reset=self.reset_session,
            on_submit=self.check_or_next,
        )

        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.quiz_view)

        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)

    # ---------- Navigation ----------

    def return_to_menu(self):
        self.timer.stop()
        self.stack.setCurrentWidget(self.main_menu)

    def load_recent_folder(self):
        if not os.path.exists(RECENT_FILE):
            QMessageBox.information(self, "No recent folder", "No recent folder saved yet.")
            return

        try:
            with open(RECENT_FILE, "r", encoding="utf-8") as f:
                folder = f.read().strip()
        except Exception:
            QMessageBox.warning(self, "Error", "Could not read recent folder.")
            return

        if not folder or not os.path.isdir(folder):
            QMessageBox.warning(self, "Missing folder", "The recent folder no longer exists.")
            return

        self.load_folder(folder)

    def save_recent(self, folder: str):
        try:
            with open(RECENT_FILE, "w", encoding="utf-8") as f:
                f.write(folder)
        except Exception:
            pass

    # ---------- Session / Folder ----------

    def load_folder(self, folder=None):
        if not folder:
            folder = QFileDialog.getExistingDirectory(self)
        if not folder:
            return

        self.current_folder = folder
        self.save_recent(folder)
        self.config_path = os.path.join(folder, CONFIG_NAME)

        self.questions, self.invalid_question_files = load_questions(folder)

        if self.invalid_question_files:
            QMessageBox.warning(
                self,
                "Invalid question files",
                "The following .txt files were skipped because they have invalid format:\n\n"
                + "\n".join(self.invalid_question_files),
            )

        if not self.questions:
            QMessageBox.warning(
                self,
                "No valid questions",
                "No valid question files were found in this folder.",
            )
            return

        session_data = None
        if os.path.exists(self.config_path):
            answer = QMessageBox.question(
                self,
                "Resume",
                "Continue previous session?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if answer == QMessageBox.Yes:
                session_data = load_session(self.config_path)
            else:
                try:
                    os.remove(self.config_path)
                except Exception:
                    pass

        if session_data:
            self.state = QuizState.from_dict(session_data, self.questions)
            self.queue = session_data.get("queue", [])
        else:
            self.new_session()

        self.quiz_view.progress.state = self.state.to_dict()
        self.quiz_view.progress.update()
        self.update_mastery_label()

        self.stack.setCurrentWidget(self.quiz_view)
        self.start_time = time.time()
        self.update_timer()
        self.timer.start(1000)

        if self.queue:
            self.next_q()
        else:
            self.finish_session()

    def new_session(self):
        reps, ok = QInputDialog.getInt(self, "Reps", "Repetitions", 1, 1, 5)
        if not ok:
            reps = 1

        self.state = QuizState(self.questions, reps)
        self.queue = []

        for q in self.questions:
            self.queue += [q["file"]] * reps

        random.shuffle(self.queue)

        self.start_time = time.time()
        self.update_timer()
        self.update_mastery_label()

        self.quiz_view.progress.state = self.state.to_dict()
        self.quiz_view.progress.update()

    def reset_session(self):
        self.new_session()
        self.waiting_next = False
        self.quiz_view.submit_btn.setText("Check")
        self.selected.clear()

        if self.queue:
            self.next_q()

    def save(self):
        if not self.state or not self.config_path:
            return
        save_session(self.config_path, self.state.to_dict(), self.queue)

    # ---------- Timer / Labels ----------

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.quiz_view.timer_label.setText(f"{minutes} min {seconds:02d} sec")

    def update_mastery_label(self):
        if not self.state:
            self.quiz_view.mastery_label.setText("0 / 0")
            return

        mastered = self.state.mastered_count()
        total = self.state.total_questions()
        self.quiz_view.mastery_label.setText(f"{mastered} / {total}")

    # ---------- Question flow ----------

    def next_q(self):
        self.selected.clear()
        self.waiting_next = False
        self.quiz_view.submit_btn.setText("Check")

        if not self.queue:
            self.finish_session()
            return

        file_name = self.queue.pop(0)

        match = next((q for q in self.questions if q["file"] == file_name), None)
        if match is None:
            self.next_q()
            return

        self.current = match
        self.render()
        self.save()

    def render(self):
        self.quiz_view.question_label.setText(self.current["question"])

        for i in reversed(range(self.quiz_view.answers.count())):
            item = self.quiz_view.answers.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        self.boxes = []
        paired = list(enumerate(self.current["answers"]))
        random.shuffle(paired)
        self.answer_mapping = {i: orig_i for i, (orig_i, _) in enumerate(paired)}

        cols = 2 if len(paired) > 2 else 1

        for i, (_, answer_text) in enumerate(paired):
            box = AnswerBox(answer_text, i, self.on_select)
            box.setEnabled(True)

            row = i // cols
            col = i % cols

            if cols == 2 and len(paired) % 2 == 1 and i == len(paired) - 1:
                self.quiz_view.answers.addWidget(box, row, 0, 1, 2, alignment=Qt.AlignHCenter)
            else:
                self.quiz_view.answers.addWidget(box, row, col)

            self.boxes.append(box)

        self.quiz_view.progress.state = self.state.to_dict()
        self.quiz_view.progress.update()

    def on_select(self, index, is_selected):
        if is_selected:
            self.selected.add(index)
        else:
            self.selected.discard(index)

    def check_or_next(self):
        if self.waiting_next:
            self.next_q()
            return

        if not self.current:
            return

        correct_set = {
            i for i, orig_i in self.answer_mapping.items()
            if orig_i in self.current["correct"]
        }

        for i, box in enumerate(self.boxes):
            box.setEnabled(False)

            if i in correct_set and i in self.selected:
                box.mark_correct()
            elif i in correct_set and i not in self.selected:
                box.mark_missing()
            elif i not in correct_set and i in self.selected:
                box.mark_wrong()

        file_name = self.current["file"]

        if self.selected == correct_set:
            self.state.register_correct(file_name)
        elif self.selected and self.selected.issubset(correct_set):
            self.state.register_partial(file_name)
            for _ in range(2):
                self.queue.insert(random.randint(len(self.queue) // 2, len(self.queue)), file_name)
        else:
            self.state.register_wrong(file_name)
            for _ in range(2):
                self.queue.insert(random.randint(len(self.queue) // 2, len(self.queue)), file_name)

        self.quiz_view.progress.state = self.state.to_dict()
        self.quiz_view.progress.update()
        self.update_mastery_label()

        self.waiting_next = True
        self.quiz_view.submit_btn.setText("Next")
        self.save()

    def finish_session(self):
        self.timer.stop()
        self.save()

        mastered = self.state.mastered_count() if self.state else 0
        total = self.state.total_questions() if self.state else 0

        QMessageBox.information(
            self,
            "Session complete",
            f"Done!\n\nMastered: {mastered} / {total}",
        )