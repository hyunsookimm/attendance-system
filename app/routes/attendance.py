from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import attendance_service

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("/check-in/{employee_id}")
def check_in(employee_id: int, db: Session = Depends(get_db)):
    log = attendance_service.record_check_in(db, employee_id)
    return {"message": "출근 처리 완료", "timestamp": log.timestamp}


@router.post("/check-out/{employee_id}")
def check_out(employee_id: int, db: Session = Depends(get_db)):
    log = attendance_service.record_check_out(db, employee_id)
    return {"message": "퇴근 처리 완료", "timestamp": log.timestamp}
