from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
)
from PySide6.QtCore import QDateTime
from pathlib import Path

from .storage import Storage


class ChatWindow(QWidget):
    """シンプルなチャット画面ウィジェット。

    - メッセージ表示: QListWidget
    - 入力欄: QLineEdit
    - 送信ボタン: QPushButton

    送信後は自分のメッセージをリストに追加し、簡単なエコー応答を表示します（デモ目的）。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PyChat - チャット")
        self.resize(600, 420)

        # ストレージ初期化（リポジトリのルートに DB を作成）
        db_path = Path(__file__).resolve().parents[1] / "chat_history.db"
        self.storage = Storage(db_path)

        main_layout = QVBoxLayout(self)

        # メッセージ表示エリア
        self.chat_view = QListWidget()
        self.chat_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.chat_view)

        # 入力エリア
        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("メッセージを入力...")
        self.send_btn = QPushButton("送信")
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.send_btn)
        main_layout.addLayout(input_layout)

        # シグナル
        self.send_btn.clicked.connect(self.send_message)
        self.input.returnPressed.connect(self.send_message)

        # 起動時に履歴をロード
        try:
            for msg in self.storage.get_messages():
                # DB の timestamp は ISO 文字列なので、簡易的にそのまま表示
                who = msg.get("sender", "?")
                text = msg.get("text", "")
                ts = msg.get("timestamp")
                # _append_message は現在時刻を表示するため、履歴用に直接 QListWidgetItem を追加
                item_text = f"[{ts}] {who}: {text}"
                from PySide6.QtWidgets import QListWidgetItem

                self.chat_view.addItem(QListWidgetItem(item_text))
            self.chat_view.scrollToBottom()
        except Exception:
            # 履歴ロードに失敗しても起動は続行
            pass

    def send_message(self):
        text = self.input.text().strip()
        if not text:
            return
        # 送信メッセージを永続化
        try:
            self.storage.add_message("あなた", text)
        except Exception:
            pass

        self._append_message("あなた", text)
        self.input.clear()

        # デモのために簡単なエコー応答を追加
        reply = f"受信しました: {text}"
        try:
            self.storage.add_message("相手", reply)
        except Exception:
            pass
        self._append_reply(reply)

    def _append_message(self, who: str, text: str):
        ts = QDateTime.currentDateTime().toString("HH:mm:ss")
        item_text = f"[{ts}] {who}: {text}"
        item = QListWidgetItem(item_text)
        self.chat_view.addItem(item)
        self.chat_view.scrollToBottom()

    def closeEvent(self, event):
        # アプリ終了時に DB を閉じる
        try:
            self.storage.close()
        except Exception:
            pass
        super().closeEvent(event)

    def _append_reply(self, text: str):
        self._append_message("相手", text)
