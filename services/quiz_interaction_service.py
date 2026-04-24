import random


class QuizInteractionService:
    def __init__(self):
        self.answer_mapping = {}
        self.selected = set()
        self.waiting_next = False
        self.answer_texts = []

    def reset(self):
        self.answer_mapping = {}
        self.selected.clear()
        self.waiting_next = False
        self.answer_texts = []

    def start_round(self, question: dict):
        self.selected.clear()
        self.waiting_next = False

        paired = list(enumerate(question["answers"]))
        random.shuffle(paired)

        self.answer_mapping = {
            display_index: original_index
            for display_index, (original_index, _) in enumerate(paired)
        }
        self.answer_texts = [answer_text for _, answer_text in paired]

        return {
            "question": question["question"],
            "answers": list(self.answer_texts),
            "columns": 2 if len(self.answer_texts) > 2 else 1,
        }

    def update_selection(self, index: int, is_selected: bool):
        if is_selected:
            self.selected.add(index)
        else:
            self.selected.discard(index)

    def submit(self, session) -> dict | None:
        if not session.current:
            return None

        result = session.evaluate_answer(self.answer_mapping, self.selected)
        if not result:
            return None

        correct_set = result["correct_set"]
        feedback = {}

        for index in range(len(self.answer_texts)):
            if index in correct_set and index in self.selected:
                feedback[index] = "correct"
            elif index in correct_set and index not in self.selected:
                feedback[index] = "missing"
            elif index not in correct_set and index in self.selected:
                feedback[index] = "wrong"
            else:
                feedback[index] = "neutral"

        self.waiting_next = True

        return {
            "feedback": feedback,
            "result": result["result"],
        }
