from pathlib import Path
from typing import Iterator

from mnemolet.cuore.ingestion.extractors.base import Extractor


class TextExtractor(Extractor):
    extensions = {
        # plain text
        ".txt",
        ".log",
        ".conf",
        ".ini",
        ".json",
        ".yml",
        ".toml",
        # code
        ".py",
        ".js",
        ".ts",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".rs",
        ".go",
        ".sh",
        ".bash",
        ".ps1",
        ".rb",
        ".php",
        "pl",
        # markdown
        # TODO: need additional work for csv and html
        ".md",
        ".html",
        ".xml",
        ".csv",
        ".tsv",
        ".css",
        # documentation
        ".rst",
        ".tex",
        ".jinja",
        ".jinja2",
        ".tpl",
    }

    def extract(self, file: Path) -> Iterator[str]:
        """
        Yield text chunks from a file.
        """
        with open(file, "r", encoding="utf-8") as f:
            while chunk := f.read(self.chunk_size):
                yield chunk
