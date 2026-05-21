from pydantic import BaseModel

from app.enums.action_type import ActionType


class AttendanceUpdateRequest(BaseModel):
    action_type: ActionType