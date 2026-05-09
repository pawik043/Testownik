import os
import random
import time
import sys
from pathlib import Path

from PySide6.QtCore import QEvent, QTimer, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QDialog,
    QFileDialog,
    QMessageBox,
    QInputDialog,
)

from ui import FlashcardFilePickerDialog, FlashcardView, MainMenu, QuizView
from widgets import AnswerBox
from services import (
    QuizInteractionService,
    QuizSessionService,
    REVIEW_FLASHCARD_FILE_NAME,
    delete_file,
    get_review_flashcard_file,
    list_flashcard_csv_files,
    load_flashcard_deck,
    load_session,
    save_json_file,
    save_review_flashcard_file,
)


CONFIG_NAME = "quiz_state.json"
FLASHCARD_CONFIG_NAME = "flashcard_state.json"

# Use user data directory for persistent files
USER_DATA_DIR = Path.home() / ".testownik"
USER_DATA_DIR.mkdir(exist_ok=True)
RECENT_SESSION_FILE = USER_DATA_DIR / "recent_session.json"


class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testownik")

        self.session = QuizSessionService()
        self.interaction = QuizInteractionService()
        self.boxes = []
        self.invalid_question_files = []
        self.start_time = time.time()
        self.active_mode = None
        self.config_path = ""
        self.flashcard_config_path = ""
        self.current_folder = ""
        self.flashcard_folder = ""
        self.selected_flashcard_files = []
        self.flashcard_cards = []
        self.flashcard_queue = []
        self.flashcard_current = None
        self.flashcard_status = {}
        self.flashcard_showing_back = False
        self.flashcard_waiting_next = False
        self.flashcard_feedback_active = False
        self.quiz_reps = 1

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

        self.flashcard_view = FlashcardView(
            on_return=self.return_to_menu,
            on_reset=self.reset_flashcard_session,
            on_flip=self.flip_flashcard,
            on_known=self.mark_flashcard_known,
            on_review=self.mark_flashcard_review,
            on_next=self.next_flashcard,
        )

        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.quiz_view)
        self.stack.addWidget(self.flashcard_view)

        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)

    def refresh_theme(self, *args):
        self.main_menu.refresh_theme()
        self.quiz_view.refresh_theme()
        self.flashcard_view.refresh_theme()
        for box in self.boxes:
            box.refresh_theme()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (
            QEvent.ApplicationPaletteChange,
            QEvent.PaletteChange,
            QEvent.StyleChange,
        ):
            self.refresh_theme()

    def keyPressEvent(self, event):
        if self.active_mode == "flashcards":
            key = event.key()
            if key == Qt.Key_Space:
                self.handle_flashcard_space()
                event.accept()
                return
            if key == Qt.Key_Backspace:
                self.handle_flashcard_backspace()
                event.accept()
                return
            if key == Qt.Key_U:
                self.handle_flashcard_known_shortcut()
                event.accept()
                return
            if key == Qt.Key_I:
                self.handle_flashcard_review_shortcut()
                event.accept()
                return

        super().keyPressEvent(event)

    # ---------- Navigation ----------

    def return_to_menu(self):
        self.timer.stop()
        if self.active_mode == "flashcards":
            self.save_flashcard_session()
        elif self.active_mode == "quiz":
            self.save()
        self.active_mode = None
        self.stack.setCurrentWidget(self.main_menu)

    def open_flashcards_mode(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Flashcards Folder")
        if not folder:
            return

        self.load_flashcard_folder(folder)

    def load_recent_folder(self):
        recent_session = load_session(str(RECENT_SESSION_FILE))
        if not recent_session:
            QMessageBox.information(self, "No recent session", "No recent session saved yet.")
            return

        mode = recent_session.get("mode")
        folder = recent_session.get("folder", "").strip()

        if not folder or not os.path.isdir(folder):
            QMessageBox.warning(self, "Missing folder", "The recent session folder no longer exists.")
            return

        if mode == "flashcards":
            self.load_flashcard_folder(folder, auto_resume=True)
            return

        self.load_folder(folder, auto_resume=True)

    def save_recent_session(self, mode: str, folder: str):
        save_json_file(
            str(RECENT_SESSION_FILE),
            {
                "mode": mode,
                "folder": folder,
            },
        )

    def load_flashcard_folder(self, folder: str, auto_resume: bool = False):
        self.flashcard_folder = folder
        self.flashcard_config_path = os.path.join(folder, FLASHCARD_CONFIG_NAME)
        self.save_recent_session("flashcards", folder)

        if auto_resume and os.path.exists(self.flashcard_config_path):
            if self.restore_flashcard_session():
                return

        flashcard_files = list_flashcard_csv_files(folder)
        review_file = get_review_flashcard_file(folder)
        if not flashcard_files and review_file is None:
            QMessageBox.warning(
                self,
                "No CSV files",
                "No CSV files were found in this folder.",
            )
            return

        dialog = FlashcardFilePickerDialog(flashcard_files, review_file, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        selected_files = dialog.selected_files()
        if not selected_files:
            QMessageBox.information(
                self,
                "No files selected",
                "Select at least one CSV file to start a flashcards session.",
            )
            return

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

        if deck["skipped_files"]:
            QMessageBox.information(
                self,
                "Some files were skipped",
                "Skipped files without usable sideA/sideB data:\n\n"
                + "\n".join(deck["skipped_files"]),
            )

        self.start_flashcard_session()

    # ---------- Session / Folder ----------

    def load_folder(self, folder=None, auto_resume: bool = False):
        if not folder:
            folder = QFileDialog.getExistingDirectory(self)
        if not folder:
            return

        self.current_folder = folder
        self.save_recent_session("quiz", folder)
        self.config_path = os.path.join(folder, CONFIG_NAME)
        self.active_mode = "quiz"

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

        if auto_resume and os.path.exists(self.config_path):
            if not self.session.restore_from_path(self.config_path):
                self.new_session()
        elif os.path.exists(self.config_path):
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

    def new_session(self, reps=None):
        if reps is None:
            reps, ok = QInputDialog.getInt(self, "Reps", "Repetitions", self.quiz_reps, 1, 5)
            if not ok:
                reps = self.quiz_reps

        self.quiz_reps = reps
        self.session.start_new(reps)

        self.start_time = time.time()
        self.update_timer()
        self.update_mastery_label()

        self.quiz_view.progress.state = self.session.serialize_state()
        self.quiz_view.progress.update()

    def reset_session(self):
        self.new_session(self.quiz_reps)
        self.interaction.reset()
        self.quiz_view.submit_btn.setText("Check")

        if self.session.has_pending_questions():
            self.next_q()

    def save(self):
        if not self.session.state or not self.config_path:
            return
        self.session.save_to_path(self.config_path)
        if self.current_folder:
            self.save_recent_session("quiz", self.current_folder)

    def start_flashcard_session(self):
        if not self.flashcard_cards:
            return

        self.active_mode = "flashcards"
        self.flashcard_status = {
            str(index): "unanswered"
            for index in range(len(self.flashcard_cards))
        }
        self.flashcard_queue = list(enumerate(self.flashcard_cards))
        random.shuffle(self.flashcard_queue)
        self.flashcard_current = None
        self.flashcard_showing_back = False
        self.flashcard_waiting_next = False
        self.flashcard_feedback_active = False
        self.flashcard_config_path = os.path.join(self.flashcard_folder, FLASHCARD_CONFIG_NAME)

        self.flashcard_view.progress.state = {"status": self.flashcard_status}
        self.flashcard_view.progress.update()
        self.update_flashcard_mastery_label()

        self.stack.setCurrentWidget(self.flashcard_view)
        self.start_time = time.time()
        self.update_timer()
        self.timer.start(1000)
        self.next_flashcard()

    def reset_flashcard_session(self):
        self.start_flashcard_session()

    def save_flashcard_session(self):
        if not self.flashcard_folder or not self.flashcard_config_path:
            return

        current_index = None
        if self.flashcard_current is not None:
            current_index = self.flashcard_current["index"]

        review_cards = [
            card
            for index, card in enumerate(self.flashcard_cards)
            if self.flashcard_status.get(str(index)) == "wrong"
        ]
        save_review_flashcard_file(self.flashcard_folder, review_cards)

        payload = {
            "selected_files": [file_info["file"] for file_info in self.selected_flashcard_files],
            "queue": [index for index, _ in self.flashcard_queue],
            "current_index": current_index,
            "status": self.flashcard_status,
            "showing_back": self.flashcard_showing_back,
            "waiting_next": self.flashcard_waiting_next,
            "cards": self.flashcard_cards,
        }
        save_json_file(self.flashcard_config_path, payload)
        self.save_recent_session("flashcards", self.flashcard_folder)

    def restore_flashcard_session(self) -> bool:
        saved = load_session(self.flashcard_config_path)
        if not saved:
            return False

        flashcard_files = list_flashcard_csv_files(self.flashcard_folder)
        file_lookup = {file_info["file"]: file_info for file_info in flashcard_files}
        selected_files = []
        saved_selected_files = saved.get("selected_files", [])
        review_file = get_review_flashcard_file(self.flashcard_folder)

        for file_name in saved_selected_files:
            if file_name in file_lookup:
                selected_files.append(file_lookup[file_name])
            elif file_name == REVIEW_FLASHCARD_FILE_NAME and review_file is not None:
                selected_files.append(review_file)
            else:
                selected_files.append(
                    {
                        "file": file_name,
                        "label": file_name,
                        "path": os.path.join(self.flashcard_folder, file_name),
                    }
                )

        deck = None
        if selected_files:
            deck = load_flashcard_deck(selected_files)
            if not deck["files"] or not deck["cards"]:
                deck = None

        if deck is None:
            saved_cards = saved.get("cards")
            if not saved_cards:
                return False

            self.selected_flashcard_files = selected_files
            self.flashcard_cards = saved_cards
        else:
            self.selected_flashcard_files = deck["files"]
            self.flashcard_cards = deck["cards"]
        self.active_mode = "flashcards"
        self.flashcard_config_path = os.path.join(self.flashcard_folder, FLASHCARD_CONFIG_NAME)

        card_lookup = {
            index: card
            for index, card in enumerate(self.flashcard_cards)
        }
        self.flashcard_status = {
            str(index): "unanswered"
            for index in range(len(self.flashcard_cards))
        }
        self.flashcard_status.update(saved.get("status", {}))

        self.flashcard_queue = [
            (index, card_lookup[index])
            for index in saved.get("queue", [])
            if index in card_lookup
        ]

        current_index = saved.get("current_index")
        self.flashcard_current = None
        if current_index in card_lookup:
            self.flashcard_current = {
                "index": current_index,
                "card": card_lookup[current_index],
            }

        self.flashcard_showing_back = bool(saved.get("showing_back", False))
        self.flashcard_waiting_next = bool(saved.get("waiting_next", False))
        self.flashcard_feedback_active = False

        self.flashcard_view.progress.state = {"status": self.flashcard_status}
        self.flashcard_view.progress.update()
        self.update_flashcard_mastery_label()

        self.stack.setCurrentWidget(self.flashcard_view)
        self.start_time = time.time()
        self.update_timer()
        self.timer.start(1000)

        if self.flashcard_current is None:
            if self.flashcard_queue:
                self.next_flashcard()
            else:
                self.finish_flashcard_session()
            return True

        self.render_current_flashcard()
        return True

    def show_completion_dialog(self):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Session Complete")
        dialog.setText("Congratulations! You made it!\n\nWhat do you want to do now?")

        return_btn = dialog.addButton("Return to Main Menu", QMessageBox.ButtonRole.AcceptRole)
        restart_btn = dialog.addButton("Restart Session", QMessageBox.ButtonRole.ActionRole)

        dialog.exec()
        clicked = dialog.clickedButton()

        if clicked == restart_btn:
            return "restart"
        if clicked == return_btn:
            return "menu"
        return "menu"

    # ---------- Timer / Labels ----------

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        if self.active_mode == "flashcards":
            self.flashcard_view.timer_label.setText(f"{minutes} min {seconds:02d} sec")
        else:
            self.quiz_view.timer_label.setText(f"{minutes} min {seconds:02d} sec")

    def update_mastery_label(self):
        mastered = self.session.mastered_count()
        total = self.session.total_questions()
        self.quiz_view.mastery_label.setText(f"{mastered} / {total}")

    def update_flashcard_mastery_label(self):
        known = sum(1 for status in self.flashcard_status.values() if status == "correct")
        total = len(self.flashcard_status)
        self.flashcard_view.mastery_label.setText(f"{known} / {total}")

    def next_flashcard(self):
        if self.active_mode != "flashcards":
            return

        if not self.flashcard_queue:
            self.finish_flashcard_session()
            return

        card_index, card = self.flashcard_queue.pop(0)
        self.flashcard_current = {
            "index": card_index,
            "card": card,
        }
        self.flashcard_showing_back = False
        self.flashcard_waiting_next = False
        self.flashcard_feedback_active = False

        self.render_current_flashcard()
        self.save_flashcard_session()

    def render_current_flashcard(self):
        if not self.flashcard_current:
            return

        current_position = len(self.flashcard_status) - len(self.flashcard_queue)
        self.flashcard_view.question_label.setText(
            f"Flashcard {current_position} / {len(self.flashcard_status)}"
        )
        card = self.flashcard_current["card"]
        if self.flashcard_waiting_next:
            subtitle = "Press Next to continue"
        elif self.flashcard_showing_back:
            subtitle = "Choose how well you knew this card"
        else:
            subtitle = f'{card["source_label"]}  •  Tap the card to reveal the answer'

        self.flashcard_view.subtitle_label.setText(subtitle)
        self.flashcard_view.card.setEnabled(True)
        if self.flashcard_showing_back:
            self.flashcard_view.card.set_text(card["side_b"]["text"], revealed=True)
        else:
            self.flashcard_view.card.set_text(card["side_a"]["text"], revealed=False)

        can_classify = (
            self.flashcard_showing_back
            and not self.flashcard_waiting_next
            and not self.flashcard_feedback_active
        )
        can_reveal = (
            not self.flashcard_showing_back
            and not self.flashcard_waiting_next
            and not self.flashcard_feedback_active
        )
        self.flashcard_view.card.setEnabled(
            not self.flashcard_waiting_next and not self.flashcard_feedback_active
        )
        self.flashcard_view.reveal_btn.setEnabled(can_reveal)
        self.flashcard_view.known_btn.setEnabled(can_classify)
        self.flashcard_view.review_btn.setEnabled(can_classify)
        self.flashcard_view.next_btn.setEnabled(
            self.flashcard_waiting_next and not self.flashcard_feedback_active
        )

    def flip_flashcard(self):
        if self.active_mode != "flashcards" or not self.flashcard_current:
            return

        if self.flashcard_showing_back or self.flashcard_waiting_next:
            return

        self.flashcard_showing_back = True
        self.render_current_flashcard()
        self.save_flashcard_session()

    def mark_flashcard_known(self):
        self.classify_flashcard("correct", advance=True)

    def mark_flashcard_review(self):
        self.classify_flashcard("wrong", advance=True)

    def handle_flashcard_space(self):
        if self.active_mode != "flashcards" or not self.flashcard_current:
            return

        if self.flashcard_feedback_active:
            return

        if self.flashcard_waiting_next:
            self.next_flashcard()
        elif self.flashcard_showing_back:
            self.classify_flashcard("correct", advance=True)
        else:
            self.flip_flashcard()

    def handle_flashcard_backspace(self):
        if self.active_mode != "flashcards" or not self.flashcard_current:
            return

        if self.flashcard_feedback_active:
            return

        if self.flashcard_waiting_next:
            self.next_flashcard()
        else:
            if not self.flashcard_showing_back:
                self.flashcard_showing_back = True
            self.classify_flashcard("wrong", advance=True)

    def handle_flashcard_known_shortcut(self):
        if self.active_mode != "flashcards" or not self.flashcard_current:
            return

        if self.flashcard_feedback_active:
            return

        if self.flashcard_waiting_next:
            self.next_flashcard()
        elif self.flashcard_showing_back:
            self.classify_flashcard("correct", advance=True)
        else:
            self.flip_flashcard()

    def handle_flashcard_review_shortcut(self):
        if self.active_mode != "flashcards" or not self.flashcard_current:
            return

        if self.flashcard_feedback_active:
            return

        if self.flashcard_waiting_next:
            self.next_flashcard()
        elif self.flashcard_showing_back:
            self.classify_flashcard("wrong", advance=True)
        else:
            self.flip_flashcard()

    def classify_flashcard(self, status: str, advance: bool = False):
        if self.active_mode != "flashcards" or not self.flashcard_current:
            return

        if (
            not self.flashcard_showing_back
            or self.flashcard_waiting_next
            or self.flashcard_feedback_active
        ):
            return

        card_index = str(self.flashcard_current["index"])
        self.flashcard_status[card_index] = status
        self.flashcard_waiting_next = True
        self.flashcard_feedback_active = advance

        self.flashcard_view.progress.state = {"status": self.flashcard_status}
        self.flashcard_view.progress.update()
        self.update_flashcard_mastery_label()
        self.render_current_flashcard()
        self.save_flashcard_session()

        if advance:
            self.flashcard_view.card.play_feedback(status, self.finish_flashcard_feedback)

    def finish_flashcard_feedback(self):
        self.flashcard_feedback_active = False
        self.next_flashcard()

    def finish_flashcard_session(self):
        self.timer.stop()

        known = sum(1 for status in self.flashcard_status.values() if status == "correct")
        review = sum(1 for status in self.flashcard_status.values() if status == "wrong")
        self.flashcard_view.subtitle_label.setText(
            f"Known: {known}  •  Needs Review: {review}"
        )

        action = self.show_completion_dialog()
        if action == "restart":
            self.reset_flashcard_session()
        else:
            self.return_to_menu()

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
        self.quiz_view.question_label.setText(f"Mastered: {mastered} / {total}")

        action = self.show_completion_dialog()
        if action == "restart":
            self.reset_session()
        else:
            self.return_to_menu()
