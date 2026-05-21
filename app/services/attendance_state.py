from app.enums.status import AttendanceStatus
from app.enums.action_type import ActionType


# 예외 정의
class InvalidTransitionException(Exception):
    pass

# 상태 전이 규칙 테이블
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


# 핵심 함수: 상태 전이 계산
def get_next_status(
    current_status: AttendanceStatus | None,
    action_type: ActionType
) -> AttendanceStatus:

    # 현재 상태에서 가능한 행동 목록 가져오기
    allowed_actions = STATE_TRANSITION.get(current_status)

    # 상태가 정의되지 않은 경우
    if allowed_actions is None:
        raise InvalidTransitionException(
            f"[INVALID STATE] {current_status} 알 수 없는 상태입니다"
        )

    # 행동이 허용되지 않는 경우
    if action_type not in allowed_actions:
        raise InvalidTransitionException(
            f"[INVALID TRANSITION] {current_status} → {action_type} 불가능"
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