import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from app.routes.attendance import router as attendance_router
from app.routes.admin import router as admin_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Attendance System",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "직원",
            "description": "직원이 직접 사용하는 출퇴근 기록 API입니다.",
        },
        {
            "name": "관리자",
            "description": "관리자가 직원의 출퇴근 기록을 조회하고 수정하는 API입니다.",
        },
    ]
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(attendance_router)
app.include_router(admin_router)
