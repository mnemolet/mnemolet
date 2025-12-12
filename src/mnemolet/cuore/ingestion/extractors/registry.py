import importlib
import logging
import pkgutil
from pathlib import Path

from mnemolet.cuore.ingestion.extractors.base import Extractor

from . import __name__ as pkg_name
from . import __path__

logger = logging.getLogger(__name__)

_EXTRACTOR_REGISTRY: dict[str, Extractor] | None = None


def get_registry() -> dict[str, Extractor]:
    """
    Load and return extractor registry lazily (after logging is configured).
    """
    global _EXTRACTOR_REGISTRY
    if _EXTRACTOR_REGISTRY is None:
        # dynamically import all modules in extractors (except base and registry)
        for _, modname, _ in pkgutil.iter_modules(__path__):
            if modname not in {"base", "registry"}:
                importlib.import_module(f"{pkg_name}.{modname}")

        _EXTRACTOR_REGISTRY = {
            ext: cls() for cls in Extractor.__subclasses__() for ext in cls.extensions
        }

        logger.debug(f"EXTRACTOR_REGISTRY: {sorted(_EXTRACTOR_REGISTRY.keys())}")

    return _EXTRACTOR_REGISTRY


def get_extractor(file: Path) -> Extractor | None:
    """
    Return registered extractor for the given file extension.
    """
    return get_registry().get(file.suffix.lower())
