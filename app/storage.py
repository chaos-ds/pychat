from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime


class Storage:
    """シンプルな SQLite ベースのメッセージストレージ。

    API:
      - add_message(sender, text, timestamp=None) -> int
      - get_messages(limit=None) -> List[Dict]
      - close()
    """

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._ensure_table()

    def _ensure_table(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add_message(self, sender: str, text: str, timestamp: Optional[str] = None) -> int:
        ts = timestamp or datetime.utcnow().isoformat()
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO messages (sender, text, timestamp) VALUES (?, ?, ?)",
            (sender, text, ts),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_messages(self, limit: Optional[int] = None) -> List[Dict]:
        cur = self.conn.cursor()
        q = "SELECT id, sender, text, timestamp FROM messages ORDER BY id ASC"
        if limit is not None:
            q += " LIMIT ?"
            cur.execute(q, (limit,))
        else:
            cur.execute(q)
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass
