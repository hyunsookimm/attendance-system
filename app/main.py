from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import create_db_and_tables
import app.models  # 👈 이게 핵심 (모델 자동 등록)

from app.routes.attendance import router as attendance_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 실행
    create_db_and_tables()
    print("DB 준비 완료")

    yield


app = FastAPI(
    title="Attendance System",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(attendance_router)


@app.get("/")
def root():
    return {"message": "출입 관리 시스템"}