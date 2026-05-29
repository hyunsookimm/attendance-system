from datetime import datetime
from typing import Optional
from uuid import UUID, uuid6

from sqlmodel import SQLModel, Field

from app.enums.status import AttendanceStatus
from app.enums.action_type import ActionType
from app.timezone import KST


def _now_kst() -> datetime:
    return datetime.now(KST).replace(tzinfo=None)


class AttendanceRecord(SQLModel, table=True):
    __tablename__ = "attendance_records"

    id: Optional[UUID] = Field(
        default_factory=uuid6,
        primary_key=True
    )

    employee_id: int = Field(
        foreign_key="employees.id",
        nullable=False
    )

    action_type: ActionType = Field(nullable=False)

    status: AttendanceStatus = Field(nullable=False)

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

    before_recorded_at: Optional[datetime] = Field(default=None)

    after_recorded_at: Optional[datetime] = Field(default=None)

    modified_at: datetime = Field(default_factory=_now_kst)
