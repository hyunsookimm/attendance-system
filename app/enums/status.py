from enum import Enum


class AttendanceStatus(str, Enum):
    WORKING = "WORKING"
    OUTING = "OUTING"
    LUNCH = "LUNCH"
    EARLY_LEAVE = "EARLY_LEAVE"
    OFF_WORK = "OFF_WORK"