from typing import Any

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


class Qdrant:
    def __init__(self, qdrant_url: str, collection_name, model: str):
        self.model = SentenceTransformer(model)
        self.client = QdrantClient(qdrant_url)
        self.collection_name = collection_name

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        query_vector = self.model.encode(query).tolist()

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )

        return [
            {
                "id": i.id,
                "text": i.payload.get("text", ""),
                "score": i.score,
                "path": i.payload.get("path", ""),
                "hash": i.payload.get("hash", ""),
            }
            for i in results.points
        ]
