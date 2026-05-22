from datetime import datetime
from typing import Optional
from uuid import UUID, uuid6
from zoneinfo import ZoneInfo

from sqlmodel import SQLModel, Field

from app.enums.status import AttendanceStatus
from app.enums.action_type import ActionType

_KST = ZoneInfo("Asia/Seoul")


def _now_kst() -> datetime:
    return datetime.now(_KST).replace(tzinfo=None)


class AttendanceRecord(SQLModel, table=True):
    __tablename__ = "attendance_records"

    id: Optional[UUID] = Field(
        default_factory=uuid6,
        primary_key=True
    )

    # 직원 FK
    employee_id: int = Field(
        foreign_key="employees.id",
        nullable=False
    )

    # 행동 종류
    action_type: ActionType = Field(
        nullable=False
    )

    # 현재 상태
    status: AttendanceStatus = Field(
        nullable=False
    )

    # 기록 시간
    recorded_at: datetime = Field(
        default_factory=_now_kst,
        nullable=False
    )


class AttendanceLog(SQLModel, table=True):
    __tablename__ = "attendance_logs"

    id: Optional[int] = Field(default=None, primary_key=True)

    attendance_id: UUID

    before_status: AttendanceStatus

    after_status: AttendanceStatus

    modified_at: datetime = Field(default_factory=_now_kst)