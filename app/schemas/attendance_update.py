from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.enums.action_type import ActionType


class AttendanceUpdateRequest(BaseModel):
    action_type: Optional[ActionType] = None
    recorded_at: Optional[datetime] = None
