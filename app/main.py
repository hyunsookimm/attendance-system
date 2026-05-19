from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import create_db_and_tables
from app.routes.attendance import router as attendance_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 실행
    create_db_and_tables()
    print("DB 초기화 완료")

    yield

app = FastAPI(
    title="Attendance System",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(attendance_router)


@app.get("/")
def root():
    return {"message": "Attendance system is running"}