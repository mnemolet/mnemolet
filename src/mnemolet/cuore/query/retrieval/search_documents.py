from qdrant_client.http.exceptions import UnexpectedResponse

from mnemolet.cuore.query.retrieval.qdrant import Qdrant


def search_documents(
    qdrant_url: str, collection_name: str, embed_model: str, query: str, top_k: int
):
    """
    Wrapper around QdrantRetriever.
    """
    xz = Qdrant(qdrant_url, collection_name, embed_model)
    try:
        return xz.search(query, top_k)

    # collection does not exist
    except UnexpectedResponse as e:
        if e.status_code == 404:
            return []
        raise
