import sys
import argparse
from PySide6.QtWidgets import QApplication
from app.chat_window import ChatWindow


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--server", default=None, help="WebSocket server URI, e.g. ws://host:8765")
    args = p.parse_args()

    app = QApplication(sys.argv)
    w = ChatWindow(server_url=args.server)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
