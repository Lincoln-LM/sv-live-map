"""Enum for input seq events events"""

from enum import IntEnum


class InputSeqEvent(IntEnum):
    """Enum for clickseq events"""

    CLICK = 0
    WAIT = 1
    PRESS = 2
    RELEASE = 3
    MOVE_LEFT_STICK = 4
    MOVE_RIGHT_STICK = 5
    TOUCH = 6
    TOUCH_HOLD = 7
