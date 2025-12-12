from pathlib import Path
from typing import Iterator

from docx import Document


def extract_docx(file: Path, chunk_size: int) -> Iterator[str]:
    """
    Yield text chunks from a DOCX.

    Args:
        file: DOCX file path.
        chunk_size: size of text chunks to yield.

    Yields:
        str: next chunk of text.
    """
    docx = Document(file)

    buffer = ""

    for par in docx.paragraphs:
        buffer += par.text + "\n"
        while len(buffer) >= chunk_size:
            yield buffer[:chunk_size]
            buffer = buffer[chunk_size:]

    if buffer:
        yield buffer
