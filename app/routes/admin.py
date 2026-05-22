from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.services.attendance_service import AttendanceService
from app.schemas.attendance_response import AttendanceRecordResponse
from app.schemas.attendance_update import AttendanceUpdateRequest

router = APIRouter(prefix="/admin/attendance", tags=["관리자"])


# DB 세션
def get_service(session: Session = Depends(get_session)):
    return AttendanceService(session)


# 오늘 최근 기록 조회
@router.get("/today", summary="직원의 오늘 최근 출퇴근 기록 조회", response_model=AttendanceRecordResponse)
def get_today(employee_id: int, service: AttendanceService = Depends(get_service)):
    record = service.get_latest_record(employee_id)
    if not record:
        raise HTTPException(status_code=404, detail="오늘 출퇴근 기록 없음")
    return record


# 출입 기록 수정
@router.patch("/{employee_id}", summary="직원의 최근 출퇴근 기록 수정", response_model=AttendanceRecordResponse)
def update_attendance(
    employee_id: int,
    request: AttendanceUpdateRequest,
    service: AttendanceService = Depends(get_service),
):
    # 수정된 출퇴근 기록
    return service.update_attendance(
        employee_id,
        request.action_type
    )
