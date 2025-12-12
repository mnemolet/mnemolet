from pathlib import Path

from pypdf import PdfReader


def extract_pdf(file: Path, chunk_size: int) -> str:
    """
    Yield text chunks from a PDF.

    Args:
        file: PDF file path.
        chunk_size: size of text chunks to yield.

    Yields:
        str: next chunk of text from PDF.
    """
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if not page_text:
            continue

        text += page_text + "\n"

        while len(text) >= chunk_size:
            yield text[:chunk_size]
            text = text[chunk_size]

    if text:
        yield text
