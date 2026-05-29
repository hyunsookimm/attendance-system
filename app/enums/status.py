from enum import Enum


class AttendanceStatus(str, Enum):
    WORKING = "WORKING"
    OUT = "OUT"

    @property
    def label(self) -> str:
        labels = {
            "WORKING": "근무 중",
            "OUT": "외출, 퇴근 상태",
        }
        return labels[self.value]
