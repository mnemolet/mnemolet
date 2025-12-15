import logging

from fastapi import (
    APIRouter,
    File,
    Query,
    UploadFile,
)

from mnemolet.config import (
    BATCH_SIZE,
    QDRANT_COLLECTION,
    QDRANT_URL,
    SIZE_CHARS,
    UPLOAD_DIR,
)

logger = logging.getLogger(__name__)

api_router = APIRouter()


@api_router.post("/ingest")
async def ingest_files(
    files: list[UploadFile] = File(...),
    force: bool = Query(
        False, description="Recreate Qdrant collection before ingestion"
    ),
):
    """
    Ingest multiple files into Qdrant.
    """
    saved_files, result = await do_ingestion(files, force)

    return {
        "status": "ok",
        "uploaded": saved_files,
        "force": force,
        "message": "Ingestion complete",
        "ingestion": {
            "files": result["files"],
            "chunks": result["chunks"],
            "time": result["time"],
        },
    }


async def do_ingestion(files, force: bool = False):
    from mnemolet.cuore.ingestion.ingest import ingest

    saved_files = []

    for f in files:
        dest = UPLOAD_DIR / f.filename

        content = await f.read()
        dest.write_bytes(content)

        saved_files.append(str(dest))

    batch_size = BATCH_SIZE
    result = ingest(
        UPLOAD_DIR, batch_size, QDRANT_URL, QDRANT_COLLECTION, SIZE_CHARS, force=force
    )

    return saved_files, result
