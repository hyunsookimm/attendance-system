import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.logging_config import setup_logging
from app.routes.attendance import router as attendance_router
from app.routes.admin import router as admin_router
from app.routes.employees import router as employees_router

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
    swagger_ui_parameters={"sortPropsAlphabetically": False},
    openapi_tags=[
        {
            "name": "직원",
            "description": "직원이 직접 사용하는 출퇴근 기록 API입니다.",
        },
        {
            "name": "관리자 - 직원관리",
            "description": "관리자가 직원을 등록, 조회, 수정, 삭제하는 API입니다.",
        },
        {
            "name": "관리자 - 근태관리",
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
app.include_router(employees_router)
app.include_router(admin_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    field_order = ["name", "department", "employee_number"]
    for schema_name in ["EmployeeCreateRequest", "EmployeeUpdateRequest"]:
        s = schema.get("components", {}).get("schemas", {}).get(schema_name)
        if s and "properties" in s:
            s["properties"] = {k: s["properties"][k] for k in field_order if k in s["properties"]}
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi  # type: ignore[method-assign]

