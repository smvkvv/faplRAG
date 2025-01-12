import logging
from opensearchpy import OpenSearch
from datetime import datetime

from interface.embedder import Embedder
from interface.schemas import EmbedderSettings, Context
from interface.models_interface import Post

from utils.database import SessionLocal


logger = logging.getLogger(__name__)


def initialize_embedding_model(config: dict) -> Embedder:
    """
    Initializes and returns the embedding model using provided configuration.
    """
    try:
        settings = EmbedderSettings(**config["embedding_model"])
        embedder = Embedder(settings)
        logger.info(f"Initialized embedding model {settings.model_name}")
        return embedder
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {e}")
        raise


def build_context_from_vectordb_response(doc: Post) -> Context:
    return Context(uid=doc.uid,
                  text=doc.text_content,
                  title=doc.title,
                  tags=list(doc.tags),
                  n_visits=int(doc.n_visits),
                  dt=datetime.combine(doc.dt, datetime.min.time()),
                  href=f"http://fapl.ru/posts/{doc.uid}/",
                  source="vector")


def build_context_from_elastic_response(doc: dict) -> Context:
    return Context(uid=doc['uid'],
                  text=doc['text_content'],
                  title=doc['title'],
                  tags=list(doc['tags']),
                  n_visits=int(doc['n_visits']),
                  dt=datetime.fromisoformat(doc['dt']).replace(tzinfo=None),
                  href=f"http://fapl.ru/posts/{doc['uid']}/",
                  source="fulltext")


def retrieve_semantic_search(db, query: str, embedder: Embedder, config: dict) -> list[Context]:
    query_vector = embedder.encode([query], doc_type="query")[0].tolist()

    # Define parameters
    k = config["retrieval"]["top_k_vector"]
    similarity_threshold = config["retrieval"]["similarity_threshold"]

    # Query the database for the most similar contexts based on cosine similarity
    results = (
        db.query(
            Post,
            Post.vector.cosine_distance(query_vector).label("distance"),
        )
        .filter(
            Post.vector.cosine_distance(query_vector) < similarity_threshold
        )
        .order_by("distance")
        .limit(k)
        .all()
    )
    return [build_context_from_vectordb_response(res.Post) for res in results]


def retrieve_fulltext_search(os_client: OpenSearch, config: dict, question: str) -> list[Context]:
    top_k = config["retrieval"]["top_k_fulltext"]

    # Constructing the query for multiple fields
    query = {
        "query": {
            "bool": {
                "should": [
                    {"multi_match": {
                        "query": question,
                        "fields": ["title^2", "text_content"],  # Boosting title field
                        "type": "best_fields"
                    }},
                    {"term": {"tags": question.lower()}}  # Assuming tags are stored in lowercase
                ]
            }
        },
        "size": top_k
    }

    # Executing the search query
    response = os_client.search(index=config["os_params"]["index_name"], body=query)

    return [build_context_from_elastic_response(hit['_source']) for hit in response['hits']['hits']]


def deduplicate_and_sort(contexts: list[Context]) -> list[Context]:
    deduplicated = {context.uid: context for context in contexts}.values()
    sorted_contexts = sorted(deduplicated, key=lambda c: c.dt, reverse=True)

    return sorted_contexts


def retrieve_contexts(query: str, embedder: Embedder, config: dict, os_client: OpenSearch) -> list[Context]:
    """
    Retrieves the most relevant contexts from DataChunks for a given query using vector search.
    """
    db = SessionLocal()
    top_chunks = []
    try:
        if config["retrieval"]["vector_search_enabled"]:
            top_chunks.extend(retrieve_semantic_search(db, query, embedder, config))
        if config["retrieval"]["fulltext_search_enabled"]:
            top_chunks.extend(retrieve_fulltext_search(os_client, config, query))

        top_chunks = deduplicate_and_sort(top_chunks)

        result = top_chunks[:config["retrieval"]["top_k"]]
        logger.info(f"Retrieved top {len(result)} contexts for the query")
        return result
    except Exception as e:
        logger.error(f"Error retrieving contexts: {e}")
        raise
    finally:
        db.close()
