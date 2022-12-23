"""Enums for pokemon type generation"""
# pylint: disable=too-many-lines

from __future__ import annotations
from enum import IntEnum
from typing import Self

class TeraTypeGeneration(IntEnum):
    """Enum for pokemon tera type generation"""
    NONE = 0
    RANDOM = 1
    NORMAL = 2
    FIGHTING = 3
    FLYING = 4
    POISON = 5
    GROUND = 6
    ROCK = 7
    BUG = 8
    GHOST = 9
    STEEL = 10
    FIRE = 11
    WATER = 12
    GRASS = 13
    ELECTRIC = 14
    PSYCHIC = 15
    ICE = 16
    DRAGON = 17
    DARK = 18
    FAIRY = 19

    def __str__(self) -> str:
        return self.name.replace('_', ' ').title()

class TeraType(IntEnum):
    """Enum for pokemon tera type"""
    NORMAL = 0
    FIGHTING = 1
    FLYING = 2
    POISON = 3
    GROUND = 4
    ROCK = 5
    BUG = 6
    GHOST = 7
    STEEL = 8
    FIRE = 9
    WATER = 10
    GRASS = 11
    ELECTRIC = 12
    PSYCHIC = 13
    ICE = 14
    DRAGON = 15
    DARK = 16
    FAIRY = 17

    @staticmethod
    def from_generation(generation: TeraTypeGeneration) -> Self:
        """Convert from TeraTypeGeneration"""
        return TeraType(generation - 2)

    def __str__(self) -> str:
        return self.name.replace('_', ' ').title()

class PokemonType(IntEnum):
    """Enum for pokemon type"""
    NORMAL = 0
    FIGHTING = 1
    FLYING = 2
    POISON = 3
    GROUND = 4
    ROCK = 5
    BUG = 6
    GHOST = 7
    STEEL = 8
    FIRE = 9
    WATER = 10
    GRASS = 11
    ELECTRIC = 12
    PSYCHIC = 13
    ICE = 14
    DRAGON = 15
    DARK = 16
    FAIRY = 17

    def __str__(self) -> str:
        return self.name.replace('_', ' ').title()
