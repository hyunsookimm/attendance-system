from typing import List

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.services.attendance_service import AttendanceService
from app.schemas.attendance_response import AttendanceRecordResponse
from app.schemas.attendance_update import AttendanceUpdateRequest
from app.schemas.attendance_create import AttendanceCreateRequest
from app.schemas.work_hours_response import WorkHoursResponse

router = APIRouter(prefix="/admin/attendance", tags=["관리자"])


async def get_service(session: AsyncSession = Depends(get_session)) -> AttendanceService:
    return AttendanceService(session)


@router.get("/today/all", summary="오늘 전체 출퇴근 기록 조회", response_model=List[AttendanceRecordResponse])
async def get_today_all(employee_id: int, service: AttendanceService = Depends(get_service)):
    return await service.get_today_records(employee_id)


@router.get("/work-hours", summary="오늘 근무시간 조회", response_model=WorkHoursResponse)
async def get_work_hours(employee_id: int, service: AttendanceService = Depends(get_service)):
    total_minutes, is_currently_in, records = await service.calculate_work_hours(employee_id)
    return WorkHoursResponse(
        employee_id=employee_id,
        total_minutes=total_minutes,
        is_currently_in=is_currently_in,
        records=records,  # type: ignore[arg-type]
    )


@router.post("", summary="출퇴근 기록 수동 추가", response_model=AttendanceRecordResponse)
async def add_record(request: AttendanceCreateRequest, service: AttendanceService = Depends(get_service)):
    return await service.add_record(request.employee_id, request.action_type, request.recorded_at)


@router.patch("/{employee_id}", summary="최근 출퇴근 기록 수정", response_model=AttendanceRecordResponse)
async def update_record(
    employee_id: int,
    request: AttendanceUpdateRequest,
    service: AttendanceService = Depends(get_service),
):
    return await service.update_record(employee_id, request.action_type, request.recorded_at)


@router.delete("/{employee_id}", summary="최근 출퇴근 기록 삭제", status_code=204)
async def delete_record(employee_id: int, service: AttendanceService = Depends(get_service)):
    await service.delete_record(employee_id)
