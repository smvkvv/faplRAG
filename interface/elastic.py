import logging
from typing import Any, Dict, Iterator, List

import more_itertools
from opensearchpy import OpenSearch, OpenSearchException
from opensearchpy.helpers import bulk

from schemas import Post

logger = logging.getLogger(__name__)


def create_index(index_name: str, os_client: OpenSearch) -> None:
    mapping: Dict = {
        "mappings": {
            "properties": {
                "uid": {"type": "integer"},
                "title": {"type": "text"},
                "text_content": {"type": "text"},
                "tags": {"type": "keyword"},
                "n_visits": {"type": "integer"},
                "author": {"type": "text"},
                "dt": {"type": "date"}
            }
        }
    }

    if not os_client.indices.exists(index=index_name):
        os_client.indices.create(index=index_name, body=mapping)
        logger.info(f"Successfully created index {index_name}")


def load(posts: List[Post]) -> Iterator[Any]:
    for post in posts:
        try:
            yield generate_document_source(post)
        except Exception:
            raise


def generate_document_source(post: Post) -> Dict[str, str]:
    return {
                "uid": post.uid,
                "title": post.title,
                "text_content": post.text_content,
                "tags": post.tags,
                "n_visits": post.n_visits,
                "author": post.author,
                "dt": post.dt
            }


def update_search(posts: list[Post], os_client: OpenSearch, batch_size: int = 500) -> None:
    total_inserted_docs: int = 0
    total_errors: int = 0

    for chunk in more_itertools.ichunked(load(posts), batch_size):
        bucket_data = []
        for document in chunk:
            cur = {
                "_index": "chunks",
                "_source": document,
            }
            if 'uid' in document:
                cur['_source']['id'] = document['uid']
            bucket_data.append(cur)
        try:
            inserted, errors = bulk(os_client, bucket_data, max_retries=4, raise_on_error=False)
            errors_num = len(errors) if isinstance(errors, list) else errors  # type: ignore
            logger.debug(f"{inserted} docs successfully inserted by bulk with {errors_num} errors")
            total_inserted_docs += inserted
            total_errors += errors_num
            if isinstance(errors, list):  # type: ignore
                for error in errors:  # type: ignore
                    logger.error(f"Doc was not inserted with error: {error}")
        except OpenSearchException as e:
            logger.exception(f"Error while pushing data to opensearch: {e}")
            raise
