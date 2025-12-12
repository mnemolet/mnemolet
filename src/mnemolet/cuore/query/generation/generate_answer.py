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
    chat: bool = False,  # default for answer endpoint
) -> Generator[Tuple[str, Optional[list[dict]]], None, None]:
    """
    Wrapper around LocalGenerator.
    """
    # ------- Retrieval -------
    filtered_results = retriever.retrieve(query)

    # ------- Answer mode -------
    if not chat:
        if not filtered_results:
            yield "No relevant information found.", []
            return

        # generator = LocalGenerator(ollama_url, model)
        context_chunks = [r["text"] for r in filtered_results]
        logger.info("Generating answer..")

        # stream LLM output
        for c in _generate_llm_chunks(generator, query, context_chunks):
            yield c, None

        # finally send sources
        yield _yield_sources_if_any(filtered_results)
        return

    # ------- Chat mode -------
    if filtered_results:
        logger.info("Relevant context found for chat.")
        context_chunks = [r["text"] for r in filtered_results]
    else:
        logger.info("No relevant context found; continue chat without context.")
        context_chunks = []

    logger.info("Generating chat response...")

    # stream LLM output
    for c in _generate_llm_chunks(generator, query, context_chunks):
        yield c, None

    # return sources only if we had any
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
