import logging
import sys
from functools import wraps
from importlib.metadata import PackageNotFoundError, version

import click

from mnemolet.config import (
    QDRANT_URL,
)
from mnemolet.cuore.utils.qdrant import QdrantManager

logger = logging.getLogger(__name__)

try:
    __version__ = version("mnemolet")
except PackageNotFoundError:
    __version__ = "0.1.0"


def requires_qdrant(f):
    """
    Decorator to check Qdrant before running a command.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        qm = QdrantManager(QDRANT_URL)
        if not qm.check_qdrant_status():
            sys.exit(1)
        return f(*args, **kwargs)

    return wrapper


@click.group()
@click.option(
    "-v", "--verbose", count=True, help="Increase output verbosity (use -v or -vv)"
)
@click.version_option(
    version=__version__,
    prog_name="MnemoLet",
)
@click.pass_context
def cli(ctx, verbose):
    """
    CLI for mnemolet.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    # map -v to INFO, --vv to DEBUG
    if verbose == 0:
        level = logging.WARNING
    elif verbose == 1:
        level = logging.INFO
    else:  # -vv or more
        level = logging.DEBUG

    # reset existing handlers
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    logger.debug(f"Logger init with level={level}")


def lazy_import(module: str, name: str):
    """
    Return a click command that imports its implementation only on execution.
    """

    logger.debug(f"[lazy_import] preparing to load {module}:{name}")

    def _wrapper(*args, **kwargs):
        logger.debug(f"[lazy_import] importing module {module}")
        mod = __import__(module, fromlist=[name])

        logger.debug(f"[lazy_import] accessing attribute {name}")
        return getattr(mod, name)

    cmd = _wrapper()

    return cmd


def register_commands():
    cli.add_command(lazy_import("mnemolet.cli.commands.config", "init_config"))
    cli.add_command(lazy_import("mnemolet.cli.commands.ingest", "ingest"))
    cli.add_command(lazy_import("mnemolet.cli.commands.search", "search"))
    cli.add_command(lazy_import("mnemolet.cli.commands.answer", "answer"))
    cli.add_command(lazy_import("mnemolet.cli.commands.stats", "stats"))
    cli.add_command(lazy_import("mnemolet.cli.commands.list", "list_collections"))
    cli.add_command(lazy_import("mnemolet.cli.commands.remove", "remove"))
    cli.add_command(lazy_import("mnemolet.cli.commands.serve", "serve"))
    cli.add_command(lazy_import("mnemolet.cli.commands.dashboard", "dashboard"))
    cli.add_command(lazy_import("mnemolet.cli.commands.chat", "chat"))


register_commands()

if __name__ == "__main__":
    cli()
