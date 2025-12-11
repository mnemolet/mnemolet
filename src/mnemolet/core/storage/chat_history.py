from pathlib import Path

from .base import BaseSQLite

SCHEMA = """
CREATE TABLE IF NOT EXISTS chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    message TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
);
"""


class ChatHistory(BaseSQLite):
    def __init__(self, db_path: Path = None):
        super().__init__(db_path)
        self._create_tables()

    def _create_tables(self):
        with self._get_connection() as conn:
            self.exec_schema(conn, SCHEMA)

    def create_session(self) -> str:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO chat_sessions (created_at) VALUES (datetime('now'))"
            )
            return cur.lastrowid

    def add_message(self, session_id: int, role: str, message: str):
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO chat_messages (session_id, role, message, created_at)
                VALUES (?, ?, ?, datetime('now'))
                """,
                (session_id, role, message),
            )

    def get_messages(self, session_id: int):
        with self._get_connection() as conn:
            cur = conn.execute(
                """SELECT role, message, created_at
                FROM chat_messages
                WHERE session_id = ? ORDER BY id""",
                (session_id,),
            )
            return cur.fetchall()

    def list_sessions(self):
        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT id, created_at FROM chat_sessions ORDER BY id DESC"
            )
            return cur.fetchall()

    def session_exists(self, session_id: int) -> bool:
        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT 1 FROM chat_sessions WHERE id = ?", (session_id,)
            )
            return cur.fetchone() is not None

    def delete_session(self, session_id: int):
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM chat_messages WHERE session_id = ?", (session_id,)
            )
            conn.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
            conn.commit()
