import tempfile
from pathlib import Path

from mnemolet.cuore.ingestion.preprocessor import process_directory
from mnemolet.cuore.storage.db_tracker import DBTracker
from mnemolet.cuore.utils.utils import hash_file


def test_load_txt_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # create tmp files
        (tmp_path / "file1.txt").write_text("Hello world", encoding="utf-8")
        (tmp_path / "file2.txt").write_text("Another file", encoding="utf-8")
        (tmp_path / "empty.txt").write_text("", encoding="utf-8")

        tracker = DBTracker()
        files = list(process_directory(tmp_path, tracker, force=False, max_length=3000))

        # skip empty files
        assert len(files) == 2

        for f in files:
            assert set(f.keys()) == {"path", "hash", "chunk"}
            assert f["path"].endswith(".txt")
            assert len(f["chunk"]) > 0
            assert f["hash"] == hash_file(Path(f["path"]))

        # validate content
        chunks = [f["chunk"] for f in files]
        assert any("Hello world" in c for c in chunks)
        assert any("Another file" in c for c in chunks)
