import numpy as np

from mnemolet.cuore.embeddings.local_llm_embed import embed_texts_batch


def test_embed_texts_batch_basic():
    texts = ["Hello world", "Another chunk"]
    embeddings = list(embed_texts_batch(texts, batch_size=10))

    # one batch, because we have 2 texts
    assert len(embeddings) == 1

    batch = embeddings[0]
    assert isinstance(batch, np.ndarray)
    assert batch.shape == (len(texts), 384)
    assert batch.dtype == np.float32

    assert not np.allclose(batch[0], batch[1])


def test_embed_texts_batch_multiple_batches():
    texts = [f"text {i}" for i in range(20)]
    batch_size = 8
    batches = list(embed_texts_batch(texts, batch_size=batch_size))

    # expect ceil(20/8) = 3 batches
    assert len(batches) == 3

    total_embs = sum(b.shape[0] for b in batches)
    assert total_embs == len(texts)
    for b in batches:
        assert b.shape[1] == 384
        assert b.dtype == np.float32


def test_embed_texts_batch_empty():
    embeddings = list(embed_texts_batch([]))

    assert embeddings == []
