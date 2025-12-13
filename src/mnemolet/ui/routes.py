from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from mnemolet.api.app import (
    do_ingestion,
    do_search,
    get_collections,
    get_stats,
)
from mnemolet.config import (
    OLLAMA_URL,
    QDRANT_URL,
)

ui_router = APIRouter()

templates = Jinja2Templates(directory="src/mnemolet/ui/templates")

API_BASE = "http://localhost:8000"  # TODO: hardcoded url


@ui_router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    from mnemolet.cuore.health.checks import get_status

    try:
        result = get_status(QDRANT_URL, OLLAMA_URL)
        error = None
    except Exception as e:
        result = None
        error = str(e)

    return templates.TemplateResponse(
        "index.html", {"request": request, "result": result, "error": error}
    )


@ui_router.get("/ingest", response_class=HTMLResponse)
async def ingest_form(request: Request):
    return templates.TemplateResponse("ingest.html", {"request": request})


@ui_router.post("/ingest", response_class=HTMLResponse)
async def ingest_submit(request: Request, files: list[UploadFile] = File(...)):
    saved_files, result = await do_ingestion(files, force=False)

    return templates.TemplateResponse(
        "ingest.html",
        {
            "request": request,
            "saved": saved_files,
            "result": result,
        },
    )


@ui_router.get("/list-collections", response_class=HTMLResponse)
async def list_collections_ui(request: Request):
    data = get_collections()
    return templates.TemplateResponse(
        "list_collections.html",
        {
            "request": request,
            "collections": data.get("collections", []),
            "status": data.get("status"),
        },
    )


@ui_router.get("/stats", response_class=HTMLResponse)
async def stats_ui(request: Request, collection_name: str = "documents"):
    stats = {}
    status = None
    error = None

    try:
        data = get_stats(collection_name)
        stats = data.get("data", {})
        status = data.get("status", {})
        error = None
    except Exception as e:
        error = f"Failed to fetch stats: {str(e)}"

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "stats": stats,
            "status": status,
            "error": error,
            "collection_name": collection_name,
        },
    )


@ui_router.get("/search", response_class=HTMLResponse)
async def search_ui(request: Request):
    return templates.TemplateResponse(
        "search.html", {"request": request, "results": None}
    )


@ui_router.post("/search", response_class=HTMLResponse)
async def search_ui_post(request: Request, query: str = Form(...)):
    data = do_search(query)
    return templates.TemplateResponse(
        "search.html",
        {"request": request, "results": data.get("results", []), "query": query},
    )


@ui_router.get("/answer", response_class=HTMLResponse)
async def answer_ui(request: Request):
    return templates.TemplateResponse(
        "answer.html", {"request": request, "results": None}
    )
