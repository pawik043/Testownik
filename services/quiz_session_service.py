import random

from models import QuizState
from .question_loader import load_questions
from .session_manager import load_session, save_session


class QuizSessionService:
    def __init__(self):
        self.questions = []
        self.questions_by_file = {}
        self.queue = []
        self.current = None
        self.state = None

    def configure_questions(self, questions: list):
        self.questions = questions
        self.questions_by_file = {q["file"]: q for q in questions}
        self.queue = []
        self.current = None
        self.state = None

    def load_questions_from_folder(self, folder: str):
        questions, invalid_files = load_questions(folder)
        self.configure_questions(questions)
        return invalid_files

    def has_questions(self) -> bool:
        return bool(self.questions)

    def restore(self, session_data: dict):
        self.state = QuizState.from_dict(session_data, self.questions)
        self.queue = list(session_data.get("queue", []))
        self.current = None

    def restore_from_path(self, config_path: str) -> bool:
        session_data = load_session(config_path)
        if not session_data:
            return False

        self.restore(session_data)
        return True

    def start_new(self, reps: int):
        self.state = QuizState(self.questions, reps)
        self.queue = []
        self.current = None

        for question in self.questions:
            self.queue.extend([question["file"]] * reps)

        random.shuffle(self.queue)

    def reset(self, reps: int):
        self.start_new(reps)

    def has_pending_questions(self) -> bool:
        return bool(self.queue)

    def next_question(self):
        while self.queue:
            file_name = self.queue.pop(0)
            match = self.questions_by_file.get(file_name)
            if match is not None:
                self.current = match
                return match

        self.current = None
        return None

    def evaluate_answer(self, answer_mapping: dict, selected: set):
        if not self.current or not self.state:
            return None

        correct_set = {
            index for index, original_index in answer_mapping.items()
            if original_index in self.current["correct"]
        }
        file_name = self.current["file"]

        if selected == correct_set:
            self.state.register_correct(file_name)
            result = "correct"
        elif selected and selected.issubset(correct_set):
            self.state.register_partial(file_name)
            self._requeue_current_question()
            result = "partial"
        else:
            self.state.register_wrong(file_name)
            self._requeue_current_question()
            result = "wrong"

        return {
            "result": result,
            "correct_set": correct_set,
        }

    def _requeue_current_question(self):
        if not self.current:
            return

        file_name = self.current["file"]
        for _ in range(2):
            insert_at = random.randint(len(self.queue) // 2, len(self.queue))
            self.queue.insert(insert_at, file_name)

    def serialize_state(self) -> dict:
        if not self.state:
            return {}
        return self.state.to_dict()

    def serialize_session(self) -> dict:
        payload = self.serialize_state()
        payload["queue"] = list(self.queue)
        return payload

    def save_to_path(self, config_path: str):
        save_session(config_path, self.serialize_state(), self.queue)

    def mastered_count(self) -> int:
        if not self.state:
            return 0
        return self.state.mastered_count()

    def total_questions(self) -> int:
        if not self.state:
            return 0
        return self.state.total_questions()
