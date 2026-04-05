import os


def load_questions(folder: str):
    """
    Load valid quiz questions from .txt files in the given folder.

    Returns:
        tuple[list[dict], list[str]]:
            - valid questions
            - invalid/skipped file descriptions
    """
    questions = []
    invalid_files = []

    for filename in os.listdir(folder):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(folder, filename)

        try:
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            invalid_files.append(f"{filename} (could not be read)")
            continue

        question_text = ""
        answers = []
        correct_indexes = []
        invalid = False

        for line in lines:
            line = line.strip()

            if not line:
                continue

            if line.startswith("?"):
                if question_text:
                    invalid = True
                    break
                question_text = line[1:].strip()

            elif line.startswith("*"):
                answer = line[1:].strip()
                if not answer:
                    invalid = True
                    break
                answers.append(answer)
                correct_indexes.append(len(answers) - 1)

            elif line.startswith("-"):
                answer = line[1:].strip()
                if not answer:
                    invalid = True
                    break
                answers.append(answer)

            else:
                invalid = True
                break

        if invalid or not question_text or not answers or not correct_indexes:
            invalid_files.append(filename)
            continue

        questions.append(
            {
                "file": filename,
                "question": question_text,
                "answers": answers,
                "correct": correct_indexes,
            }
        )

    return questions, invalid_files