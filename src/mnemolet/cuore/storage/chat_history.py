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
        with self.get_session() as session:
            try:
                session_obj = ChatSession(
                    title=title,
                    created_at=datetime.now(UTC),
                )
                session.add(session_obj)
                session.flush()
                session.commit()
                logger.debug(f"Created chat session: {session_obj.id}")
                return session_obj.id
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error creating session: {e}")
                raise

    def add_message(self, session_id: int, role: str, message: str) -> int:
        """Add a message to a chat session and return its ID."""
        with self.get_session() as session:
            try:
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
                session.commit()
                logger.debug(f"Added message to session {session_id}: {role}")
                return chat_message.id
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error adding message: {e}")
                raise

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
                        "message_count": len(s.messages),
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
        with self.get_session() as session:
            try:
                session_obj = session.get(ChatSession, session_id)
                if not session_obj:
                    logger.warning(f"Session {session_id} not found for deletion")
                    return False
                session.delete(session_obj)
                session.commit()
                logger.debug(f"Deleted session {session_id} and its messages")
                return True
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error deleting session {session_id}: {e}")
                raise

    def delete_all_sessions(self) -> int:
        """Delete all sessions and messages. Returns count of deleted sessions."""
        with self.get_session() as session:
            try:
                result = session.execute(select(ChatSession))
                sessions = result.scalars().all()
                count = len(sessions)
                for s in sessions:
                    session.delete(s)
                session.commit()
                logger.debug(f"Deleted {count} sessions and all associated messages")
                return count
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error deleting all sessions: {e}")
                raise

    def rename_session(self, session_id: int, title: str) -> bool:
        """Rename a chat session."""
        with self.get_session() as session:
            try:
                session_obj = session.get(ChatSession, session_id)
                if not session_obj:
                    logger.warning(f"Session {session_id} not found for renaming")
                    return False
                session_obj.title = title
                session.commit()
                logger.debug(f"Renamed session {session_id} to '{title}'")
                return True
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error renaming session {session_id}: {e}")
                raise