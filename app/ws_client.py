from __future__ import annotations

import threading
import json
from typing import Optional

from PySide6.QtCore import QObject, Signal

import websocket


class WSClient(QObject):
    """Simple WebSocket client using `websocket-client` running in background thread.

    Signals:
      - message_received(dict)
      - connected()
      - disconnected()
    """

    message_received = Signal(dict)
    connected = Signal()
    disconnected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ws: Optional[websocket.WebSocketApp] = None
        self._thread: Optional[threading.Thread] = None

    def start(self, uri: str):
        if self.ws is not None:
            return

        def _on_message(ws, message):
            try:
                data = json.loads(message)
            except Exception:
                data = {"text": message}
            self.message_received.emit(data)

        def _on_open(ws):
            self.connected.emit()

        def _on_close(ws, close_status_code, close_msg):
            self.disconnected.emit()

        self.ws = websocket.WebSocketApp(uri, on_message=_on_message, on_open=_on_open, on_close=_on_close)
        self._thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self._thread.start()

    def send(self, data: dict):
        if self.ws and self.ws.sock and self.ws.sock.connected:
            try:
                self.ws.send(json.dumps(data, ensure_ascii=False))
            except Exception:
                pass

    def stop(self):
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None
