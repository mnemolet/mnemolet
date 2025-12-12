from pathlib import Path
from typing import Iterator

from odfdo import Document


def extract_odt(file: Path, chunk_size: int) -> Iterator[str]:
    """
    Yield text chunks from a ODT.

    Args:
        file: ODT file path.
        chunk_size: size of text chunks to yield.

    Yields:
        str: next chunk of text.

    Reference:
        - ODFDO Recipies: https://jdum.github.io/odfdo/recipes.html
    """
    odt = Document(file)
    text = odt.get_formatted_text()

    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size]
