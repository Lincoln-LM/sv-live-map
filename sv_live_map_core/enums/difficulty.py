"""Enums for raid difficulty"""
# pylint: disable=too-many-lines

from __future__ import annotations
from enum import IntEnum
from typing import Self


class StoryProgress(IntEnum):
    """Enum for story progress"""
    DEFAULT = 0
    THREE_STAR_UNLOCKED = 1
    FOUR_STAR_UNLOCKED = 2
    FIVE_STAR_UNLOCKED = 3
    SIX_STAR_UNLOCKED = 4

    def to_star_level(self) -> StarLevel:
        """Convert StoryProgress to the highest StarLevel it unlocks (excl SEVEN_STAR)"""
        return StarLevel(self + StarLevel.TWO_STAR)

    def __str__(self) -> str:
        return self.name.replace('_', ' ').title()


class StarLevel(IntEnum):
    """Enum for the basic star levels"""
    ONE_STAR = 0
    TWO_STAR = 1
    THREE_STAR = 2
    FOUR_STAR = 3
    FIVE_STAR = 4
    SIX_STAR = 5

    # event exclusive
    SEVEN_STAR = 6

    # for easy compatability
    EVENT = -1

    @staticmethod
    def from_game(value: int) -> Self:
        """Convert from the value sometimes used in game"""
        return StarLevel(value - 1)

    def is_unlocked(self, story_progress: StoryProgress) -> bool:
        """Check if a den of this difficulty is allowed to be generated"""
        # five star makes 1/2 stars not appear
        if self <= StarLevel.TWO_STAR:
            return story_progress < StoryProgress.FIVE_STAR_UNLOCKED

        # six star also unlocks seven star
        if self == StarLevel.SEVEN_STAR:
            return story_progress >= StoryProgress.SIX_STAR_UNLOCKED

        # staggered unlocks
        return self <= story_progress.to_star_level()

    def __str__(self) -> str:
        return self.name.replace('_', ' ').title()
