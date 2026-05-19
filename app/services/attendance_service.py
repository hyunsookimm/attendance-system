from datetime import date, datetime, time

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.attendance import AttendanceRecord
from app.enums.status import AttendanceStatus
from app.enums.action_type import ActionType


# 상태 변경 규칙
ALLOWED_TRANSITIONS = {

    AttendanceStatus.WORKING: [
        AttendanceStatus.OUTING,
        AttendanceStatus.LUNCH,
        AttendanceStatus.EARLY_LEAVE,
        AttendanceStatus.OFF_WORK,
    ],

    AttendanceStatus.OUTING: [
        AttendanceStatus.WORKING
    ],

    AttendanceStatus.LUNCH: [
        AttendanceStatus.WORKING
    ]
}


class AttendanceService:

    def __init__(self, session: Session):
        self.session = session

    # 오늘 기록 전체 조회
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

    # 가장 최근 기록 조회
    def get_latest_record(self, employee_id: int):

        records = self.get_today_records(employee_id)

        if not records:
            return None

        return records[-1]

    # 출입 기록 
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
        )

        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)

        return record

    # 상태 변경 가능 여부 확인
    def validate_transition(
        self,
        current_status: AttendanceStatus,
        new_status: AttendanceStatus
    ):

        if current_status not in ALLOWED_TRANSITIONS:
            raise HTTPException(
                status_code=400,
                detail="변경 불가능한 상태"
            )

        allowed_status = ALLOWED_TRANSITIONS[current_status]

        if new_status not in allowed_status:
            raise HTTPException(
                status_code=400,
                detail=f"{current_status} → {new_status} 변경 불가"
            )

    # 출근
    def check_in(self, employee_id: int):

        latest_record = self.get_latest_record(employee_id)

        # 이미 오늘 출근했는지 확인
        if latest_record:
            raise HTTPException(
                status_code=400,
                detail="이미 출근 처리됨"
            )

        return self.create_record(
            employee_id=employee_id,
            action_type=ActionType.CHECK_IN,
            status=AttendanceStatus.WORKING
        )

    # 외출
    def outing(self, employee_id: int):

        latest_record = self.get_latest_record(employee_id)

        if not latest_record:
            raise HTTPException(
                status_code=404,
                detail="출근 기록 없음"
            )

        self.validate_transition(
            latest_record.status,
            AttendanceStatus.OUTING
        )

        return self.create_record(
            employee_id=employee_id,
            action_type=ActionType.OUTING,
            status=AttendanceStatus.OUTING
        )

    # 복귀
    def return_to_work(self, employee_id: int):

        latest_record = self.get_latest_record(employee_id)

        if not latest_record:
            raise HTTPException(
                status_code=404,
                detail="출근 기록 없음"
            )

        self.validate_transition(
            latest_record.status,
            AttendanceStatus.WORKING
        )

        return self.create_record(
            employee_id=employee_id,
            action_type=ActionType.RETURN,
            status=AttendanceStatus.WORKING
        )

    # 점심
    def lunch(self, employee_id: int):

        latest_record = self.get_latest_record(employee_id)

        if not latest_record:
            raise HTTPException(
                status_code=404,
                detail="출근 기록 없음"
            )

        self.validate_transition(
            latest_record.status,
            AttendanceStatus.LUNCH
        )

        return self.create_record(
            employee_id=employee_id,
            action_type=ActionType.LUNCH,
            status=AttendanceStatus.LUNCH
        )

    # 조퇴
    def early_leave(self, employee_id: int):

        latest_record = self.get_latest_record(employee_id)

        if not latest_record:
            raise HTTPException(
                status_code=404,
                detail="출근 기록 없음"
            )

        self.validate_transition(
            latest_record.status,
            AttendanceStatus.EARLY_LEAVE
        )

        return self.create_record(
            employee_id=employee_id,
            action_type=ActionType.EARLY_LEAVE,
            status=AttendanceStatus.EARLY_LEAVE
        )

    # 퇴근
    def check_out(self, employee_id: int):

        latest_record = self.get_latest_record(employee_id)

        if not latest_record:
            raise HTTPException(
                status_code=404,
                detail="출근 기록 없음"
            )

        self.validate_transition(
            latest_record.status,
            AttendanceStatus.OFF_WORK
        )

        return self.create_record(
            employee_id=employee_id,
            action_type=ActionType.CHECK_OUT,
            status=AttendanceStatus.OFF_WORK
        )