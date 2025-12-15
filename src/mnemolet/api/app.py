import json
import logging
from typing import Any

from fastapi import (
    APIRouter,
    FastAPI,
    HTTPException,
)
from fastapi.responses import StreamingResponse

from mnemolet.api.routes.chat import api_router as chat_router
from mnemolet.api.routes.ingest import api_router as ingest_router
from mnemolet.config import (
    EMBED_MODEL,
    MIN_SCORE,
    OLLAMA_MODEL,
    OLLAMA_URL,
    QDRANT_COLLECTION,
    QDRANT_URL,
    TOP_K,
)
from mnemolet.cuore.utils.qdrant import QdrantManager

logger = logging.getLogger(__name__)

app = FastAPI(title="MnemoLet API", version="0.0.1")
api_router = APIRouter()

api_router.include_router(chat_router)
api_router.include_router(ingest_router)


@api_router.get("/search")
def search(
    query: str,
    qdrant_url: str = QDRANT_URL,
    collection_name: str = QDRANT_COLLECTION,
    embed_model: str = EMBED_MODEL,
    top_k: int = TOP_K,
):
    """
    Search documents in Qdrant.
    """
    return do_search(query, qdrant_url, collection_name, embed_model, top_k)


def do_search(
    query: str,
    qdrant_url: str = QDRANT_URL,
    collection_name: str = QDRANT_COLLECTION,
    embed_model: str = EMBED_MODEL,
    top_k: int = TOP_K,
):
    from mnemolet.cuore.query.retrieval.search_documents import search_documents

    try:
        results = search_documents(
            qdrant_url=QDRANT_URL,
            collection_name=QDRANT_COLLECTION,
            embed_model=EMBED_MODEL,
            query=query,
            top_k=top_k,
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")


@api_router.get("/answer")
def answer(
    query: str,
    qdrant_url: str = QDRANT_URL,
    collection_name: str = QDRANT_COLLECTION,
    embed_model: str = EMBED_MODEL,
    ollama_url: str = OLLAMA_URL,
    ollama_model: str = OLLAMA_MODEL,
    top_k: int = TOP_K,
):
    return StreamingResponse(
        get_answer(
            query,
            qdrant_url,
            collection_name,
            embed_model,
            ollama_url,
            ollama_model,
            top_k,
        ),
        media_type="application/json",
    )


def get_answer(
    query: str,
    qdrant_url: str = QDRANT_URL,
    collection_name: str = QDRANT_COLLECTION,
    embed_model: str = EMBED_MODEL,
    ollama_url: str = OLLAMA_URL,
    ollama_model: str = OLLAMA_MODEL,
    top_k: int = TOP_K,
) -> dict[str, Any]:
    """
    Generate answer from local LLM.
    """
    from mnemolet.cuore.query.generation.generate_answer import generate_answer
    from mnemolet.cuore.query.generation.local_generator import get_llm_generator
    from mnemolet.cuore.query.retrieval.retriever import get_retriever

    try:
        retriever = get_retriever(
            url=QDRANT_URL,
            collection=QDRANT_COLLECTION,
            model=EMBED_MODEL,
            top_k=top_k,
            min_score=MIN_SCORE,
        )
        generator = get_llm_generator(OLLAMA_URL, ollama_model)

        for chunk, sources in generate_answer(
            retriever=retriever,
            generator=generator,
            query=query,
        ):
            if chunk:
                # answer_chunks.append(answer)
                logger.info(f"Chunk: {chunk}")
                yield (json.dumps({"type": "chunk", "data": chunk}) + "\n").encode(
                    "utf-8"
                )
            elif sources:
                yield (json.dumps({"type": "sources", "data": sources}) + "\n").encode(
                    "utf-8"
                )

    except Exception as e:
        yield json.dumps({"type": "error", "data": str(e)}) + "\n"


@api_router.get("/stats")
def stats(collection_name: str):
    return get_stats(collection_name)


def get_stats(collection_name: str):
    """
    Output statistics about Qdrant database.
    """
    try:
        qm = QdrantManager(QDRANT_URL)
        stats = qm.get_collection_stats(collection_name)
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {e}")


@api_router.get("/list-collections")
def list_collections():
    return get_collections()


def get_collections():
    """
    List all Qdrant collections.
    """
    try:
        qm = QdrantManager(QDRANT_URL)
        xz = qm.list_collections()
        if not xz:
            return {
                "status": "success",
                "collections": [],
                "message": "No collections found.",
            }
        return {"status": "success", "collections": xz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {e}")


@api_router.get("/dashboard")
def dashboard():
    from mnemolet.cuore.health.checks import get_status

    return get_status(QDRANT_URL, OLLAMA_URL)
