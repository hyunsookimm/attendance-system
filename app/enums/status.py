from enum import Enum


class AttendanceStatus(str, Enum):
    WORKING = "WORKING"
    OUTING = "OUTING"
    LUNCH = "LUNCH"
    EARLY_LEAVE = "EARLY_LEAVE"
    OFF_WORK = "OFF_WORK"

    @property
    def label(self) -> str:
        labels = {
            "WORKING": "근무 중",
            "OUTING": "외출 중",
            "LUNCH": "점심 중",
            "EARLY_LEAVE": "조퇴",
            "OFF_WORK": "퇴근",
        }
        return labels[self.value]