from mnemolet.cuore.ingestion.preprocessor import chunk_text


def test_chunk_text():
    text = " ".join(["word"] * 2700)
    max_chars = 500
    chunks = chunk_text(text, max_length=max_chars)

    total_length = sum(len(c) for c in chunks)
    assert total_length == len(text)

    assert all(isinstance(c, str) for c in chunks)
