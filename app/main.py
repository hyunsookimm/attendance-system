import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.logging_config import setup_logging
from app.routes.attendance import router as attendance_router
from app.routes.admin import router as admin_router

setup_logging(settings.env)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("서버 시작 (env=%s)", settings.env)
    yield
    logger.info("서버 종료")


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(attendance_router)
app.include_router(admin_router)


@app.get("/health", tags=["시스템"], summary="서버 상태 확인")
async def health() -> dict[str, str]:
    return {"status": "ok"}
