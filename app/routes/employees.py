from typing import List

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.schemas.employee import EmployeeCreateRequest, EmployeeUpdateRequest, EmployeeResponse
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/admin/employees", tags=["관리자 - 직원관리"])


async def get_service(session: AsyncSession = Depends(get_session)) -> EmployeeService:
    return EmployeeService(session)


@router.get("", summary="전체 직원 목록 조회", response_model=List[EmployeeResponse])
async def get_all(service: EmployeeService = Depends(get_service)):
    return await service.get_all()


@router.get("/one", summary="직원 단건 조회", response_model=EmployeeResponse)
async def get_one(
    employee_id: int | None = None,
    name: str | None = None,
    service: EmployeeService = Depends(get_service),
):
    return await service.resolve_employee(employee_id, name)


@router.post("", summary="직원 등록", response_model=EmployeeResponse, status_code=201)

async def create(request: EmployeeCreateRequest, service: EmployeeService = Depends(get_service)):
    return await service.create(request.name, request.department, request.employee_number)  # type: ignore[arg-type]


@router.patch("/one", summary="직원 정보 수정", response_model=EmployeeResponse)
async def update(
    request: EmployeeUpdateRequest,
    employee_id: int | None = None,
    name: str | None = None,
    service: EmployeeService = Depends(get_service),
):
    employee = await service.resolve_employee(employee_id, name)
    return await service.update(employee.id, request.name, request.department, request.employee_number)


@router.delete("/one", summary="직원 삭제", status_code=204)
async def delete(
    employee_id: int | None = None,
    name: str | None = None,
    service: EmployeeService = Depends(get_service),
):
    employee = await service.resolve_employee(employee_id, name)
    await service.delete(employee.id)
