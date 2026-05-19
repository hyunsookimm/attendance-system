from enum import Enum


class ActionType(str, Enum):
    CHECK_IN = "CHECK_IN"
    OUTING = "OUTING"
    RETURN = "RETURN"
    LUNCH = "LUNCH"
    EARLY_LEAVE = "EARLY_LEAVE"
    CHECK_OUT = "CHECK_OUT"