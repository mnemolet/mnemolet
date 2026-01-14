import shutil
from datetime import datetime
from pathlib import Path

import click

from mnemolet.config import DEFAULT_CONFIG


@click.command("reset-config")
@click.option("--path", default="config.toml", help="Path to save config file.")
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite existing config.toml (creates a backup first).",
)
def init_config(path: str, force: bool):
    """
    Generate a default config.toml file.
    """
    import tomli_w

    config_path = Path(path)

    if config_path.exists() and not force:
        click.echo("config.toml already exists. Use --force to overwrite it.")
        return

    if config_path.exists() and force:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        backup_path = config_path.with_suffix(f".toml.bak-{timestamp}")
        click.echo(backup_path)
        shutil.copy2(config_path, backup_path)
        click.echo(f"Existing config backed up as {backup_path.name}")

    with open(config_path, "wb") as f:
        tomli_w.dump(DEFAULT_CONFIG, f)

    click.echo(f"Configuration written to {config_path}.")
