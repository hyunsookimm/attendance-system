from datetime import date, datetime
from sqlalchemy.orm import Session
from app.models.attendance import Attendance
from app.models.attendance_log import AttendanceLog
from app.enums.status import AttendanceStatus


def get_or_create_attendance(db: Session, employee_id: int, target_date: date) -> Attendance:
    attendance = (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee_id, Attendance.date == target_date)
        .first()
    )
    if not attendance:
        attendance = Attendance(employee_id=employee_id, date=target_date)
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
    return attendance


def record_check_in(db: Session, employee_id: int) -> AttendanceLog:
    today = date.today()
    attendance = get_or_create_attendance(db, employee_id, today)
    log = AttendanceLog(
        attendance_id=attendance.id,
        status=AttendanceStatus.CHECK_IN,
        timestamp=datetime.now(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def record_check_out(db: Session, employee_id: int) -> AttendanceLog:
    today = date.today()
    attendance = get_or_create_attendance(db, employee_id, today)
    log = AttendanceLog(
        attendance_id=attendance.id,
        status=AttendanceStatus.CHECK_OUT,
        timestamp=datetime.now(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
