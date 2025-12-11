import logging
import sqlite3
from pathlib import Path

from mnemolet.config import DB_PATH

logger = logging.getLogger(__name__)


class BaseSQLite:
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or DB_PATH

    def _get_connection(self) -> sqlite3.Connection:
        """
        Returns a SQLite connection.
        """
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    @staticmethod
    def exec_schema(conn: sqlite3.Connection, schema: str) -> None:
        """
        Execute SQL schema in the given conn.
        """
        conn.executescript(schema)
        logger.info("[BaseSQLite]: schema executed successfully")
