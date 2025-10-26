from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QFileDialog,
)
from PySide6.QtCore import QDateTime
from pathlib import Path
import shutil

from .storage import Storage
from .ui_enhancements import MessageBubble


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
        # 添付ボタン
        self.attach_btn = QPushButton("添付")
        self.send_btn = QPushButton("送信")
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.attach_btn)
        input_layout.addWidget(self.send_btn)
        main_layout.addLayout(input_layout)

        # シグナル
        self.send_btn.clicked.connect(self.send_message)
        self.input.returnPressed.connect(self.send_message)
        self.attach_btn.clicked.connect(self.attach_file)

        # 起動時に履歴をロード
        try:
            for msg in self.storage.get_messages():
                who = msg.get("sender", "?")
                text = msg.get("text", "")
                ts = msg.get("timestamp")
                attachment = msg.get("attachment")
                is_sender = who == "あなた"
                # MessageBubble を使って履歴表示
                widget = MessageBubble(who, text=text, attachment=attachment, align_right=is_sender)
                item = QListWidgetItem()
                item.setSizeHint(widget.sizeHint())
                self.chat_view.addItem(item)
                self.chat_view.setItemWidget(item, widget)
            self.chat_view.scrollToBottom()
        except Exception:
            # 履歴ロード失敗は無視
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

        # UI にバブルとして追加
        widget = MessageBubble("あなた", text=text, align_right=True)
        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        self.chat_view.addItem(item)
        self.chat_view.setItemWidget(item, widget)
        self.input.clear()

        # 自動エコーは不要のためここでは何もしない

    def _append_message(self, who: str, text: str):
        ts = QDateTime.currentDateTime().toString("HH:mm:ss")
        item_text = f"[{ts}] {who}: {text}"
        item = QListWidgetItem(item_text)
        self.chat_view.addItem(item)
        self.chat_view.scrollToBottom()

    def attach_file(self):
        # ファイルダイアログで画像を選び、attachments フォルダにコピーしてメッセージとして送信
        filename, _ = QFileDialog.getOpenFileName(self, "ファイルを選択", str(Path.home()), "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if not filename:
            return
        try:
            attachments_dir = Path(__file__).resolve().parents[1] / "attachments"
            attachments_dir.mkdir(parents=True, exist_ok=True)
            dest = attachments_dir / (f"{int(QDateTime.currentSecsSinceEpoch())}_" + Path(filename).name)
            shutil.copy(filename, str(dest))
            # 永続化（テキストは空でも良い）
            self.storage.add_message("あなた", "", attachment=str(dest))

            # UI に追加
            widget = MessageBubble("あなた", text="", attachment=str(dest), align_right=True)
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.chat_view.addItem(item)
            self.chat_view.setItemWidget(item, widget)
            self.chat_view.scrollToBottom()
        except Exception:
            pass

    def closeEvent(self, event):
        # アプリ終了時に DB を閉じる
        try:
            self.storage.close()
        except Exception:
            pass
        super().closeEvent(event)

