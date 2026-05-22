from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.enums.action_type import ActionType
from app.enums.status import AttendanceStatus


class AttendanceRecordResponse(BaseModel):
    id: UUID
    employee_id: int
    action_type: ActionType
    status: AttendanceStatus
    recorded_at: datetime

    model_config = {"from_attributes": True}
