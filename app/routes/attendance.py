from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.employee import Employee
from app.services.attendance_service import AttendanceService
from app.schemas.attendance_response import AttendanceRecordResponse

router = APIRouter(prefix="/attendance", tags=["직원"])


async def get_service(session: AsyncSession = Depends(get_session)) -> AttendanceService:
    return AttendanceService(session)


@router.post("/tap", summary="카드 태깅 (입장/퇴장 자동 판별)", response_model=AttendanceRecordResponse)
async def tap(
    employee_id: int | None = None,
    name: str | None = None,
    service: AttendanceService = Depends(get_service),
):
    if employee_id is None and name is None:
        raise HTTPException(status_code=400, detail="employee_id 또는 name 중 하나를 입력해주세요")

    if name is not None:
        stmt = select(Employee).where(Employee.name == name)
        if employee_id is not None:
            stmt = stmt.where(Employee.id == employee_id)
        result = await service.session.exec(stmt)
        employees = result.all()
        if not employees:
            raise HTTPException(status_code=404, detail="등록되지 않은 직원입니다")
        if len(employees) > 1:
            raise HTTPException(
                status_code=400,
                detail=f"동일한 이름의 직원이 {len(employees)}명입니다. employee_id도 함께 입력해주세요",
            )
        employee_id = employees[0].id

    return await service.tap(employee_id)  # type: ignore[arg-type]
