from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector
from datetime import datetime, timezone

from config import Config

engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String(500), nullable=False)
    title = Column(String(500))
    upload_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    page_count = Column(Integer)
    status = Column(String(50), default="processing")  # processing, indexed, failed


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer)
    embedding = Column(Vector(Config.EMBEDDING_DIMENSION))


class GoldenQA(Base):
    """Golden set for evaluation — expected question/answer pairs."""
    __tablename__ = "golden_qa"

    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    expected_answer = Column(Text, nullable=False)
    source_document = Column(String(500))
    source_page = Column(Integer)


def init_db():
    """Create tables and enable pgvector extension."""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(engine)
