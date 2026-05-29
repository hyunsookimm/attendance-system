from enum import Enum


class ActionType(str, Enum):
    ENTER = "ENTER"
    EXIT = "EXIT"

    @property
    def label(self) -> str:
        labels = {
            "ENTER": "입장",
            "EXIT": "퇴장",
        }
        return labels[self.value]
