import logging
from opensearchpy import OpenSearch
from gigachat import GigaChat

from interface.schemas import Context
from interface.embedder import Embedder
from interface.retrieval import retrieve_contexts
from interface.llm_client import generate_response, rewrite_query


logger = logging.getLogger(__name__)


def process_request(config: dict, embedder: Embedder, llm_client: GigaChat, query: str, os_client: OpenSearch) -> dict | str:
    """
    Processes the incoming query by retrieving relevant contexts and generating a response.
    """
    try:
        rewrited_query = rewrite_query(llm_client, query, config)
        contexts: list[Context] = retrieve_contexts(rewrited_query, embedder, config, os_client)

        # Generate the response
        llm_response = generate_response(llm_client, contexts, query, config)

        # Return both the response and the contexts used
        return {"response": llm_response, "context": contexts}

    except Exception as e:
        logger.error(f"Failed to process request: {e}")
        return (
            "An error occurred while processing your request. Please try again later."
        )
