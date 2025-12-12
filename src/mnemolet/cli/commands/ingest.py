import logging

import click

from mnemolet.config import (
    BATCH_SIZE,
    QDRANT_COLLECTION,
    QDRANT_URL,
    SIZE_CHARS,
)

from .utils import requires_qdrant

logger = logging.getLogger(__name__)


@click.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--force", is_flag=True, help="Recreate Qdrant collection and reindex all files."
)
@click.option(
    "--batch-size",
    default=BATCH_SIZE,
    show_default=True,
    help="Number of chunks per batch.",
)
@click.pass_context
@requires_qdrant
def ingest(ctx, directory: str, force: bool, batch_size: int):
    """
    Ingest files from a directory into Qdrant.
    - streams files, chunks them, embeds text and stores data in Qdrant.
    """
    from mnemolet.cuore.ingestion.ingest import ingest

    result = ingest(
        directory, batch_size, QDRANT_URL, QDRANT_COLLECTION, SIZE_CHARS, force=force
    )

    click.echo(
        f"Ingestion complete: {result['files']} files, {result['chunks']} stored in "
        f"Qdrant in {result['time']:.1f}s.\n"
    )
