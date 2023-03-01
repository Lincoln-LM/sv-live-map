"""Enums for pokemon nature generation"""
# pylint: disable=too-many-lines

from __future__ import annotations
from enum import IntEnum
from typing import Self


class NatureGeneration(IntEnum):
    """Enum for pokemon nature generation"""

    NONE = 0
    HARDY = 1
    LONELY = 2
    BRAVE = 3
    ADAMANT = 4
    NAUGHTY = 5
    BOLD = 6
    DOCILE = 7
    RELAXED = 8
    IMPISH = 9
    LAX = 10
    TIMID = 11
    HASTY = 12
    SERIOUS = 13
    JOLLY = 14
    NAIVE = 15
    MODEST = 16
    MILD = 17
    QUIET = 18
    BASHFUL = 19
    RASH = 20
    CALM = 21
    GENTLE = 22
    SASSY = 23
    CAREFUL = 24
    QUIRKY = 25

    def __str__(self) -> str:
        return self.name.replace("_", " ").title()


class Nature(IntEnum):
    """Enum for Pokemon nature"""

    HARDY = 0
    LONELY = 1
    BRAVE = 2
    ADAMANT = 3
    NAUGHTY = 4
    BOLD = 5
    DOCILE = 6
    RELAXED = 7
    IMPISH = 8
    LAX = 9
    TIMID = 10
    HASTY = 11
    SERIOUS = 12
    JOLLY = 13
    NAIVE = 14
    MODEST = 15
    MILD = 16
    QUIET = 17
    BASHFUL = 18
    RASH = 19
    CALM = 20
    GENTLE = 21
    SASSY = 22
    CAREFUL = 23
    QUIRKY = 24

    @staticmethod
    def from_generation(generation: NatureGeneration) -> Self:
        """Convert from NatureGeneration"""
        return Nature(generation - 1)

    def __str__(self) -> str:
        return self.name.replace("_", " ").title()
