import logging

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
)

from mnemolet.config import (
    EMBED_MODEL,
    MIN_SCORE,
    OLLAMA_MODEL,
    OLLAMA_URL,
    QDRANT_COLLECTION,
    QDRANT_URL,
    TOP_K,
)
from mnemolet.cuore.storage.chat_history import ChatHistory

logger = logging.getLogger(__name__)

api_router = APIRouter(prefix="/chat", tags=["chat"])


@api_router.post("/sessions")
def create_session():
    h = ChatHistory()
    session_id = h.create_session()
    return {"session_id": session_id}


@api_router.post("/sessions/{session_id}/messages")
async def send_message(session_id: int, request: Request):
    from mnemolet.cuore.query.generation.chat_runner import run_chat_turn
    from mnemolet.cuore.query.generation.local_generator import get_llm_generator
    from mnemolet.cuore.query.retrieval.retriever import get_retriever

    payload = await request.json()

    if "message" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'message' field")

    message = payload["message"]

    h = ChatHistory()

    if not h.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    # load previous messages from DB
    initial_messages = h.get_messages(session_id)

    retriever = get_retriever(
        url=QDRANT_URL,
        collection=QDRANT_COLLECTION,
        model=EMBED_MODEL,
        top_k=TOP_K,
        min_score=MIN_SCORE,
    )

    generator = get_llm_generator(OLLAMA_URL, OLLAMA_MODEL)

    assistant_msg = run_chat_turn(
        retriever=retriever,
        generator=generator,
        user_input=message,
        initial_messages=initial_messages,
        session_id=session_id,
        history_store=h,
    )

    return {"assistant": assistant_msg}


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
