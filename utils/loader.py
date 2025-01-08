import logging

from opensearchpy import OpenSearch
from database import SessionLocal
from models import Post

from embedder import Embedder
from elastic import create_index, update_search

logger = logging.getLogger(__name__)


def load_and_process_text_documents(db, posts: list[Post], embedder: Embedder, os_client: OpenSearch) -> None:
    """
    Loads and processes text documents from a file, chunking and vectorizing the content.
    """

    try:
        create_index(index_name="posts", os_client=os_client)
        update_search(posts=posts, os_client=os_client)

        logger.info("Successfully created opensearch index and stored data")

        for post in posts:
            post.vector = embedder.encode([post.text_content], doc_type="document")[0].tolist()
            doc = Post(**post.model_dump())
            db.add(doc)
            db.commit()
        logger.info("Processed and stored '%s' posts in vector DB", len(posts))
    except Exception as e:
        logger.error("Error processing text documents: '%s'", e)
        raise


def load_data(posts: list[Post], embedder: Embedder, os_client: OpenSearch, config: dict) -> None:
    """
    Loads and processes data into the database by vectorizing text.
    Only loads data into a table if the table is empty.
    """
    db = SessionLocal()
    try:
        # Check if there is any data in the Post table
        if db.query(Post).first() is not None:
            logger.info(
                "Data already exists in the Post table. Skipping data loading for this table."
            )
        else:
            logger.info(
                "No existing data found in Post data. Proceeding with data loading and processing for this table."
            )
            load_and_process_text_documents(db, posts, embedder, os_client)

        logger.info("Data loading process completed successfully.")
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        db.rollback()
        raise
    finally:
        db.close()
