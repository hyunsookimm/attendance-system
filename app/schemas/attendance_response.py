from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.enums.action_type import ActionType
from app.enums.status import AttendanceStatus
from app.timezone import KST


class AttendanceRecordResponse(BaseModel):
    id: UUID
    employee_id: int
    action_type: ActionType
    status: AttendanceStatus
    recorded_at: datetime

    @field_validator("recorded_at", mode="before")
    @classmethod
    def utc_to_kst(cls, v: datetime) -> datetime:
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc).astimezone(KST).replace(tzinfo=None)
        return v

    model_config = {"from_attributes": True}
