# Testownik

A desktop study app built with Python and PySide6.

It currently supports two learning modes:
- Quiz mode for multiple-choice practice from `.txt` files
- Flashcards mode for card-based review from `.csv` files

## Current Release: v1.1.0

Compared with `v1.0.1`, this build focuses on smoother flashcard study, better theme support, and a simpler release pipeline.

### What's New Since v1.0.1

- Added dynamic light/dark theme handling. The custom UI now follows system appearance changes while the app is running.
- Reworked bright mode to use clean white and pale gray surfaces, with distinct pale-tinted main menu mode buttons.
- Added flashcard keyboard navigation:
  - `Space` reveals a card, then marks it as known and advances on the next press.
  - `U` reveals a card, or marks `I Knew It` when the answer is visible.
  - `I` reveals a card, or marks `Needs Review` when the answer is visible.
  - `Backspace` marks the card as `Needs Review`.
- Added visual flashcard feedback before auto-advance:
  - known cards briefly pulse green
  - review cards briefly pulse red
- Added a review flashcard file flow so cards marked `Needs Review` can be stored and picked up again later.
- Temporarily disabled the macOS GitHub Actions build while keeping the workflow commented for future use.
- Windows GitHub Actions builds remain active.

## Features

- Two study modes from the main menu: `Quiz Mode` and `Flashcards Mode`
- `Continue Last Session` resumes the most recent session, whether it was quiz or flashcards
- Built-in timer, progress tracking, and session restart flow
- Completion dialog with `Return to Main Menu` and `Restart Session`

### Quiz Mode

- Loads questions from a folder of `.txt` files
- Repetition-based learning with configurable repetition count
- Tracks mastery per question
- Answer feedback:
  - green = correct
  - yellow = missed correct answer
  - red = wrong selected answer
- Wrong and partial answers are reinserted into the queue for extra practice
- Session progress is saved to `quiz_state.json` inside the selected question folder

### Flashcards Mode

- Loads flashcard sets from `.csv` files in a selected folder
- Lets the user choose which CSV files to include through a checkbox picker
- Includes `Select All` and `Deselect All` shortcuts in the file picker
- Displays a large flashcard with `sideA` first and `sideB` after reveal
- Reveal by clicking the card or pressing `Check`
- Classify cards with `I Knew It` or `Needs Review`
- Tracks flashcard progress during the session
- Session progress is saved to `flashcard_state.json` inside the selected flashcard folder

## Getting Started

### Requirements

- Python 3.10+

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the app

From the parent directory of `Testownik`:

```bash
python -m Testownik
```

## Quiz File Format

Each quiz question is stored in its own `.txt` file.

### Example

```text
?What are primary colors?
*Red
*Blue
*Yellow
-Green
-Purple
```

### Rules

- `?` means the question line
- `*` means a correct answer
- `-` means an incorrect answer

### Requirements

Each file must contain:
- exactly one question line
- at least one correct answer
- at least one answer overall

### Invalid Quiz Files

Files are skipped automatically if they:
- contain invalid line formats
- contain multiple question lines
- contain empty answers
- do not contain a valid question/correct-answer structure

## Flashcard CSV Format

Flashcards are created from `.csv` files using only columns named `sideA` and `sideB`.

Any column with a different header is ignored.

### Simple Example

```csv
sideA,sideB
dog,pies
cat,kot
```

### Multiple Columns Per Side

If a file contains repeated `sideA` or `sideB` columns, values from the same row are combined on one side of the card.

Example:

```csv
sideA,sideA,sideB
DataX,DataY,DataZ
```

This becomes:

- front side:

```text
DataX

DataY
```

- back side:

```text
DataZ
```

If repeated columns on the same side contain the same text in the same row, duplicates are removed instead of being shown twice.

### Flashcard CSV Notes

- Header matching for `sideA` and `sideB` is case-insensitive
- Empty values are ignored
- A row is skipped if it does not produce both a non-empty `sideA` and a non-empty `sideB`
- Files without usable `sideA`/`sideB` data are skipped
- File names shown in the picker are cleaned for display, for example:
  - `kanji_new.csv` becomes `Kanji New`

## Session Persistence

- The app stores the latest session type and folder in `recent_session.json`
- `Continue Last Session` restores the most recent quiz or flashcard session
- Quiz progress is restored from the selected quiz folder
- Flashcard progress is restored from the selected flashcard folder, including:
  - selected files
  - remaining queue
  - current card
  - known / needs-review status
  - whether the current card was already revealed

## UI Summary

- Main menu now matches the same dark card-based style used in study sessions
- Flashcard mode uses a large scalable card with dynamic font sizing and wrapping
- Flashcard controls are arranged as:
  - `Check`
  - `I Knew It` and `Needs Review`
  - `Next`

## License

MIT
