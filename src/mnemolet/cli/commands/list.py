import click

from mnemolet.config import (
    QDRANT_URL,
)
from mnemolet.cuore.utils.qdrant import QdrantManager

from .utils import requires_qdrant


@click.command()
@requires_qdrant
def list_collections():
    """
    List all Qdrant collections.
    """
    qm = QdrantManager(QDRANT_URL)
    xz = qm.list_collections()
    if not xz:
        click.echo("No collections found.")
    else:
        click.echo("Collections in Qdrant:")
        for x in xz:
            click.echo(f"- {x}")
