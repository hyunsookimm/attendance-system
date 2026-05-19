from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

from app.enums.status import AttendanceStatus
from app.enums.action_type import ActionType


class AttendanceRecord(SQLModel, table=True):
    __tablename__ = "attendance_records"

    id: Optional[int] = Field(
        default=None,
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
        default_factory=datetime.now,
        nullable=False
    )