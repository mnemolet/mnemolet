import logging
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from mnemolet.config import DB_PATH
from mnemolet.cuore.storage.models import Base

logger = logging.getLogger(__name__)


class BaseDatabaseManager:
    """
    Base class for SQLAlchemy database managers with shared configuration.
    Handles engine creation, session management, and SQLite optimizations.
    """

    def __init__(self, db_path: Optional[Path] = None, echo: bool = False):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        db_url = f"sqlite:///{self.db_path}"

        self.engine = create_engine(
            db_url,
            echo=echo,
            connect_args={
                "check_same_thread": False,
                "timeout": 30,
            },
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

        self._configure_sqlite()
        self._create_tables()

    def _configure_sqlite(self) -> None:
        """Configure SQLite PRAGMAs for WAL mode and foreign keys."""

        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            logger.debug("SQLite PRAGMAs configured: WAL mode and foreign keys enabled")

    def _create_tables(self) -> None:
        """Create all tables defined in Base metadata."""
        Base.metadata.create_all(bind=self.engine)
        logger.info(
            f"[{self.__class__.__name__}] Tables created/verified at {self.db_path}"
        )

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
