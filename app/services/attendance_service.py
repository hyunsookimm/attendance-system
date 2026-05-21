from datetime import date, datetime, time

from fastapi import HTTPException
from sqlalchemy.orm import attributes
from sqlmodel import Session, select

from app.models.attendance import AttendanceRecord
from app.models.attendance_log import AttendanceLog

from app.enums.status import AttendanceStatus
from app.enums.action_type import ActionType

from app.services.attendance_state import get_next_status, is_valid_transition, InvalidTransitionException


class AttendanceService:

    def __init__(self, session: Session):
        self.session = session

    # 오늘 기록 조회
    def get_today_records(self, employee_id: int):

        today = date.today()

        statement = (
            select(AttendanceRecord)
            .where(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.recorded_at >= datetime.combine(today, time.min),
                AttendanceRecord.recorded_at <= datetime.combine(today, time.max),
            )
            .order_by(AttendanceRecord.recorded_at)
        )

        return self.session.exec(statement).all()

    # 최근 기록
    def get_latest_record(self, employee_id: int):

        records = self.get_today_records(employee_id)
        return records[-1] if records else None

    # 공통 생성 로직
    def create_record(
        self,
        employee_id: int,
        action_type: ActionType,
        status: AttendanceStatus
    ):

        record = AttendanceRecord(
            employee_id=employee_id,
            action_type=action_type,
            status=status,
            recorded_at=datetime.now()
        )

        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)

        return record

    # 출근
    def check_in(self, employee_id: int):

        latest = self.get_latest_record(employee_id)

        if latest:
            raise HTTPException(status_code=400, detail="이미 출근 처리됨")

        return self.create_record(
            employee_id,
            ActionType.CHECK_IN,
            AttendanceStatus.WORKING
        )

    # 외출
    def outing(self, employee_id: int):

        latest = self.get_latest_record(employee_id)

        if not latest:
            raise HTTPException(status_code=404, detail="출근 기록 없음")

        if not is_valid_transition(latest.status, ActionType.OUTING):
            raise HTTPException(status_code=400, detail="외출 불가능")

        return self.create_record(
            employee_id,
            ActionType.OUTING,
            AttendanceStatus.OUTING
        )

    # 복귀
    def return_to_work(self, employee_id: int):

        latest = self.get_latest_record(employee_id)

        if not latest:
            raise HTTPException(status_code=404, detail="출근 기록 없음")

        if not is_valid_transition(latest.status, ActionType.RETURN):
            raise HTTPException(status_code=400, detail="복귀 불가능")

        return self.create_record(
            employee_id,
            ActionType.RETURN,
            AttendanceStatus.WORKING
        )

    # 점심
    def lunch(self, employee_id: int):

        latest = self.get_latest_record(employee_id)

        if not latest:
            raise HTTPException(status_code=404, detail="출근 기록 없음")

        if not is_valid_transition(latest.status, ActionType.LUNCH):
            raise HTTPException(status_code=400, detail="점심 불가능")

        return self.create_record(
            employee_id,
            ActionType.LUNCH,
            AttendanceStatus.LUNCH
        )

    # 조퇴
    def early_leave(self, employee_id: int):

        latest = self.get_latest_record(employee_id)

        if not latest:
            raise HTTPException(status_code=404, detail="출근 기록 없음")

        if not is_valid_transition(latest.status, ActionType.EARLY_LEAVE):
            raise HTTPException(status_code=400, detail="조퇴 불가능")

        return self.create_record(
            employee_id,
            ActionType.EARLY_LEAVE,
            AttendanceStatus.EARLY_LEAVE
        )

    # 퇴근
    def check_out(self, employee_id: int):

        latest = self.get_latest_record(employee_id)

        if not latest:
            raise HTTPException(status_code=404, detail="출근 기록 없음")

        if not is_valid_transition(latest.status, ActionType.CHECK_OUT):
            raise HTTPException(status_code=400, detail="퇴근 불가능")

        return self.create_record(
            employee_id,
            ActionType.CHECK_OUT,
            AttendanceStatus.OFF_WORK
        )

    # 수정
    def update_attendance(
        self,
        employee_id: int,
        new_action_type: ActionType
    ):

        attendance = self.get_latest_record(employee_id)

        if not attendance:
            raise HTTPException(status_code=404, detail="출근 기록 없음")

        # 상태 계산
        try:
            new_status = get_next_status(attendance.status, new_action_type)
        except InvalidTransitionException as e:
            raise HTTPException(status_code=400, detail=str(e))

        before_status = attendance.status

        # 둘 다 업데이트
        attendance.status = new_status
        attendance.action_type = new_action_type
        attributes.flag_modified(attendance, "status")
        attributes.flag_modified(attendance, "action_type")

        # 로그 저장
        log = AttendanceLog(
            attendance_id=attendance.id,
            before_status=before_status,
            after_status=new_status,
        )

        self.session.add(attendance)
        self.session.add(log)

        self.session.commit()
        self.session.refresh(attendance)

        return attendance