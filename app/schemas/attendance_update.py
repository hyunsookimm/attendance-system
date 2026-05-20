from pydantic import BaseModel

from app.enums.status import AttendanceStatus


class AttendanceUpdateRequest(BaseModel):
    status: AttendanceStatus