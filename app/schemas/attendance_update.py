from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.enums.action_type import ActionType
from app.timezone import KST


class AttendanceUpdateRequest(BaseModel):
    action_type: Optional[ActionType] = None
    recorded_at: Optional[datetime] = None

    @field_validator("recorded_at", mode="after")
    @classmethod
    def validate_recorded_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return v
        if v.tzinfo is not None:
            v = v.astimezone(KST).replace(tzinfo=None)
        if v > datetime.now(KST).replace(tzinfo=None):
            raise ValueError("미래 시간은 입력할 수 없습니다")
        return v
