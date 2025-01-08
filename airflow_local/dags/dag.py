import sys
import logging

from datetime import datetime, timedelta
from airflow.decorators import dag, task

sys.path.insert(0, '/opt/airflow/utils')
sys.path.insert(0, '/opt/airflow/interface')

logger = logging.getLogger(__name__)


@dag(
    description="This DAG is used to parse data from fapl.ru and updating the db.",
    schedule_interval=None,
    tags=['dataloader'],
    start_date=datetime(2025, 1, 1, 1, 1, 1),
    dagrun_timeout=timedelta(hours=6),
    default_args={
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
)
def load_data_to_db():
    @task
    def scrap_data_from_fapl() -> list[dict]:
        # TODO fix pythonpath issues
        from parser import get_posts
        from utils import load_yaml_from_file

        config = load_yaml_from_file('interface/config.yml')
        logger.info("Loaded config")

        result: list[dict] = get_posts(n_months_to_iterate=config['data']['n_months'])

        return result

    @task
    def update_db(posts: list[dict]) -> None:
        # TODO fix pythonpath issues
        from utils import load_yaml_from_file
        from schemas import EmbedderSettings, Post
        from embedder import Embedder

        from loader import load_data
        from models import Base
        from database import engine
        from opensearchpy import OpenSearch

        config = load_yaml_from_file('interface/config.yml')
        logger.info("Loaded config")

        settings = EmbedderSettings(**config['embedding_model'])
        embedder = Embedder(settings)
        logger.info("Initialized embedding model '%s'", settings.model_name)

        os_client = OpenSearch(([{"host": config["os_params"]["host"], "port": config["os_params"]["port"]}]))
        logger.info("Initialized opensearch-py client")

        Base.metadata.create_all(bind=engine)

        posts = [Post(**post) for post in posts]

        load_data(posts=posts, embedder=embedder, os_client=os_client, config=config)


    loaded_posts = scrap_data_from_fapl()
    update_db(loaded_posts)

load_data_to_db()
