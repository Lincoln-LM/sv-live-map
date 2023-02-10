"""Enum for sysbot-base buttons"""

from enum import Enum


class Button(Enum):
    """Enum for sysbot-base buttons"""
    A = "A"
    B = "B"
    X = "X"
    Y = "Y"

    LEFT_STICK = "LSTICK"
    RIGHT_STICK = "RSTICK"

    L = "L"
    R = "R"
    ZL = "ZL"
    ZR = "ZR"

    PLUS = "PLUS"
    MINUS = "MINUS"

    DPAD_LEFT = "DL"
    DPAD_UP = "DU"
    DPAD_DOWN = "DD"
    DPAD_RIGHT = "DR"

    HOME = "HOME"
    CAPTURE = "CAPTURE"
    POKEBALL_PLUS = "PALMA"


class Stick(Enum):
    """Enum for sysbot-base sticks"""
    LEFT = "LEFT"
    RIGHT = "RIGHT"
