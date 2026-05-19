from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance"])

# DB 세션
def get_service(session: Session = Depends(get_session)):
    return AttendanceService(session)

#출근
@router.post("/check-in")
def check_in(
    employee_id: int,
    service: AttendanceService = Depends(get_service)
):
    return service.check_in(employee_id)

#외출
@router.post("/outing")
def check_out(
    employee_id: int,
    service: AttendanceService = Depends(get_service)
):
    return service.outing(employee_id)

#복귀
@router.post("/return")
def return_to_work(
    employee_id: int,
    service: AttendanceService = Depends(get_service)
):
    return service.return_to_work(employee_id)

#점심
@router.post("/lunch")
def lunch(
    employee_id: int,
    service: AttendanceService = Depends(get_service)
):
    return service.lunch(employee_id)

#조퇴
@router.post("/early-leave")
def early_leave(
    employee_id: int,
    service: AttendanceService = Depends(get_service)
):
    return service.early_leave(employee_id)

#퇴근
@router.post("/check-out")
def check_out(
    employee_id: int,
    service: AttendanceService = Depends(get_service)
):
    return service.check_out(employee_id)

#오늘 기록 조회
@router.get("/today")
def get_today(
    employee_id: int,
    service: AttendanceService = Depends(get_service)
):
    return service.get_today_records(employee_id)
