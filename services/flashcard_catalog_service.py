import csv
import os
import re


REVIEW_FLASHCARD_FILE_NAME = "review.csv"


# Common encodings for Polish text files
POLISH_ENCODINGS = ["utf-8-sig", "utf-8", "windows-1250", "iso-8859-2", "cp1250"]


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

        if filename.lower() == REVIEW_FLASHCARD_FILE_NAME.lower():
            continue

        files.append(
            {
                "file": filename,
                "label": format_flashcard_name(filename),
                "path": os.path.join(folder, filename),
            }
        )

    return files


def save_review_flashcard_file(folder: str, cards: list[dict]) -> bool:
    path = os.path.join(folder, REVIEW_FLASHCARD_FILE_NAME)

    if not cards:
        if not os.path.exists(path):
            return True
        try:
            os.remove(path)
            return True
        except Exception:
            return False

    try:
        with open(path, "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["sideA", "sideB"])
            for card in cards:
                writer.writerow([card["side_a"]["text"], card["side_b"]["text"]])
        return True
    except Exception:
        return False


def get_review_flashcard_file(folder: str) -> dict | None:
    path = os.path.join(folder, REVIEW_FLASHCARD_FILE_NAME)
    if not os.path.exists(path) or not os.path.isfile(path):
        return None

    return {
        "file": REVIEW_FLASHCARD_FILE_NAME,
        "label": "Review Pool",
        "path": path,
    }


def normalize_flashcard_header(header: str) -> str:
    return header.replace("\ufeff", "").strip().lower()


def build_flashcard_side(values: list[str]) -> dict:
    cleaned_values = []

    for value in values:
        if not value or not value.strip():
            continue

        normalized = value.strip()
        if normalized in cleaned_values:
            continue

        cleaned_values.append(normalized)

    return {
        "segments": cleaned_values,
        "text": "\n\n".join(cleaned_values),
    }


def _read_csv_with_encoding(path: str):
    """Try multiple encodings to read a CSV file, supporting Polish characters."""
    for encoding in POLISH_ENCODINGS:
        try:
            with open(path, "r", encoding=encoding, newline="") as csv_file:
                return list(csv.reader(csv_file))
        except (UnicodeDecodeError, LookupError):
            continue
        except Exception:
            return None
    return None


def parse_flashcard_csv_file(path: str) -> dict:
    rows = _read_csv_with_encoding(path)
    if rows is None:
        return {
            "cards": [],
            "side_a_indexes": [],
            "side_b_indexes": [],
        }

    if not rows:
        return {
            "cards": [],
            "side_a_indexes": [],
            "side_b_indexes": [],
        }

    headers = [normalize_flashcard_header(header) for header in rows[0]]
    side_a_indexes = [index for index, header in enumerate(headers) if header == "sidea"]
    side_b_indexes = [index for index, header in enumerate(headers) if header == "sideb"]

    cards = []

    for row_number, row in enumerate(rows[1:], start=2):
        padded_row = list(row) + [""] * (len(headers) - len(row))
        side_a = build_flashcard_side([padded_row[index] for index in side_a_indexes])
        side_b = build_flashcard_side([padded_row[index] for index in side_b_indexes])

        if not side_a["segments"] or not side_b["segments"]:
            continue

        cards.append(
            {
                "side_a": side_a,
                "side_b": side_b,
                "source_row": row_number,
            }
        )

    return {
        "cards": cards,
        "side_a_indexes": side_a_indexes,
        "side_b_indexes": side_b_indexes,
    }


def load_flashcard_deck(selected_files: list[dict]) -> dict:
    parsed_files = []
    all_cards = []
    skipped_files = []

    for file_info in selected_files:
        parsed = parse_flashcard_csv_file(file_info["path"])
        card_count = len(parsed["cards"])

        if not parsed["side_a_indexes"] or not parsed["side_b_indexes"] or card_count == 0:
            skipped_files.append(file_info["label"])
            continue

        parsed_file = dict(file_info)
        parsed_file["cards"] = parsed["cards"]
        parsed_file["card_count"] = card_count
        parsed_file["side_a_columns"] = len(parsed["side_a_indexes"])
        parsed_file["side_b_columns"] = len(parsed["side_b_indexes"])
        parsed_files.append(parsed_file)

        for card in parsed["cards"]:
            card_copy = dict(card)
            card_copy["source_file"] = file_info["file"]
            card_copy["source_label"] = file_info["label"]
            all_cards.append(card_copy)

    return {
        "files": parsed_files,
        "cards": all_cards,
        "skipped_files": skipped_files,
    }
