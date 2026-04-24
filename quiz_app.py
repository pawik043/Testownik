import os
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

from .ui import FlashcardFilePickerDialog, MainMenu, QuizView
from .widgets import AnswerBox
from .services import (
    QuizInteractionService,
    QuizSessionService,
    delete_file,
    list_flashcard_csv_files,
    load_flashcard_deck,
    read_text_file,
    write_text_file,
)


CONFIG_NAME = "quiz_state.json"
RECENT_FILE = "recent_folder.txt"


class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testownik")

        self.session = QuizSessionService()
        self.interaction = QuizInteractionService()
        self.boxes = []
        self.invalid_question_files = []
        self.start_time = time.time()
        self.config_path = ""
        self.current_folder = ""
        self.flashcard_folder = ""
        self.selected_flashcard_files = []
        self.flashcard_cards = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.stack = QStackedWidget()

        self.main_menu = MainMenu(
            on_select_folder=self.load_folder,
            on_load_recent=self.load_recent_folder,
            on_flashcards=self.open_flashcards_mode,
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

    def open_flashcards_mode(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Flashcards Folder")
        if not folder:
            return

        flashcard_files = list_flashcard_csv_files(folder)
        if not flashcard_files:
            QMessageBox.warning(
                self,
                "No CSV files",
                "No CSV files were found in this folder.",
            )
            return

        dialog = FlashcardFilePickerDialog(flashcard_files, self)
        if dialog.exec() != dialog.Accepted:
            return

        selected_files = dialog.selected_files()
        if not selected_files:
            QMessageBox.information(
                self,
                "No files selected",
                "Select at least one CSV file to start a flashcards session.",
            )
            return

        self.flashcard_folder = folder
        deck = load_flashcard_deck(selected_files)

        if not deck["files"]:
            QMessageBox.warning(
                self,
                "No valid flashcards",
                "No selected CSV files contained usable sideA/sideB columns with card data.",
            )
            return

        self.selected_flashcard_files = deck["files"]
        self.flashcard_cards = deck["cards"]

        message_lines = [
            f"Loaded {len(self.flashcard_cards)} flashcards from {len(self.selected_flashcard_files)} file(s).",
            "",
            "Selected files:",
            *[
                f'{file_info["label"]} ({file_info["card_count"]} cards)'
                for file_info in self.selected_flashcard_files
            ],
        ]

        if deck["skipped_files"]:
            message_lines.extend(
                [
                    "",
                    "Skipped files without usable sideA/sideB data:",
                    *deck["skipped_files"],
                ]
            )

        QMessageBox.information(
            self,
            "Flashcards Selection Saved",
            "\n".join(message_lines),
        )

    def load_recent_folder(self):
        if not os.path.exists(RECENT_FILE):
            QMessageBox.information(self, "No recent folder", "No recent folder saved yet.")
            return

        folder = read_text_file(RECENT_FILE)
        if folder is None:
            QMessageBox.warning(self, "Error", "Could not read recent folder.")
            return

        if not folder or not os.path.isdir(folder):
            QMessageBox.warning(self, "Missing folder", "The recent folder no longer exists.")
            return

        self.load_folder(folder)

    def save_recent(self, folder: str):
        write_text_file(RECENT_FILE, folder)

    # ---------- Session / Folder ----------

    def load_folder(self, folder=None):
        if not folder:
            folder = QFileDialog.getExistingDirectory(self)
        if not folder:
            return

        self.current_folder = folder
        self.save_recent(folder)
        self.config_path = os.path.join(folder, CONFIG_NAME)

        self.invalid_question_files = self.session.load_questions_from_folder(folder)

        if self.invalid_question_files:
            QMessageBox.warning(
                self,
                "Invalid question files",
                "The following .txt files were skipped because they have invalid format:\n\n"
                + "\n".join(self.invalid_question_files),
            )

        if not self.session.has_questions():
            QMessageBox.warning(
                self,
                "No valid questions",
                "No valid question files were found in this folder.",
            )
            return

        if os.path.exists(self.config_path):
            answer = QMessageBox.question(
                self,
                "Resume",
                "Continue previous session?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if answer == QMessageBox.Yes:
                if not self.session.restore_from_path(self.config_path):
                    self.new_session()
            else:
                delete_file(self.config_path)
                self.new_session()
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
        self.interaction.reset()
        self.quiz_view.submit_btn.setText("Check")

        if self.session.has_pending_questions():
            self.next_q()

    def save(self):
        if not self.session.state or not self.config_path:
            return
        self.session.save_to_path(self.config_path)

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
        self.interaction.reset()
        self.quiz_view.submit_btn.setText("Check")

        current = self.session.next_question()
        if not current:
            self.finish_session()
            return

        self.render()
        self.save()

    def render(self):
        round_data = self.interaction.start_round(self.session.current)
        self.quiz_view.question_label.setText(round_data["question"])

        for i in reversed(range(self.quiz_view.answers.count())):
            item = self.quiz_view.answers.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        self.boxes = []
        cols = round_data["columns"]
        answer_count = len(round_data["answers"])

        for i, answer_text in enumerate(round_data["answers"]):
            box = AnswerBox(answer_text, i, self.on_select)
            box.setEnabled(True)

            row = i // cols
            col = i % cols

            if cols == 2 and answer_count % 2 == 1 and i == answer_count - 1:
                self.quiz_view.answers.addWidget(box, row, 0, 1, 2, alignment=Qt.AlignHCenter)
            else:
                self.quiz_view.answers.addWidget(box, row, col)

            self.boxes.append(box)

        self.quiz_view.progress.state = self.session.serialize_state()
        self.quiz_view.progress.update()

    def on_select(self, index, is_selected):
        self.interaction.update_selection(index, is_selected)

    def check_or_next(self):
        if self.interaction.waiting_next:
            self.next_q()
            return

        if not self.session.current:
            return

        result = self.interaction.submit(self.session)
        if not result:
            return

        for i, box in enumerate(self.boxes):
            box.setEnabled(False)
            feedback = result["feedback"].get(i, "neutral")

            if feedback == "correct":
                box.mark_correct()
            elif feedback == "missing":
                box.mark_missing()
            elif feedback == "wrong":
                box.mark_wrong()

        self.quiz_view.progress.state = self.session.serialize_state()
        self.quiz_view.progress.update()
        self.update_mastery_label()

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
