import logging
import threading
from typing import Iterable, Iterator, Optional

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_model: Optional[SentenceTransformer] = None
_model_lock = threading.Lock()


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                _model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
    return _model


def get_dimension() -> int:
    return _get_model().get_embedding_dimension()


def embed_texts_batch(
    texts: Iterable[str],
    batch_size: int = 512,
    show_progress: bool = False,
) -> Iterator[np.ndarray]:
    model = _get_model()
    batch = []
    for text in texts:
        batch.append(text)
        if len(batch) >= batch_size:
            embeddings = model.encode(
                batch, show_progress_bar=show_progress, convert_to_numpy=True
            ).astype(np.float32)
            yield embeddings
            batch = []
    if batch:
        embeddings = model.encode(
            batch, show_progress_bar=show_progress, convert_to_numpy=True
        ).astype(np.float32)
        yield embeddings
