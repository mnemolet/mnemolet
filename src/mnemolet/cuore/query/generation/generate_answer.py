import logging
from typing import Generator, Optional, Tuple

from mnemolet.cuore.query.generation.local_generator import (
    LocalGenerator,
)
from mnemolet.cuore.query.retrieval.retriever import Retriever
from mnemolet.cuore.utils.utils import _only_unique

logger = logging.getLogger(__name__)


def generate_answer(
    retriever: Retriever,
    generator: LocalGenerator,
    query: str,
    chat: bool = False,
) -> Generator[Tuple[str, Optional[list[dict]]], None, None]:
    """
    Wrapper around LocalGenerator.
    """
    filtered_results = retriever.retrieve(query)

    if not chat and not filtered_results:
        yield "No relevant documents found. Using general knowledge...\n\n", None

    context_chunks = [r["text"] for r in filtered_results]
    mode = "chat" if chat else "answer"
    logger.info(f"Generating {mode} response...")

    for c in _generate_llm_chunks(generator, query, context_chunks):
        yield c, None

    yield _yield_sources_if_any(filtered_results)


def _generate_llm_chunks(
    generator: LocalGenerator, query: str, context_chunks: list[str]
) -> Generator[str, None, None]:
    """
    Helper fn for streaming chunks from LocalGenerator.
    """
    yield from generator.generate_answer(query, context_chunks)


def _yield_sources_if_any(
    filtered_results: list[dict],
) -> Tuple[str, Optional[list[dict]]]:
    """
    Return sources if they exist, else empty list.
    """
    if filtered_results:
        return "", _only_unique(filtered_results)
    return "", []
