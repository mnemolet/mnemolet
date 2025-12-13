import logging

from fastapi import (
    APIRouter,
)

from mnemolet.cuore.storage.chat_history import ChatHistory

logger = logging.getLogger(__name__)

api_router = APIRouter(prefix="/chat", tags=["chat"])


@api_router.get("/sessions")
def list_sessions():
    return ChatHistory().list_sessions()


@api_router.get("/sessions/{session_id}")
def show_session(session_id: int):
    h = ChatHistory()
    return h.get_messages(session_id)
