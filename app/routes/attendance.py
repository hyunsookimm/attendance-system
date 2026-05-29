from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.services.attendance_service import AttendanceService
from app.schemas.attendance_response import AttendanceRecordResponse

router = APIRouter(prefix="/attendance", tags=["직원"])


async def get_service(session: AsyncSession = Depends(get_session)):
    return AttendanceService(session)


@router.post("/tap", summary="카드 태깅 (입장/퇴장 자동 판별)", response_model=AttendanceRecordResponse)
async def tap(employee_id: int, service: AttendanceService = Depends(get_service)):
    return await service.tap(employee_id)
