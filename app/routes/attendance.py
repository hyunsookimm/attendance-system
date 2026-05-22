from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.services.attendance_service import AttendanceService
from app.schemas.attendance_response import AttendanceRecordResponse

router = APIRouter(prefix="/attendance", tags=["직원"])


# DB 세션
def get_service(session: Session = Depends(get_session)):
    return AttendanceService(session)


# 출근
@router.post("/check-in", summary="출근", response_model=AttendanceRecordResponse)
def check_in(employee_id: int, service: AttendanceService = Depends(get_service)):
    return service.check_in(employee_id)


# 퇴근
@router.post("/check-out", summary="퇴근", response_model=AttendanceRecordResponse)
def check_out(employee_id: int, service: AttendanceService = Depends(get_service)):
    return service.check_out(employee_id)


# 외출
@router.post("/outing", summary="외출", response_model=AttendanceRecordResponse)
def outing(employee_id: int, service: AttendanceService = Depends(get_service)):
    return service.outing(employee_id)


# 복귀
@router.post("/return", summary="외출 / 점심 후 복귀", response_model=AttendanceRecordResponse)
def return_to_work(employee_id: int, service: AttendanceService = Depends(get_service)):
    return service.return_to_work(employee_id)


# 점심
@router.post("/lunch", summary="점심", response_model=AttendanceRecordResponse)
def lunch(employee_id: int, service: AttendanceService = Depends(get_service)):
    return service.lunch(employee_id)


# 조퇴
@router.post("/early-leave", summary="조퇴", response_model=AttendanceRecordResponse)
def early_leave(employee_id: int, service: AttendanceService = Depends(get_service)):
    return service.early_leave(employee_id)
