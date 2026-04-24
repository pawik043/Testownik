import csv
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


def parse_flashcard_csv_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.reader(csv_file)
        rows = list(reader)

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
