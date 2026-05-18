from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

from app.enums.status import AttendanceStatus


class AttendanceRecord(SQLModel, table=True):
    __tablename__ = "attendance_records"

    id: Optional[int] = Field(default=None, primary_key=True)

    employee_id: int

    action_type: str

    status: AttendanceStatus

    recorded_at: datetime = Field(default_factory=datetime.now)