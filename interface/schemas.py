from typing import Any
from pydantic import BaseModel
from datetime import datetime


class Post(BaseModel):
    uid: int
    title: str
    text_content: str
    tags: list[str]
    n_visits: int
    author: str
    dt: datetime
    vector: Any | None = None


class EmbedderSettings(BaseModel):
    batch_size: int = 16
    model_name: str
    model_type: str
    dimension: int
    prefix_query: str
    prefix_document: str


class QuestionCreate(BaseModel):
    question: str


class Context(BaseModel):
    uid: int
    text: str
    title: str
    tags: list[str]
    n_visits: int
    dt: datetime
    href: str
    source: str


class QuestionResponse(BaseModel):
    response: str
    contexts: list[Context] | str
