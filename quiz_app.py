import os
import random
import time

from PySide6.QtCore import QTimer, Qt
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
from .services import QuizSessionService, load_questions, load_session, save_session


CONFIG_NAME = "quiz_state.json"
RECENT_FILE = "recent_folder.txt"


class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testownik")

        self.session = QuizSessionService()
        self.answer_mapping = {}
        self.selected = set()
        self.boxes = []
        self.invalid_question_files = []
        self.waiting_next = False
        self.start_time = time.time()
        self.config_path = ""
        self.current_folder = ""

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

        questions, self.invalid_question_files = load_questions(folder)
        self.session.configure_questions(questions)

        if self.invalid_question_files:
            QMessageBox.warning(
                self,
                "Invalid question files",
                "The following .txt files were skipped because they have invalid format:\n\n"
                + "\n".join(self.invalid_question_files),
            )

        if not self.session.questions:
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
            self.session.restore(session_data)
        else:
            self.new_session()

        self.quiz_view.progress.state = self.session.serialize_state()
        self.quiz_view.progress.update()
        self.update_mastery_label()

        self.stack.setCurrentWidget(self.quiz_view)
        self.start_time = time.time()
        self.update_timer()
        self.timer.start(1000)

        if self.session.has_pending_questions():
            self.next_q()
        else:
            self.finish_session()

    def new_session(self):
        reps, ok = QInputDialog.getInt(self, "Reps", "Repetitions", 1, 1, 5)
        if not ok:
            reps = 1

        self.session.start_new(reps)

        self.start_time = time.time()
        self.update_timer()
        self.update_mastery_label()

        self.quiz_view.progress.state = self.session.serialize_state()
        self.quiz_view.progress.update()

    def reset_session(self):
        self.new_session()
        self.waiting_next = False
        self.quiz_view.submit_btn.setText("Check")
        self.selected.clear()

        if self.session.has_pending_questions():
            self.next_q()

    def save(self):
        if not self.session.state or not self.config_path:
            return
        save_session(
            self.config_path,
            self.session.serialize_state(),
            self.session.queue,
        )

    # ---------- Timer / Labels ----------

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.quiz_view.timer_label.setText(f"{minutes} min {seconds:02d} sec")

    def update_mastery_label(self):
        mastered = self.session.mastered_count()
        total = self.session.total_questions()
        self.quiz_view.mastery_label.setText(f"{mastered} / {total}")

    # ---------- Question flow ----------

    def next_q(self):
        self.selected.clear()
        self.waiting_next = False
        self.quiz_view.submit_btn.setText("Check")

        current = self.session.next_question()
        if not current:
            self.finish_session()
            return

        self.render()
        self.save()

    def render(self):
        self.quiz_view.question_label.setText(self.session.current["question"])

        for i in reversed(range(self.quiz_view.answers.count())):
            item = self.quiz_view.answers.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        self.boxes = []
        paired = list(enumerate(self.session.current["answers"]))
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

        self.quiz_view.progress.state = self.session.serialize_state()
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

        if not self.session.current:
            return

        result = self.session.evaluate_answer(self.answer_mapping, self.selected)
        if not result:
            return

        correct_set = result["correct_set"]

        for i, box in enumerate(self.boxes):
            box.setEnabled(False)

            if i in correct_set and i in self.selected:
                box.mark_correct()
            elif i in correct_set and i not in self.selected:
                box.mark_missing()
            elif i not in correct_set and i in self.selected:
                box.mark_wrong()

        self.quiz_view.progress.state = self.session.serialize_state()
        self.quiz_view.progress.update()
        self.update_mastery_label()

        self.waiting_next = True
        self.quiz_view.submit_btn.setText("Next")
        self.save()

    def finish_session(self):
        self.timer.stop()
        self.save()

        mastered = self.session.mastered_count()
        total = self.session.total_questions()

        QMessageBox.information(
            self,
            "Session complete",
            f"Done!\n\nMastered: {mastered} / {total}",
        )
