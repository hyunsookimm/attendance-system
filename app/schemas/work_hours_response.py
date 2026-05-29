from typing import List

from pydantic import BaseModel

from app.schemas.attendance_response import AttendanceRecordResponse


class WorkHoursResponse(BaseModel):
    employee_id: int
    total_minutes: int
    is_currently_in: bool
    records: List[AttendanceRecordResponse]
