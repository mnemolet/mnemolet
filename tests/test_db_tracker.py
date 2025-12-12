import os

from mnemolet.config import DB_PATH
from mnemolet.cuore.storage.db_tracker import DBTracker


def setup_module(module):
    """
    Remove db before tests (clean run).
    """
    if DB_PATH.exists():
        os.remove(DB_PATH)


def test_add_and_list_files():
    tracker = DBTracker()
    path = "example.txt"
    file_hash = "example_hash"

    tracker.add_file(path, file_hash)
    assert tracker.file_exists(file_hash) is True

    files = tracker.list_files()
    assert len(files) == 1
    assert files[0]["path"] == path

    tracker.mark_indexed(file_hash)
    indexed_files = tracker.list_files(indexed=True)
    assert len(indexed_files) == 1
