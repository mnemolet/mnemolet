import click

from mnemolet.config import (
    QDRANT_COLLECTION,
    QDRANT_URL,
)
from mnemolet.cuore.utils.qdrant import QdrantManager

from .utils import requires_qdrant


@click.command()
@click.option(
    "--collection_name",
    default=QDRANT_COLLECTION,
    help="Define collection name.",
)
@requires_qdrant
def remove(collection_name: str):
    """
    Remove Qdrant collection.
    """
    click.confirm(
        f"Are you sure you want to delete the collection '{collection_name}'?",
        abort=True,
    )
    try:
        qm = QdrantManager(QDRANT_URL)
        qm.remove_collection(collection_name)
        click.echo(f"Collection '{collection_name}' removed successfully.")
    except Exception as e:
        click.echo(f"Failed to remove collection '{collection_name}': {e}")
