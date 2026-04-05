import sys
from PySide6.QtWidgets import QApplication
from .quiz_app import QuizApp


def main():
    app = QApplication(sys.argv)
    window = QuizApp()
    window.resize(1100, 700)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()