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
