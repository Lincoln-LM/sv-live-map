"""Misc enums for pokemon generation"""

from enum import IntEnum


class IVGeneration(IntEnum):
    """Enum for pokemon IV generation"""

    RANDOM_IVS = 0
    SET_GUARANTEED_IVS = 1
    SET_IVS = 2

    def __str__(self) -> str:
        return self.name.replace("_", " ").title()


class ShinyGeneration(IntEnum):
    """Enum for pokemon shininess generation"""

    RANDOM_SHININESS = 0
    SHINY_LOCKED = 1
    FORCED_SHINY = 2

    def __str__(self) -> str:
        return self.name.replace("_", " ").title()


class SizeGeneration(IntEnum):
    """Enum for pokemon size generation"""

    RANDOM_SIZE = 0
    XS = 1
    S = 2
    M = 3
    L = 4
    XL = 5
    SET_VALUE = 6

    def __str__(self) -> str:
        return self.name.replace("_", " ").title()
