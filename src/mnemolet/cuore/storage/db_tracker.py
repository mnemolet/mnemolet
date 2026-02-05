import logging
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import (
    select,
)
from sqlalchemy.exc import SQLAlchemyError

from mnemolet.cuore.storage.base_db import BaseDatabaseManager
from mnemolet.cuore.storage.models import FileRecord

logger = logging.getLogger(__name__)


class DBTracker(BaseDatabaseManager):
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
                        indexed=False,
                    )
                    session.add(file_record)
                    session.commit()
                    logger.debug(f"Added file: {path}")
                else:
                    logger.debug(
                        f"File already exists with hash {file_hash}: {existing.path}"
                    )

            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error adding file {path}: {e}")
                raise

    def file_exists(self, file_hash: str) -> bool:
        """
        Check if file with this hash is already in db.

        Args:
            file_hash: File hash to check

        Returns:
            True if file exists, False otherwise
        """
        with self.get_session() as session:
            try:
                result = session.execute(
                    select(FileRecord).where(FileRecord.hash == file_hash)
                ).scalar_one_or_none()
                return result is not None
            except SQLAlchemyError as e:
                logger.error(f"Error checking file existence {file_hash}: {e}")
                return False

    def mark_indexed(self, file_hash: str) -> None:
        """
        Mark file as indexed in Qdrant.

        Args:
            file_hash: Hash of file to mark as indexed
        """
        with self.get_session() as session:
            try:
                result = session.execute(
                    select(FileRecord).where(FileRecord.hash == file_hash)
                ).scalar_one_or_none()

                if result:
                    result.indexed = True
                    session.commit()
                    logger.debug(f"Marked file as indexed: {file_hash}")
                else:
                    logger.warning(f"File not found for marking indexed: {file_hash}")

            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error marking file as indexed {file_hash}: {e}")
                raise

    def list_files(self, indexed: Optional[bool] = None) -> list[dict]:
        """
        List all tracked files, optionally filtered by indexed status.

        Args:
            indexed: If True/False, filter by indexed status. If None, return all.

        Returns:
            List of dictionaries containing file information
        """
        with self.get_session() as session:
            try:
                query = select(FileRecord)
                if indexed is not None:
                    query = query.where(FileRecord.indexed == indexed)
                results = session.execute(query).scalars().all()

                return [
                    {
                        "id": record.id,
                        "path": record.path,
                        "hash": record.hash,
                        "ingested_at": record.ingested_at.isoformat(),
                        "indexed": record.indexed,
                    }
                    for record in results
                ]

            except SQLAlchemyError as e:
                logger.error(f"Error listing files: {e}")
                return []
