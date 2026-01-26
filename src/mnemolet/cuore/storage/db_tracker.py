import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import (
        Boolean,
        Column,
        DateTime,
        Integer,
        String,
        select,
        event,
        create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from mnemolet.cuore.storage.base import BaseSQLite
from mnemolet.config import DB_PATH

logger = logging.getLogger(__name__)

Base = declarative_base()


class FileRecord(Base):
    """SQLAlchemy ORM model for files table"""

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String, unique=True, nullable=False)
    hash = Column(String, nullable=False)
    ingested_at = Column(DateTime(timezone=True), nullable=False)
    indexed = Column(Boolean, default=False, nullable=False)


CREATE_TABLE_FILES = """
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE,
    hash TEXT,
    ingested_at TEXT,
    indexed INTEGER DEFAULT 0
);
"""


class DBTracker(BaseSQLite):
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH

        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create database URL
        db_url = f"sqlite:///{self.db_path}"

        self.engine = create_engine(
            db_url,
            echo=False,
            connect_args={
                "check_same_thread": False,
                "timeout": 30  # add timeout for concurrent access
            }
        )

        # Configure session factory
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False  # for better performance
        )

         # Enable WAL mode and foreign keys
        self._configure_sqlite()

        # Create tables
        self._create_tables()

    def _configure_sqlite(self):
        """Configure SQLite with WAL mode and foreign keys."""
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set PRAGMAs on SQLite connection."""
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            logger.debug("SQLite PRAGMAs configured: WAL mode and foreign keys enabled")

    def _create_tables(self):
        """Create all tables defined in Base metadata."""
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"[DBTracker] Tables created/verified at {self.db_path}")

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def add_file(self, path: str, file_hash: str) -> None:
        """
        Insert a new file if it does not exist.

        Args:
            path: File path
            file_hash: File hash
        """
        with self.get_session() as session:
            try:
                # Check if file already exists by hash
                existing = session.execute(
                    select(FileRecord).where(FileRecord.hash == file_hash)
                ).scalar_one_or_none()

                if existing is None:
                    # Create new record
                    file_record = FileRecord(
                        path=path,
                        hash=file_hash,
                        ingested_at=datetime.now(UTC),
                        indexed=False
                    )
                    session.add(file_record)
                    session.commit()
                    logger.debug(f"Added file: {path}")
                else:
                    logger.debug(f"File already exists with hash {file_hash}: {existing.path}")

            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error adding file {path}: {e}")
                raise

    def file_exists(self, file_hash: str) -> bool:
        """
        Check if file with this hash is already in db.
        """
        with self._get_connection() as conn:
            curr = conn.execute("SELECT 1 FROM files WHERE hash = ?", (file_hash,))
            return curr.fetchone() is not None

    def mark_indexed(self, file_hash: str):
        """
        Mark file as indexed is Qdrant.
        """
        with self._get_connection() as conn:
            conn.execute("UPDATE files SET indexed = 1 WHERE hash = ?", (file_hash,))

    def list_files(self, indexed: Optional[bool] = None) -> list[dict]:
        """
        List all tracked files, can be optionally filtered by indexed status.
        """
        query = "SELECT path, hash, ingested_at, indexed FROM files"
        params = ()
        if indexed is not None:
            query += " WHERE indexed = ?"
            params = (1 if indexed else 0,)
        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
