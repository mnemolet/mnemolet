import logging
from collections.abc import Iterator
from pathlib import Path

from mnemolet.cuore.ingestion.extractors.registry import get_extractor
from mnemolet.cuore.storage.db_tracker import DBTracker
from mnemolet.cuore.utils.utils import hash_file

logger = logging.getLogger(__name__)


def stream_files(
    dir: Path, tracker: DBTracker, force: bool = False
) -> Iterator[dict[str, str, str]]:
    """
    Yield files from a dir in chunks, skipping files already ingested.
    Duplicates by hash are skipped automatically.
    """
    seen_hashes = set()

    for file_path in dir.rglob("*"):
        extractor = get_extractor(file_path)
        logger.debug(f" -> extractor: {extractor}")
        if not extractor:
            continue

        file_hash = hash_file(file_path)

        # Skip if already ingested
        if not force and tracker.file_exists(file_hash):
            logger.info(f"Skipping already ingested: {file_path}")
            continue

        # Skip duplicates within current batch
        if file_hash in seen_hashes:
            logger.info(f"Skipping duplicate file in directory: {file_path}")
            continue

        seen_hashes.add(file_hash)

        try:
            file_added = False
            resolved_path = str(file_path.resolve())

            for content_part in extractor.extract(file_path):
                logger.debug(f"[LOADER] Received part: len={len(content_part)}")

                if not file_added:
                    tracker.add_file(resolved_path, file_hash)

                data = {
                    "path": resolved_path,
                    "content": content_part,
                    "hash": file_hash,
                }
            yield data
        except Exception as e:
            print(f"Skipping {file_path}: {e}")
