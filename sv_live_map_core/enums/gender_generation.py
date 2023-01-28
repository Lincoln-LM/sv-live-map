"""Enums for pokemon gender generation"""
# pylint: disable=too-many-lines

from __future__ import annotations
from enum import IntEnum
from typing import Self


class GenderGeneration(IntEnum):
    """Enum for pokemon gender generation"""
    RANDOM_GENDER = 0
    MALE = 1
    FEMALE = 2
    GENDERLESS = 3

    def __str__(self) -> str:
        return self.name.replace('_', ' ').title()


class Gender(IntEnum):
    """Enum for genders"""
    MALE = 0
    FEMALE = 1
    GENDERLESS = 2

    @staticmethod
    def from_generation(value: GenderGeneration) -> Self:
        """Convert from GenderGeneration"""
        return Gender(value - 1)

    def __str__(self) -> str:
        return self.name.replace('_', ' ').title()
