import logging

import requests
from qdrant_client import QdrantClient
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class QdrantManager:
    def __init__(self, qdrant_url: str):
        """
        Init Qdrant client once.
        """
        self.qdrant_url = qdrant_url
        self.client = QdrantClient(url=qdrant_url)

    def check_qdrant_status(self, endpoint: str = "healthz") -> bool:
        """
        Check if Qdrant is alive, ready, or healthy via its HTTP status endpoint.

        Return bool

        Reference:
            https://qdrant.tech/documentation/guides/monitoring/
        """
        try:
            response = requests.get(self.qdrant_url, timeout=2)
            if response.status_code == 200:
                logger.info(f"Qdrant {endpoint} check passed at {self.qdrant_url}")
                return True
            else:
                logger.warning(
                    f"Unexpected response from {self.qdrant_url}: {response.text}"
                )
                return False
        except RequestException as e:
            logger.error(f"Could not connect to Qdrant at {self.qdrant_url}: {e}")
            return False

    def collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def get_collection_stats(self, collection_name: str) -> dict:
        """
        Return collection stats as a dictionary.
        """
        info = self.client.get_collection(collection_name)

        return {
            "collection_name": collection_name,
            "status": info.status,
            "optimizer_status": info.optimizer_status,
            "points_count": info.points_count,
            "indexed_vectors_count": info.indexed_vectors_count,
            "segment_count": info.segments_count,
            "vector_size": info.config.params.vectors.size,
            "distance": info.config.params.vectors.distance,
            "on_disk_payload": info.config.params.on_disk_payload,
        }

    def remove_collection(self, collection_name: str) -> None:
        """
        Delete Qdrant collection.
        """
        self.client.delete_collection(collection_name=collection_name)

    def list_collections(self) -> list[str]:
        """
        Return a list of all collection names in Qdrant.
        """
        info = self.client.get_collections()
        return [c.name for c in info.collections]
