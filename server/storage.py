from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Optional
import aiosqlite
from datetime import datetime


class Storage:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db: Optional[aiosqlite.Connection] = None

    async def init(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = await aiosqlite.connect(str(self.db_path))
        await self._ensure_table()

    async def _ensure_table(self) -> None:
        assert self.db
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                attachment TEXT
            )
            """
        )
        await self.db.commit()

    async def add_message(self, sender: str, text: str, timestamp: Optional[str] = None, attachment: Optional[str] = None) -> int:
        assert self.db
        ts = timestamp or datetime.utcnow().isoformat()
        cur = await self.db.execute(
            "INSERT INTO messages (sender, text, timestamp, attachment) VALUES (?, ?, ?, ?)",
            (sender, text, ts, attachment),
        )
        await self.db.commit()
        return cur.lastrowid

    async def get_messages(self, limit: Optional[int] = None) -> List[Dict]:
        assert self.db
        q = "SELECT id, sender, text, timestamp, attachment FROM messages ORDER BY id ASC"
        if limit is not None:
            q += " LIMIT ?"
            cur = await self.db.execute(q, (limit,))
        else:
            cur = await self.db.execute(q)
        rows = await cur.fetchall()
        return [dict(row) for row in rows]

    async def close(self) -> None:
        if self.db:
            await self.db.close()
