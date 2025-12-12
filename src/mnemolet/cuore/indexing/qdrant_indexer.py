import logging
import uuid

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

logger = logging.getLogger(__name__)


class QdrantIndexer:
    def __init__(self, qdrant_url: str, collection_name: str):
        """
        Init Qdrant client using config.toml.
        """
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name

    def init_collection(self, vector_size: int = 384):
        """
        Delete and recreate Qdrant collection.
        """
        logger.info(f"Recreating Qdrant collection (dim={vector_size})..")
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    def ensure_collection(self, vector_size: int = 384):
        """
        Create collection only if it does not exist.
        """
        if not self.client.collection_exists(self.collection_name):
            logger.info(f"Creating Qdrant collection (dim={vector_size})..")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
        else:
            logger.info(f"Collection {self.collection_name} already exists.")

    def store_embeddings(
        self, chunks: list[str], embeddings: np.ndarray, metadata: list[dict[str, str]]
    ):
        """
        Store text embeddings in Qdrant.
        """
        payloads = [
            {"path": m["path"], "hash": m["hash"], "text": chunk}
            for m, chunk in zip(metadata, chunks)
        ]

        # build Qdrand points
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embeddings[i],
                payload=payloads[i],
            )
            for i in range(len(chunks))
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)

        info = self.client.get_collection(self.collection_name)
        points_count = info.points_count
        indexed_count = info.indexed_vectors_count
        logger.info(
            f"Upserted → total points: {points_count}, indexed: {indexed_count}"
        )
