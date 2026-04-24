import os
import re


def format_flashcard_name(filename: str) -> str:
    base_name, _ = os.path.splitext(filename)
    cleaned = re.sub(r"[_-]+", " ", base_name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned.title() if cleaned else filename


def list_flashcard_csv_files(folder: str) -> list[dict]:
    files = []

    for filename in sorted(os.listdir(folder)):
        if not filename.lower().endswith(".csv"):
            continue

        files.append(
            {
                "file": filename,
                "label": format_flashcard_name(filename),
                "path": os.path.join(folder, filename),
            }
        )

    return files
