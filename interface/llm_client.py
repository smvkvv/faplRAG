import os
import logging
from dotenv import load_dotenv

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from interface.schemas import Context


logger = logging.getLogger(__name__)


def initialize_llm_client() -> GigaChat:
    """
    Initializes and returns the LLM client using provided configuration.
    """
    try:
        load_dotenv('.env')
        llm_client = GigaChat(credentials=os.environ.get("LLM_API_KEY"), verify_ssl_certs=False)
        logger.info("LLM client initialized successfully.")
        return llm_client
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}")
        raise


def build_prompt(contexts: list[str], query: str) -> str:
    """
    Constructs the prompt for the LLM based on the given contexts and query.
    """

    prompt = "Отвечай используя контекст:\n"
    for i, context in enumerate(contexts):
        prompt += f"Контекст {i + 1}: {context}\n"
    prompt += f"Вопрос: {query}\nНе упоминай, что ты пользуешься контекстом\nПодробный Ответ: "
    return prompt


def generate_response(llm_client: GigaChat, contexts: list[Context], query: str, config) -> str:
    """
    Generates a response based on retrieved contexts and the input query.
    """
    try:
        contexts = [context.text[:2048] for context in contexts] # TODO add chunker

        prompt = build_prompt(contexts, query)
        response = llm_client.stream(
            Chat(
                messages=[
                    Messages(role=MessagesRole.SYSTEM, content=config["llm"]["system_prompt"]),
                    Messages(role=MessagesRole.USER, content=prompt),
                ],
                temperature=config["llm"]["temperature"],
                top_p=config["llm"]["top_p"],
                max_tokens=config["llm"]["max_tokens"],
            )
        )

        generated_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                generated_response += chunk.choices[0].delta.content

        logger.info(f"Generated response: {generated_response[:30]}...")
        return generated_response
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise


def rewrite_query(llm_client: GigaChat, query: str, config: dict) -> str:
    """
    Answers user's query using LLM_rewriter
    """
    try:
        response = llm_client.stream(
            Chat(
                messages=[
                    Messages(role=MessagesRole.SYSTEM, content=config["llm_rewriter"]["system_prompt"]),
                    Messages(role=MessagesRole.USER, content=f"Вопрос: {query}"),
                ],
                temperature=config["llm_rewriter"]["temperature"],
                top_p=config["llm_rewriter"]["top_p"],
                max_tokens=config["llm_rewriter"]["max_tokens"],
            )
        )

        rewrited_query = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                rewrited_query += chunk.choices[0].delta.content

        rewrited_query += f'\n------------------\n{query}'
        logger.info(f"Rewrited query: {rewrited_query}")
        return rewrited_query
    except Exception as e:
        logger.error(f"Error rewriting query: {e}")
        raise
