import sys
from PySide6.QtWidgets import QApplication
from app.chat_window import ChatWindow


def main():
    app = QApplication(sys.argv)
    w = ChatWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
