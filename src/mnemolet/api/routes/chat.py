import logging

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
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


@api_router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: int):
    h = ChatHistory()
    if not h.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    h.delete_session(session_id)


@api_router.delete("/sessions", status_code=204)
def prune_session(confirm: bool = Query(False)):
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required. Use ?confirm=true",
        )
    h = ChatHistory()
    h.delete_all_sessions()
