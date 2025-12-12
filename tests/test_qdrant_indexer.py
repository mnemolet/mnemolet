from unittest.mock import MagicMock, patch

from mnemolet.cuore.indexing.qdrant_indexer import QdrantIndexer

test_url = "http://localhost:6333"
test_collection = "test_collection"


@patch("mnemolet.cuore.indexing.qdrant_indexer.QdrantClient")
def test_init_collection(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    indexer = QdrantIndexer(qdrant_url=test_url, collection_name=test_collection)

    indexer.init_collection(vector_size=384)

    mock_client.recreate_collection.assert_called_once()
    args, kwargs = mock_client.recreate_collection.call_args
    assert kwargs["collection_name"] == "test_collection"
    assert kwargs["vectors_config"].size == 384


@patch("mnemolet.cuore.indexing.qdrant_indexer.QdrantClient")
def test_store_embeddings(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    indexer = QdrantIndexer(qdrant_url=test_url, collection_name=test_collection)
    texts = ["one", "two"]
    embeddings = [[0.1, 0.2], [0.3, 0.4]]
    metadata = [
        {"path": "p1", "hash": "h1"},
        {"path": "p2", "hash": "h2"},
    ]

    indexer.store_embeddings(texts, embeddings, metadata)

    mock_client.upsert.assert_called_once()
    args, kwargs = mock_client.upsert.call_args
    assert kwargs["collection_name"] == "test_collection"

    points = kwargs["points"]
    assert len(points) == 2
    assert points[0].payload["text"] == "one"
    assert points[1].payload["text"] == "two"
