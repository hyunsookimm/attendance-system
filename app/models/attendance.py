from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid6

from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy import Uuid as SAUuid
from sqlmodel import SQLModel, Field

from app.enums.status import AttendanceStatus
from app.enums.action_type import ActionType


def _now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AttendanceRecord(SQLModel, table=True):
    __tablename__ = "attendance_records"
    __table_args__ = (
        Index("ix_attendance_employee_recorded", "employee_id", "recorded_at"),
    )

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
        default_factory=_now_utc,
        nullable=False
    )


class AttendanceLog(SQLModel, table=True):
    __tablename__ = "attendance_logs"

    id: Optional[int] = Field(default=None, primary_key=True)

    attendance_id: UUID = Field(
        sa_column=Column(SAUuid, ForeignKey("attendance_records.id", ondelete="CASCADE"), nullable=False)
    )

    before_action_type: ActionType
    after_action_type: ActionType

    before_status: AttendanceStatus
    after_status: AttendanceStatus

    before_recorded_at: Optional[datetime] = Field(default=None)
    after_recorded_at: Optional[datetime] = Field(default=None)

    modified_at: datetime = Field(default_factory=_now_utc)
