from typing import List

from pydantic import BaseModel, computed_field

from app.schemas.attendance_response import AttendanceRecordResponse


class WorkHoursResponse(BaseModel):
    employee_id: int
    total_minutes: int
    is_currently_in: bool
    records: List[AttendanceRecordResponse]

    @computed_field
    @property
    def hours(self) -> int:
        return self.total_minutes // 60

    @computed_field
    @property
    def minutes(self) -> int:
        return self.total_minutes % 60
