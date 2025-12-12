import logging
import time
from pathlib import Path

from tqdm import tqdm

from mnemolet.cuore.embeddings.local_llm_embed import (
    get_dimension,
)
from mnemolet.cuore.indexing.qdrant_indexer import QdrantIndexer
from mnemolet.cuore.ingestion.preprocessor import process_directory
from mnemolet.cuore.storage.db_tracker import DBTracker

logger = logging.getLogger(__name__)


def ingest(
    directory: str,
    batch_size: int,
    qdrant_url: str,
    collection_name: str,
    size_chars: int,
    force: bool,
) -> dict:
    """
    Ingest files from a directory into Qdrant.
    - streams files, chunks them, embeds text and stores data in Qdrant.
    """

    start_total = time.time()
    directory = Path(directory)

    files = list(directory.rglob("*"))
    files = [f for f in files if f.is_file()]
    if not files:
        logger.warning("No files found to ingest.")
        return
    logger.info(f"Found {len(files)} files to ingest from {directory}.")

    logger.info(f"Starting ingestion from {directory}")

    # SQLite db
    tracker = DBTracker()
    indexer = QdrantIndexer(qdrant_url, collection_name)
    embedding_dim = get_dimension()
    # runs only if there is no collection
    indexer.ensure_collection(vector_size=embedding_dim)
    total_chunks = 0
    total_files = 0  # can be actually different with files count

    chunk_batch = []
    metadata_batch = []

    pbar = tqdm(total=len(files), desc="Ingesting files", unit="file")

    seen_files = set()

    if force:
        embedding_dim = get_dimension()
        logger.info(f"Recreating Qdrant collection (dim={embedding_dim})..")
        indexer.init_collection(vector_size=embedding_dim)

    for data in process_directory(directory, tracker, force, size_chars):
        file_path = data["path"]
        file_hash = data["hash"]
        chunk = data["chunk"]

        if file_path not in seen_files:
            logger.info(f"Processing file #{total_files}: {file_path}")
            total_files += 1
            seen_files.add(file_path)
            pbar.update(1)  # increment progress bar

        # add to current batch
        chunk_batch.append(chunk)
        metadata_batch.append({"path": file_path, "hash": file_hash})
        total_chunks += 1

        # if batch full —> embed & store
        if len(chunk_batch) >= batch_size:
            _store_batch(indexer, chunk_batch, metadata_batch, embedding_dim, force)
            chunk_batch.clear()
            metadata_batch.clear()

    # handle the rest
    if chunk_batch:
        _store_batch(indexer, chunk_batch, metadata_batch, embedding_dim, force)

    pbar.close()

    total_time = time.time() - start_total

    return {"files": total_files, "chunks": total_chunks, "time": total_time}


def _store_batch(indexer, chunk_batch, metadata_batch, embedding_dim, force):
    from mnemolet.cuore.embeddings.local_llm_embed import (
        embed_texts_batch,
    )

    logger.info(f"Embedding batch of {len(chunk_batch)} chunks..")
    for embeddings in embed_texts_batch(chunk_batch, batch_size=len(chunk_batch)):
        indexer.store_embeddings(chunk_batch, embeddings, metadata_batch)
        logger.info(f"Stored {len(chunk_batch)} chunks in Qdrant.")
