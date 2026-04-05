# 🧠 Testownik – Quiz Learning App

A simple yet powerful desktop quiz application built with **Python + PySide6**, designed for efficient learning through repetition, feedback, and progress tracking.

---

## ✨ Features

- 📂 Load questions from a folder of `.txt` files
- 🔁 Repetition-based learning (configurable per session)
- 🎯 Tracks mastery of each question
- 🟢 Visual feedback:
  - Green = correct
  - Orange = partially correct
  - Red = wrong
- 📊 Smooth progress bar showing answer quality
- ⏱ Built-in session timer
- 💾 Resume previous session automatically
- 🧠 Smart repetition:
  - Wrong/partial answers are reinserted into the queue

---

## 🚀 Getting Started

### 1. Requirements

- Python **3.10+**
- Recommended: use a virtual environment

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

From the parent directory of `Testownik`:

```bash
python -m Testownik
```

---

## 📝 Question Format

Each question is stored in a `.txt` file.

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

- `?` → question (only one per file)
- `*` → correct answer
- `-` → incorrect answer

### Requirements

Each file must contain:
- exactly **one question (`?`)**
- at least **one correct answer (`*`)**
- at least **one answer overall**

---

## ⚠️ Invalid Files

Files will be **skipped automatically** if they:
- have invalid format
- contain empty answers
- contain multiple `?` lines
- contain unsupported line formats

A warning will be displayed listing all skipped files.

---

## 🧠 How Learning Works

- You choose how many repetitions each question requires
- A question is considered **mastered** only after all required correct repetitions are completed
- Wrong or partial answers **do not increase required repetitions**, but add extra practice attempts

---

## 🤝 Contributing

Contributions are very welcome!

If you have ideas for improvements, new features, or bug fixes:

- ⭐ Open an issue to discuss ideas
- 🔧 Submit a pull request
- 💡 Suggest UX/UI improvements

This project is meant to evolve — feel free to experiment and improve it.

---


## 📜 License

MIT 

---

## 👨‍💻 Author

Built as a learning-focused project. Feel free to fork, modify, and extend 🚀