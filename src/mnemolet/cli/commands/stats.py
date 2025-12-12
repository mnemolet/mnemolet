import click

from mnemolet.config import (
    QDRANT_COLLECTION,
    QDRANT_URL,
)

from .utils import requires_qdrant


@click.command()
@click.option(
    "--collection_name",
    default=QDRANT_COLLECTION,
    help="Define collection name.",
)
@requires_qdrant
def stats(collection_name: str):
    """
    Output statistics about Qdrant database.
    """
    from mnemolet.cuore.utils.qdrant import QdrantManager

    try:
        qm = QdrantManager(QDRANT_URL)
        stats = qm.get_collection_stats(collection_name)
    except Exception as e:
        click.echo(f"Failed to fetch stats: {e}")
        return

    click.echo(f"Qdrant Collection Stats: {stats['collection_name']}")
    click.echo("-" * 60)
    for k, v in stats.items():
        if k != "collection_name":
            click.echo(f"{k.replace('_', ' ').title():22}: {v}")
    click.echo("-" * 60)
