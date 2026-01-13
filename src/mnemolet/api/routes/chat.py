import logging

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
    Response,
)
from fastapi.responses import StreamingResponse

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
from mnemolet.cuore.utils.export_session import export_session

logger = logging.getLogger(__name__)

api_router = APIRouter(prefix="/chat", tags=["chat"])


@api_router.post("/sessions")
def create_session():
    h = ChatHistory()
    session_id = h.create_session()
    return {"session_id": session_id}


@api_router.post("/sessions/messages")
async def send_message(request: Request):
    import json

    from mnemolet.cuore.query.generation.chat_runner import run_chat_turn
    from mnemolet.cuore.query.generation.local_generator import get_llm_generator
    from mnemolet.cuore.query.retrieval.retriever import get_retriever

    payload = await request.json()

    if "message" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'message' field")

    message = payload["message"]
    session_id = payload.get("session_id")  # optional

    h = ChatHistory()
    if session_id is None:
        session_id = h.create_session()
    elif not h.session_exists(session_id):
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

    assistant_chunks = []

    # save user message
    h.add_message(session_id, "user", message)

    def stream_response():
        for c in run_chat_turn(
            retriever=retriever,
            generator=generator,
            user_input=message,
            messages=initial_messages,
            session_id=session_id,
            stream=True,
        ):
            assistant_chunks.append(c)
            data = json.dumps({"type": "chunk", "data": c})
            yield f"{data}\n".encode("utf-8")

        # save assistant message
        full_msg = "".join(assistant_chunks).strip()
        if full_msg:
            h.add_message(session_id, "assistant", full_msg)
        done = json.dumps({"type": "done", "session_id": session_id})
        yield f"{done}\n".encode("utf-8")

    return StreamingResponse(stream_response(), media_type="application/json")


@api_router.get("/sessions")
def list_sessions():
    return ChatHistory().list_sessions()


@api_router.get("/sessions/{session_id}")
def show_session(
    session_id: int,
    format: str = Query("json", enum=["json", "text"]),
):
    h = ChatHistory()
    session = h.get_session(session_id)
    messages = h.get_messages(session_id)

    if not h.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    output = export_session(
        session=session,
        messages=messages,
        fmt=format,
    )

    if format == "text":
        return Response(
            content=output,
            media_type="text/plain; charset=utf-8",
        )

    # json
    return Response(
        content=output,
        media_type="application/json",
    )


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


@api_router.patch("/sessions/{session_id}")
async def rename_chat_session(request: Request, session_id: int):
    data = await request.json()

    title = (data.get("title") or "").strip()

    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    if len(title) > 50:
        raise HTTPException(status_code=400, detail="Title too long (max 50 chars)")

    h = ChatHistory()

    if not h.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    h.rename_session(session_id, title)

    return {
        "status": "ok",
        "session_id": session_id,
        "title": title,
    }
