import sqlite3
from typing import List, Dict, Any, Optional

class ContextStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        # collections table (optional, but we can keep simple)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                timestamp REAL NOT NULL,
                source_id TEXT
            )
        """)
        self.conn.commit()

    def add_chunk(self, text: str, timestamp: float, source_id: Optional[str] = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO chunks (text, timestamp, source_id) VALUES (?, ?, ?)",
            (text, timestamp, source_id)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_chunks(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        query = "SELECT id, text, timestamp, source_id FROM chunks ORDER BY id"
        if limit is not None:
            query += f" LIMIT {limit} OFFSET {offset}"
        cur = self.conn.execute(query)
        rows = cur.fetchall()
        return [dict(row) for row in rows]

    def get_chunk_by_id(self, chunk_id: int) -> Optional[Dict[str, Any]]:
        cur = self.conn.execute(
            "SELECT id, text, timestamp, source_id FROM chunks WHERE id = ?", (chunk_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def update_chunk(self, chunk_id: int, text: Optional[str] = None, 
                     timestamp: Optional[float] = None, source_id: Optional[str] = None):
        fields = []
        values = []
        if text is not None:
            fields.append("text = ?")
            values.append(text)
        if timestamp is not None:
            fields.append("timestamp = ?")
            values.append(timestamp)
        if source_id is not None:
            fields.append("source_id = ?")
            values.append(source_id)
        if not fields:
            return
        values.append(chunk_id)
        query = f"UPDATE chunks SET {', '.join(fields)} WHERE id = ?"
        self.conn.execute(query, values)
        self.conn.commit()

    def delete_chunk(self, chunk_id: int):
        self.conn.execute("DELETE FROM chunks WHERE id = ?", (chunk_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    # For testing compatibility
    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
