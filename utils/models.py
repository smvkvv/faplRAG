from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Date, Integer, String, Text, ARRAY

from database import Base
from config import EMBEDDING_DIMENSION


class Post(Base):
    __tablename__ = "posts"

    uid = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    dt = Column(Date, nullable=False)
    text_content = Column(Text)
    tags = Column(ARRAY(String, as_tuple=True))
    n_visits = Column(Integer)
    vector = Column(Vector(EMBEDDING_DIMENSION))
    author = Column(String)
