from typing import Generator

from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "mysql+pymysql://root:1234@localhost/attendance_db"

engine = create_engine(
    DATABASE_URL,
    echo=True,              # 개발용 SQL 로그 출력
    pool_pre_ping=True,     # 끊긴 커넥션 자동 체크
    pool_recycle=300        # MySQL 연결 유지 안정화
)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)