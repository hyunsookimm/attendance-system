from datetime import datetime

from pydantic import BaseModel, field_validator

from app.enums.action_type import ActionType
from app.timezone import KST


class AttendanceCreateRequest(BaseModel):
    employee_id: int
    action_type: ActionType
    recorded_at: datetime

    @field_validator("recorded_at", mode="after")
    @classmethod
    def validate_recorded_at(cls, v: datetime) -> datetime:
        if v.tzinfo is not None:
            v = v.astimezone(KST).replace(tzinfo=None)
        if v > datetime.now(KST).replace(tzinfo=None):
            raise ValueError("미래 시간은 입력할 수 없습니다")
        return v
