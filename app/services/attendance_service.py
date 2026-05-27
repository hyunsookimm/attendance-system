from datetime import datetime, time
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy.orm import attributes
from sqlmodel import Session, select

from app.models.attendance import AttendanceRecord, AttendanceLog
from app.models.employee import Employee

from app.enums.status import AttendanceStatus
from app.enums.action_type import ActionType

KST = ZoneInfo("Asia/Seoul")


# 예외 정의
class InvalidTransitionException(Exception):
    pass


# 상태 규칙 테이블
STATE_TRANSITION: dict = {
    # 아직 출근 전
    None: {
        ActionType.CHECK_IN: AttendanceStatus.WORKING,
    },

    # 근무 중
    AttendanceStatus.WORKING: {
        ActionType.OUTING: AttendanceStatus.OUTING,
        ActionType.LUNCH: AttendanceStatus.LUNCH,
        ActionType.EARLY_LEAVE: AttendanceStatus.EARLY_LEAVE,
        ActionType.CHECK_OUT: AttendanceStatus.OFF_WORK,
    },

    # 외출 상태
    AttendanceStatus.OUTING: {
        ActionType.RETURN: AttendanceStatus.WORKING,
    },

    # 점심 상태
    AttendanceStatus.LUNCH: {
        ActionType.RETURN: AttendanceStatus.WORKING,
    },

    # 조퇴 상태
    AttendanceStatus.EARLY_LEAVE: {
        ActionType.CHECK_OUT: AttendanceStatus.OFF_WORK,
    },

    # 퇴근 상태
    AttendanceStatus.OFF_WORK: {
        # 아무 행동도 허용하지 않음
    },
}


# 상태 계산
def get_next_status(
    current_status: AttendanceStatus | None,
    action_type: ActionType
) -> AttendanceStatus:

    allowed_actions = STATE_TRANSITION.get(current_status)

    if allowed_actions is None:
        raise InvalidTransitionException(
            f"알 수 없는 상태입니다: {current_status}"
        )

    if action_type not in allowed_actions:
        current_label = current_status.label if current_status else "출근 전"
        allowed_labels = ", ".join(a.label for a in allowed_actions)
        raise InvalidTransitionException(
            f"현재 상태 [{current_label}]에서 [{action_type.label}]은(는) 불가능합니다. "
            f"가능한 행동: {allowed_labels}"
        )

    return allowed_actions[action_type]


# 유효성 체크
def is_valid_transition(
    current_status: AttendanceStatus | None,
    action_type: ActionType
) -> bool:

    allowed_actions = STATE_TRANSITION.get(current_status)

    if allowed_actions is None:
        return False

    return action_type in allowed_actions


class AttendanceService:

    def __init__(self, session: Session):
        self.session = session

    # KST 날짜 범위
    def _get_today_range(self) -> tuple[datetime, datetime]:
        today = datetime.now(KST).date()
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)
        return start, end

    # 오늘 기록 조회
    def get_today_records(self, employee_id: int):

        start, end = self._get_today_range()

        statement = (
            select(AttendanceRecord)
            .where(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.recorded_at >= start,
                AttendanceRecord.recorded_at <= end,
            )
            .order_by(AttendanceRecord.recorded_at)
        )

        return self.session.exec(statement).all()

    # 최근 기록 1건 조회
    def get_latest_record(self, employee_id: int):

        start, end = self._get_today_range()

        statement = (
            select(AttendanceRecord)
            .where(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.recorded_at >= start,
                AttendanceRecord.recorded_at <= end,
            )
            .order_by(AttendanceRecord.recorded_at.desc())
            .limit(1)
        )

        return self.session.exec(statement).first()

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
            recorded_at=datetime.now(KST).replace(tzinfo=None)
        )

        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)

        return record

    # 출근
    def check_in(self, employee_id: int):

        # 직원이 없으면 자동 생성
        employee = self.session.get(Employee, employee_id)
        if not employee:
            employee = Employee(
                id=employee_id,
                name=f"직원_{employee_id}",
                department="미지정",
                employee_number=str(employee_id),
            )
            self.session.add(employee)
            self.session.commit()

        latest = self.get_latest_record(employee_id)

        if latest:
            raise HTTPException(status_code=400, detail="이미 출근 처리됨")

        return self.create_record(
            employee_id,
            ActionType.CHECK_IN,
            AttendanceStatus.WORKING
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


    # 수정
    def update_attendance(
        self,
        employee_id: int,
        new_action_type: ActionType
    ):

        latest = self.get_latest_record(employee_id)

        if not latest:
            raise HTTPException(status_code=404, detail="출근 기록 없음")

        try:
            new_status = get_next_status(latest.status, new_action_type)
        except InvalidTransitionException as e:
            raise HTTPException(status_code=400, detail=str(e))

        before_status = latest.status

        # 둘 다 업데이트
        latest.status = new_status
        latest.action_type = new_action_type
        attributes.flag_modified(latest, "status")
        attributes.flag_modified(latest, "action_type")

        # 로그 저장
        log = AttendanceLog(
            attendance_id=latest.id,
            before_status=before_status,
            after_status=new_status,
        )

        self.session.add(latest)
        self.session.add(log)

        self.session.commit()
        self.session.refresh(latest)

        return latest