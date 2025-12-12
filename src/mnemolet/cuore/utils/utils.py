import hashlib
from pathlib import Path
from typing import Any


def filter_by_min_score(
    raw: list[dict[str, Any]], min_score: float
) -> list[dict[str, Any]]:
    """
    Return only results with score >= min_score.
    """
    filtered = []
    for r in raw:
        try:
            score = float(r.get("score", 0))
            if score >= min_score:
                filtered.append(r)
        except (ValueError, TypeError):
            continue
    return filtered


def _only_unique(xz: list) -> list:
    """
    Helper fn to return only unique results by file path.
    """
    unique = []
    seen = set()

    for x in xz:
        path = x["path"]
        if path not in seen:
            seen.add(path)
            unique.append(x)
    return unique


def hash_file(path: Path) -> str:
    """
    Return SHA256 hash of file content
    """
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        # reads 8KB (8192), stops when get to b"" (empty byte)
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
