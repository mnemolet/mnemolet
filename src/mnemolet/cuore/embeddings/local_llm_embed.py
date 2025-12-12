import logging
from typing import Iterable, Iterator

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

logger = logging.getLogger(__name__)

# detect GPU automatically, small embedding model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)


def embed_texts_batch(
    texts: Iterable[str],
    batch_size: int = 512,
    show_progress: bool = False,
) -> Iterator[np.ndarray]:
    """
    Generate embeddings in batches and save directly to disk.

    Args:
        texts: Iterable of text chunks to embed
        output_file: Path to save the embeddings (*.npy)
        batch_size: Number of items per batch

    Returns:
        a tuple (num_texts, embedding_dim) with the total number of chunks and
        the embedding vector dimension.
    """
    batch = []
    iterator = tqdm(texts, desc="Emdedding chunks", disable=not show_progress)

    for text in iterator:
        batch.append(text)
        if len(batch) >= batch_size:
            embeddings = model.encode(
                batch, convert_to_numpy=True, show_progress_bar=False, device=device
            ).astype(np.float32)
            yield embeddings
            batch = []

    # flush
    if batch:
        embeddings = model.encode(
            batch, convert_to_numpy=True, show_progress_bar=False, device=device
        ).astype(np.float32)
        yield embeddings


def get_dimension() -> int:
    """
    Returns dimension for a specific model using dummy data.
    """
    try:
        dummy = ["dummy"]
        dummy_embedding = next(embed_texts_batch(dummy, batch_size=1))
        return dummy_embedding.shape[1]
    except StopIteration:
        logger.warning("No embedding generated from dummy data.")
        return None
    except Exception as e:
        logger.error(f"Failed to get embedding dimension: {e}")
        return None
