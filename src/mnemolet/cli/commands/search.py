import click

from mnemolet.config import (
    EMBED_MODEL,
    MIN_SCORE,
    QDRANT_COLLECTION,
    QDRANT_URL,
    TOP_K,
)

from .utils import requires_qdrant


@click.command()
@click.argument("query", type=str)
@click.option(
    "--top-k", default=TOP_K, show_default=True, help="Number of results to retrieve."
)
@click.option(
    "--min-score", default=MIN_SCORE, show_default=True, help="Minimum score threshold."
)
@requires_qdrant
def search(query: str, top_k: int, min_score: float):
    """
    Search Qdrant for relevant documents.
    """
    from mnemolet.cuore.query.retrieval.search_documents import search_documents
    from mnemolet.cuore.utils.utils import filter_by_min_score

    results = search_documents(
        qdrant_url=QDRANT_URL,
        collection_name=QDRANT_COLLECTION,
        embed_model=EMBED_MODEL,
        query=query,
        top_k=top_k,
    )

    filtered_results = filter_by_min_score(results, min_score)

    if not filtered_results:
        click.echo("No results found.")
        return

    click.echo("\nTop results:\n")
    for i, r in enumerate(filtered_results, start=1):
        click.echo(
            f"{i}. (score={r['score']:.4f}) (path={r['path']}) {r['text'][:200]}...\n"
        )
