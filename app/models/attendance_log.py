from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

from app.enums.status import AttendanceStatus


class AttendanceLog(SQLModel, table=True):
    __tablename__ = "attendance_logs"

    id: Optional[int] = Field(default=None, primary_key=True)

    attendance_id: int

    before_status: AttendanceStatus

    after_status: AttendanceStatus

    modified_at: datetime = Field(default_factory=datetime.now)