from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import create_db_and_tables
import app.models  # 모델을 SQLModel에 등록하기 위한 의도적 import

from app.routes.attendance import router as attendance_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    
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