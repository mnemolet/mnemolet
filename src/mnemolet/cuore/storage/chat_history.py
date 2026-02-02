import logging
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from mnemolet.cuore.storage.base_db import BaseDatabaseManager
from mnemolet.cuore.storage.models import ChatMessage, ChatSession

logger = logging.getLogger(__name__)


class ChatHistory(BaseDatabaseManager):
    def create_session(self, title: str = "New Chat") -> int:
        """Create a new chat session and return its ID."""

        def _operation(session):
            session_obj = ChatSession(
                title=title,
                created_at=datetime.now(UTC),
            )
            session.add(session_obj)
            session.flush()  # Get ID before commit
            logger.debug(f"Created chat session: {session_obj.id}")
            return session_obj.id

        return self._safe_execute(_operation)

    def add_message(self, session_id: int, role: str, message: str) -> int:
        """Add a message to a chat session and return its ID."""

        def _operation(session):
            # Verify session exists first
            session_obj = session.get(ChatSession, session_id)
            if not session_obj:
                raise ValueError(f"Session {session_id} not found")

            chat_message = ChatMessage(
                session_id=session_id,
                role=role,
                message=message,
                created_at=datetime.now(UTC),
            )
            session.add(chat_message)
            session.flush()
            logger.debug(f"Added message to session {session_id}: {role}")
            return chat_message.id

        return self._safe_execute(_operation)

    def get_chat_session(self, session_id: int) -> Optional[dict]:
        """Get session metadata by ID."""
        with self.get_session() as session:
            try:
                result = session.get(ChatSession, session_id)
                if not result:
                    return None
                return {
                    "id": result.id,
                    "title": result.title,
                    "created_at": result.created_at.isoformat(),
                }
            except SQLAlchemyError as e:
                logger.error(f"Error getting session {session_id}: {e}")
                return None

    def get_messages(self, session_id: int) -> list[dict]:
        """Get all messages for a session ordered by creation time."""
        with self.get_session() as session:
            try:
                messages = (
                    session.execute(
                        select(ChatMessage)
                        .where(ChatMessage.session_id == session_id)
                        .order_by(ChatMessage.created_at)
                    )
                    .scalars()
                    .all()
                )

                return [
                    {
                        "id": msg.id,
                        "role": msg.role,
                        "message": msg.message,
                        "created_at": msg.created_at.isoformat(),
                    }
                    for msg in messages
                ]
            except SQLAlchemyError as e:
                logger.error(f"Error getting messages for session {session_id}: {e}")
                return []

    def list_sessions(self) -> list[dict]:
        """List all chat sessions ordered by creation time (newest first)."""
        with self.get_session() as session:
            try:
                sessions = (
                    session.execute(
                        select(ChatSession).order_by(ChatSession.created_at.desc())
                    )
                    .scalars()
                    .all()
                )

                return [
                    {
                        "id": s.id,
                        "title": s.title,
                        "created_at": s.created_at.isoformat(),
                        "message_count": len(s.messages),  # Uses relationship
                    }
                    for s in sessions
                ]
            except SQLAlchemyError as e:
                logger.error(f"Error listing sessions: {e}")
                return []

    def session_exists(self, session_id: int) -> bool:
        """Check if a chat session exists."""
        with self.get_session() as session:
            try:
                return session.get(ChatSession, session_id) is not None
            except SQLAlchemyError as e:
                logger.error(f"Error checking session existence {session_id}: {e}")
                return False

    def delete_session(self, session_id: int) -> bool:
        """Delete a session and all its messages (cascade handled by ORM)."""

        def _operation(session):
            session_obj = session.get(ChatSession, session_id)
            if not session_obj:
                logger.warning(f"Session {session_id} not found for deletion")
                return False

            session.delete(session_obj)
            logger.debug(f"Deleted session {session_id} and its messages")
            return True

        return self._safe_execute(_operation)

    def delete_all_sessions(self) -> int:
        """Delete all sessions and messages. Returns count of deleted sessions."""

        def _operation(session):
            result = session.execute(select(ChatSession))
            sessions = result.scalars().all()
            count = len(sessions)

            for s in sessions:
                session.delete(s)

            logger.debug(f"Deleted {count} sessions and all associated messages")
            return count

        return self._safe_execute(_operation)

    def rename_session(self, session_id: int, title: str) -> bool:
        """Rename a chat session."""

        def _operation(session):
            session_obj = session.get(ChatSession, session_id)
            if not session_obj:
                logger.warning(f"Session {session_id} not found for renaming")
                return False

            session_obj.title = title
            logger.debug(f"Renamed session {session_id} to '{title}'")
            return True

        return self._safe_execute(_operation)

    def _row_to_dict(self, row):
        return dict(row) if row else None

    def _rows_to_dicts(self, rows):
        return [dict(r) for r in rows]
