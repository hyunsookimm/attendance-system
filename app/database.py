import os
from typing import Generator

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ENV = os.getenv("ENV", "production")

engine = create_engine(
    DATABASE_URL,
    echo=(ENV == "development"),
    pool_pre_ping=True,
    pool_recycle=300
)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)