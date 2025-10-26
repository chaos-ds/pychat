from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy, QSpacerItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from pathlib import Path


class MessageBubble(QWidget):
    """メッセージをバブル表示するウィジェット。

    - sender: 表示用に吹き出しの色を変える
    - text: テキスト（省略可）
    - attachment: 画像パス（省略可）
    - align_right: 送信者側なら右寄せにする
    """

    def __init__(self, sender: str, text: str = "", attachment: str | None = None, align_right: bool = False, parent=None):
        super().__init__(parent)
        self.sender = sender
        self.text = text
        self.attachment = attachment
        self.align_right = align_right

        self._init_ui()

    def _init_ui(self):
        main = QHBoxLayout(self)
        if self.align_right:
            main.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        bubble = QWidget()
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(10, 6, 10, 6)

        # テキストラベル
        if self.text:
            label = QLabel(self.text)
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            bubble_layout.addWidget(label)

        # 画像添付があれば表示
        if self.attachment:
            p = Path(self.attachment)
            if p.exists():
                pix = QPixmap(str(p))
                if not pix.isNull():
                    img_label = QLabel()
                    # 適度にリサイズ（最大幅 240 px）
                    max_w = 240
                    w = pix.width()
                    h = pix.height()
                    if w > max_w:
                        pix = pix.scaledToWidth(max_w, Qt.SmoothTransformation)
                    img_label.setPixmap(pix)
                    img_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                    bubble_layout.addWidget(img_label)

        # スタイル
        bubble.setObjectName("bubble")
        if self.align_right:
            bubble.setStyleSheet("#bubble { background: #87CEFA; border-radius:10px; }")
        else:
            bubble.setStyleSheet("#bubble { background: #E8E8E8; border-radius:10px; }")

        main.addWidget(bubble)
        if not self.align_right:
            main.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.setLayout(main)
