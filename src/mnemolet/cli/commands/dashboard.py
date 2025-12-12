import json

import click

from mnemolet.config import (
    OLLAMA_URL,
    QDRANT_URL,
)


@click.command()
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output in JSON format.",
)
def dashboard(json_output: bool):
    """
    Show system and service health status.
    """
    from mnemolet.cuore.health.checks import get_status

    status = get_status(QDRANT_URL, OLLAMA_URL)

    if json_output:
        click.echo(json.dumps(status, indent=2))
    else:
        for k, v in status.items():
            if isinstance(v, dict):
                click.echo(f"{k}:")
                for k2, v2 in v.items():
                    click.echo(f"  {k2}: {v2}")
            else:
                click.echo(f"{k}: {v}")
