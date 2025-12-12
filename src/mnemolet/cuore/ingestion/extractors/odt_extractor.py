from pathlib import Path
from typing import Iterator

from mnemolet.cuore.ingestion.extractors.base import Extractor
from mnemolet.cuore.ingestion.loaders.odt_loader import extract_odt


class OdtExtractor(Extractor):
    extensions = {".odt"}

    def extract(self, file: Path) -> Iterator[str]:
        yield from extract_odt(file, self.chunk_size)
