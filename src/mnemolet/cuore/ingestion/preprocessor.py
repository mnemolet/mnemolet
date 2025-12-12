import logging
from pathlib import Path

from mnemolet.cuore.ingestion.loader import stream_files
from mnemolet.cuore.storage.db_tracker import DBTracker

logger = logging.getLogger(__name__)


def chunk_text(text: str, max_length: int = 3000) -> list[str]:
    """
    Split large text into smaller chunks (by chars).

    Args:
        text: input text
        max_length: chunk size in words
    """
    chunks = []
    text_len = len(text)

    logger.info(f"[CHUNK] Total text length: {text_len} chars")
    logger.info(f"[CHUNK] Max chunk size: {max_length} chars")

    start = 0
    chunk_count = 0

    while start < text_len:
        end = start + max_length
        chunk = text[start:end]
        chunks.append(chunk)
        chunk_count += 1

        logger.debug(
            f"[CHUNK] Chunk #{chunk_count}: start={start},"
            f"end={min(end, text_len)}, length={len(chunk)}"
        )

        start = end

    logger.info(f"[CHUNK] Total chunks created: {chunk_count}")

    return chunks


def process_directory(dir: Path, tracker: DBTracker, force: bool, max_length: int):
    """
    Combine file streaming and chunking.
    """
    for data in stream_files(dir, tracker, force):
        for chunk in chunk_text(data["content"], max_length=max_length):
            yield {
                "path": data["path"],
                "chunk": chunk,
                "hash": data["hash"],
            }
