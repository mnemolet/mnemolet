import sys
from functools import wraps

from mnemolet.config import (
    QDRANT_URL,
)
from mnemolet.cuore.utils.qdrant import QdrantManager


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
