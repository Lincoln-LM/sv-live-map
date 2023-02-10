"""Misc enums for data from SV"""
# pylint: disable=too-many-lines

from __future__ import annotations
from enum import IntEnum
from typing import Self


class Game(IntEnum):
    """Enum for the game version"""

    BOTH = 0
    SCARLET = 1
    VIOLET = 2

    @staticmethod
    def from_game_id(value: int) -> Self:
        """Convert game id to Game enum"""
        return Game(value - 49)

    def __str__(self) -> str:
        return self.name.replace("_", " ").title()


class Ball(IntEnum):
    """Enum for pokemon balls"""

    NONE = 0
    MASTER_BALL = 1
    ULTRA_BALL = 2
    GREAT_BALL = 3
    POKE_BALL = 4
    SAFARI_BALL = 5
    NET_BALL = 6
    DIVE_BALL = 7
    NEST_BALL = 8
    REPEAT_BALL = 9
    TIMER_BALL = 10
    LUXURY_BALL = 11
    PREMIER_BALL = 12
    DUSK_BALL = 13
    HEAL_BALL = 14
    QUICK_BALL = 15
    CHERISH_BALL = 16
    FAST_BALL = 17
    LEVEL_BALL = 18
    LURE_BALL = 19
    HEAVY_BALL = 20
    LOVE_BALL = 21
    FRIEND_BALL = 22
    MOON_BALL = 23
    SPORT_BALL = 24
    DREAM_BALL = 25
    BEAST_BALL = 26

    def __str__(self) -> str:
        return self.name.replace("_", " ").title()


class MovesetType(IntEnum):
    """Enum for pokemon moveset generation"""

    AUTO = 0
    SET = 1

    def __str__(self) -> str:
        return self.name.replace("_", " ").title()


class ExtraActType(IntEnum):
    """Enum for raid boss extra act type"""

    NONE = 0
    BOSS_STATUS_RESET = 1
    PLAYER_STATUS_RESET = 2
    MOVE = 3
    GEM_COUNT = 4

    def __str__(self) -> str:
        return self.name.replace("_", " ").title()


class ExtraTimingType(IntEnum):
    """Enum for raid boss extra timing type"""

    NONE = 0
    TIME = 1
    HP = 2

    def __str__(self) -> str:
        return self.name.replace("_", " ").title()


class Language(IntEnum):
    """Enum for save language"""

    UNSET = 0
    JAPANESE = 1
    ENGLISH = 2
    FRENCH = 3
    ITALIAN = 4
    GERMAN = 5
    UNUSED_6 = 6
    SPANISH = 7
    KOREAN = 8
    CHINESE_SIMPLIFIED = 9
    CHINESE_TRADITIONAL = 10

    def __str__(self) -> str:
        return self.name.replace("_", "_").title()
