from typing import Generator

from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "mysql+pymysql://root:1234@localhost/attendance_db"

engine = create_engine(
    DATABASE_URL,
    echo=True,              
    pool_pre_ping=True,     
    pool_recycle=300 
)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)