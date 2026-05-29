from datetime import datetime

from pydantic import BaseModel

from app.enums.action_type import ActionType


class AttendanceCreateRequest(BaseModel):
    employee_id: int
    action_type: ActionType
    recorded_at: datetime
