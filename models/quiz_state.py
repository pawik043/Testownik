class QuizState:
    def __init__(self, questions: list, reps: int):
        self.status = {q["file"]: "unanswered" for q in questions}
        self.required_correct = {q["file"]: reps for q in questions}
        self.correct_streak = {q["file"]: 0 for q in questions}

    # ---------- Progress / Mastery ----------

    def register_correct(self, file: str):
        self.status[file] = "correct"
        needed = self.required_correct.get(file, 1)
        current = self.correct_streak.get(file, 0)

        if current < needed:
            self.correct_streak[file] = current + 1

    def register_partial(self, file: str):
        self.status[file] = "partial"

    def register_wrong(self, file: str):
        self.status[file] = "wrong"

    def is_mastered(self, file: str) -> bool:
        return self.correct_streak.get(file, 0) >= self.required_correct.get(file, 1)

    def mastered_count(self) -> int:
        return sum(
            1 for f in self.required_correct
            if self.is_mastered(f)
        )

    def total_questions(self) -> int:
        return len(self.required_correct)

    # ---------- Serialization ----------

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "required_correct": self.required_correct,
            "correct_streak": self.correct_streak,
        }

    @staticmethod
    def from_dict(data: dict, questions: list):
        obj = QuizState(questions, reps=1)

        obj.status = data.get("status", obj.status)
        obj.required_correct = data.get(
            "required_correct",
            {q["file"]: 1 for q in questions}
        )
        obj.correct_streak = data.get(
            "correct_streak",
            {q["file"]: 0 for q in questions}
        )

        return obj