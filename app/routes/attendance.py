from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.services.attendance_service import AttendanceService
from app.services.employee_service import EmployeeService
from app.schemas.attendance_response import AttendanceRecordResponse

router = APIRouter(prefix="/attendance", tags=["직원"])


async def get_service(session: AsyncSession = Depends(get_session)) -> AttendanceService:
    return AttendanceService(session)


async def get_employee_service(session: AsyncSession = Depends(get_session)) -> EmployeeService:
    return EmployeeService(session)


@router.post("/tap", summary="카드 태깅 (입장/퇴장 자동 판별)", response_model=AttendanceRecordResponse)
async def tap(
    employee_id: int | None = None,
    name: str | None = None,
    service: AttendanceService = Depends(get_service),
    emp_service: EmployeeService = Depends(get_employee_service),
):
    employee = await emp_service.resolve_employee(employee_id, name)
    return await service.tap(employee.id)
