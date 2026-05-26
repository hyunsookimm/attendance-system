from enum import Enum


class ActionType(str, Enum):
    CHECK_IN = "CHECK_IN"
    OUTING = "OUTING"
    RETURN = "RETURN"
    LUNCH = "LUNCH"
    EARLY_LEAVE = "EARLY_LEAVE"
    CHECK_OUT = "CHECK_OUT"

    @property
    def label(self) -> str:
        labels = {
            "CHECK_IN": "출근",
            "OUTING": "외출",
            "RETURN": "복귀",
            "LUNCH": "점심",
            "EARLY_LEAVE": "조퇴",
            "CHECK_OUT": "퇴근",
        }
        return labels[self.value]