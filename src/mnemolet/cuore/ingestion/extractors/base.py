import logging
from pathlib import Path
from typing import Iterator

from mnemolet.config import CHUNK_SIZE

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 1024 * 1024


class Extractor:
    """
    Base extractor class.
    All extractors must define supported extensions and implement extract().
    """

    extensions: set[str] = set()

    def __init__(self, chunk_size: int | None = None):
        if chunk_size is not None:
            self.chunk_size = chunk_size
            logger.info(f"Using user-provided chunk size: {self.chunk_size}")
        elif isinstance(CHUNK_SIZE, int) and CHUNK_SIZE > 0:
            self.chunk_size = CHUNK_SIZE
            logger.info(f"Using chunk size from config.toml: {self.chunk_size}")
        else:
            self.chunk_size = DEFAULT_CHUNK_SIZE
            logger.warning(
                f"CHUNK_SIZE from config is invalid or missing. "
                f"Using default chunk size: {self.chunk_size}"
            )

    def extract(self, file: Path) -> Iterator[str]:
        """
        Yield text chunks from file.
        """
        raise NotImplementedError("Subclasses must implement extract()")
