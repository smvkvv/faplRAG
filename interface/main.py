import logging
from contextlib import asynccontextmanager

import yaml
from opensearchpy import OpenSearch
from fastapi import FastAPI

from interface.schemas import QuestionResponse, QuestionCreate
from interface.llm_client import initialize_llm_client
from interface.retrieval import initialize_embedding_model
from interface.process import process_request
from interface import models_interface

from utils.database import engine


# Load configuration
config_path = "interface/config.yml"
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# Initialize logger
logging.basicConfig(level=logging.getLevelName(config["logging"]["level"]))
logger = logging.getLogger(config["project"]["name"])
os_logger = logging.getLogger('opensearch')
os_logger.setLevel(logging.WARNING)

# Initialize the database
models_interface.Base.metadata.create_all(bind=engine)

# Initialize models and LLM client
local_embedder = initialize_embedding_model(config)
llm_client = initialize_llm_client()

os_client = OpenSearch([{"host": config["os_params"]["host"], "port": config["os_params"]["port"]}])

unexpected_format_response = "An error occurred while processing the request due to unexpected response format."
unexpected_format_context = "No valid context available due to unexpected response format."

server_error_response = "An internal server error occurred. Please try again later."
server_error_context = "No context available due to server error."


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    logger.info("App shutting down")


app = FastAPI(title=config["project"]["name"], lifespan=lifespan)


@app.post("/ask/", response_model=QuestionResponse)
def ask_question(question: QuestionCreate):
    logger.info(f"Received question: {question.question}")

    try:
        response_content = process_request(config, local_embedder, llm_client, question.question, os_client)
        logger.info(f"LLM Response: {response_content}")

        if isinstance(response_content, dict) and 'response' in response_content and 'context' in response_content:
            return QuestionResponse(
                response=response_content['response'],
                contexts=response_content['context'],
            )
        else:
            logger.error(f"Unexpected response format: {response_content}")
            return QuestionResponse(
                response=unexpected_format_response,
                contexts=unexpected_format_context,
                code=400
            )

    except Exception as e:
        logger.exception(f"An error occurred while processing the question: {str(e)}")
        return QuestionResponse(
            response=server_error_response,
            contexts=server_error_context,
            code=500
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app,
                host=config["server"]["host"],
                port=config["server"]["port"],
                reload=True,
                )
