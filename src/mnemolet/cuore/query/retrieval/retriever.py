from __future__ import annotations

from dataclasses import dataclass

from qdrant_client import QdrantClient

from mnemolet.cuore.query.retrieval.search_documents import search_documents
from mnemolet.cuore.utils.utils import filter_by_min_score


@dataclass
class RetrieverConfig:
    qdrant_url: str
    collection_name: str
    embed_model: str
    top_k: int
    min_score: float


class Retriever:
    def __init__(self, config: RetrieverConfig):
        self.cfg = config
        self._client = QdrantClient(url=config.qdrant_url)

    def retrieve(self, query: str) -> list[dict]:
        """
        Retrieve and filter context chunks from Qdrant.
        """
        try:
            results = search_documents(
                self.cfg.qdrant_url,
                self.cfg.collection_name,
                self.cfg.embed_model,
                query,
                self.cfg.top_k,
            )
            return filter_by_min_score(results, self.cfg.min_score)
        except Exception:
            return []

    def has_documents(self) -> bool:
        try:
            info = self._client.get_collection(self.cfg.collection_name)
            return info.points_count > 0
        except Exception:
            return False


def get_retriever(
    url: str, collection: str, model: str, top_k: int, min_score: float
) -> Retriever:
    cfg = RetrieverConfig(
        qdrant_url=url,
        collection_name=collection,
        embed_model=model,
        top_k=top_k,
        min_score=min_score,
    )
    return Retriever(cfg)
