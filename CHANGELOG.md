# Changelog

All notable changes to Testownik are documented here.

## v1.1.0 - 2026-05-09

### Added

- Added dynamic light/dark theme support for the custom PySide UI.
- Added live theme refresh when the system appearance changes while the app is running.
- Added bright-mode styling with clean white and pale gray surfaces.
- Added distinct pale-tinted main menu buttons in bright mode.
- Added flashcard keyboard navigation:
  - `Space` reveals a card, then marks it as known and advances on the next press.
  - `U` reveals a card, or marks `I Knew It` when the answer is visible.
  - `I` reveals a card, or marks `Needs Review` when the answer is visible.
  - `Backspace` marks the card as `Needs Review`.
- Added visual flashcard feedback before auto-advance:
  - green pulse for `I Knew It`
  - red pulse for `Needs Review`
- Added a review flashcard file flow for cards marked `Needs Review`.

### Changed

- Improved flashcard keyboard behavior so `U` and `I` can reveal the card before classification.
- Updated flashcard buttons to show shortcut hints: `I Knew It [U]` and `Needs Review [I]`.
- Temporarily commented out the macOS GitHub Actions build while keeping the workflow available for future use.
- Kept Windows GitHub Actions builds active for releases.
- Updated the README with the current v1.1.0 release notes.

### Fixed

- Fixed theme import/package placement for the shared theme helper.
- Fixed stylesheet f-string brace handling in themed widgets.
- Fixed custom widgets not updating fully after system theme changes.
- Fixed unreliable flashcard shortcuts by handling keys at the main app level.
- Fixed review feedback colors so the `Needs Review` pulse stays red instead of mixing multiple colors.

## v1.0.1 - 2026-05-02

### Changed

- Updated the Windows build flow in GitHub Actions.

### Fixed

- Fixed relative path issues.
- Cleaned up project files after the v1.0.0 release.

## v1.0.0 - 2026-05-01

### Added

- Added the initial GitHub Actions build workflow.
- Added the main quiz application with PySide6 UI.
- Added quiz mode for `.txt` question files.
- Added answer selection, checking, color feedback, counters, progress tracking, and timer support.
- Added session restart and recent-session support.
- Added service-layer structure for question loading, quiz sessions, and interactions.
- Added flashcards mode for `.csv` files with `sideA` and `sideB` parsing.
- Added flashcard file selection with bulk select/deselect controls.
- Added flashcard session persistence.
- Added a main menu with quiz, flashcards, and continue-session navigation.
- Added completion dialogs and restart/return flows.
- Added README documentation, requirements, and packaging metadata.

### Changed

- Refined the main menu and study-session visual design.
- Improved answer box layout and button geometry.
- Improved dynamic font scaling for flashcards.
- Improved flashcard CSV parsing, including repeated side columns and duplicate-value cleanup.
- Split the original app into dedicated `ui`, `widgets`, `services`, and `models` modules.

### Fixed

- Fixed handling for malformed quiz question files.
- Fixed answer locking after pressing `Check`.
- Fixed progress bar behavior.
- Fixed window size jumping after checking answers.
- Fixed Polish character handling.
- Fixed study material selection errors.
