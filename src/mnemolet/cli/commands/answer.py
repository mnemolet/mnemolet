import logging

import click

from mnemolet.config import (
    EMBED_MODEL,
    MIN_SCORE,
    OLLAMA_PROMPT,
    OLLAMA_URL,
    QDRANT_COLLECTION,
    QDRANT_URL,
    TOP_K,
)

from .utils import requires_qdrant

logger = logging.getLogger(__name__)


@click.command()
@click.argument("query", type=str)
@click.option(
    "--top-k",
    default=TOP_K,
    show_default=True,
    help="Number of context chunks for generation.",
)
@click.option(
    "--ollama-url",
    default=OLLAMA_URL,
    show_default=True,
    help="Ollama url",
)
@click.option(
    "--ollama-model",
    default="llama3",
    show_default=True,
    help="Local model to use for generation.",
)
@click.option(
    "--min-score", default=MIN_SCORE, show_default=True, help="Minimum score threshold."
)
@requires_qdrant
def answer(
    ollama_url: str, query: str, top_k: int, ollama_model: str, min_score: float
):
    """
    Search Qdrant and generate an answer using local LLM.
    """
    from mnemolet.cuore.query.generation.generate_answer import generate_answer
    from mnemolet.cuore.query.generation.local_generator import get_llm_generator
    from mnemolet.cuore.query.retrieval.retriever import get_retriever

    retriever = get_retriever(
        url=QDRANT_URL,
        collection=QDRANT_COLLECTION,
        model=EMBED_MODEL,
        top_k=top_k,
        min_score=min_score,
    )

    generator = get_llm_generator(
        url=OLLAMA_URL,
        model=ollama_model,
        prompt=OLLAMA_PROMPT,
    )

    click.echo("Generating answer..")

    for chunk, sources in generate_answer(
        retriever=retriever,
        generator=generator,
        query=query,
    ):
        if sources is None:
            click.echo(chunk, nl=False)

    click.echo("\n")

    # retrieve sources from results
    if sources:
        click.echo("\nSources:\n")
        for i, r in enumerate(sources, start=1):
            click.echo(f"{i}. {r['path']} (score={r['score']:.4f})")
