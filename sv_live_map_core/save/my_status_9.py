"""MyStatus9 Save Block"""

from dataclasses import dataclass
from bytechomp.datatypes import U16, U8
from bytechomp import Annotated
from ..enums import Game, Gender, Language

@dataclass
class CharacterByte:
    """Half of a utf16-le character"""
    value: U8

@dataclass
class UnusedByte:
    """Unused byte"""
    _unused: U8

@dataclass
class MyStatus9:
    """MyStatus9 Save Block"""
    tid: U16
    sid: U16
    _game: U8
    _gender: U16
    _language: U8
    _unused_0: Annotated[list[UnusedByte], 8]
    _ot_trash: Annotated[list[CharacterByte], 20]
    _unused_1: Annotated[list[UnusedByte], 0x36]
    birth_month: U8
    birth_day: U8

    def __post_init__(self):
        self.full_id = ((self.sid << 16) | self.tid)
        self.g9tid = self.full_id % 1000000
        self.g9sid = self.full_id // 1000000
        self.game = Game.from_game_id(self._game)
        self.gender = Gender(self._gender)
        self.language = Language(self._language)
        self.original_trainer = bytes(
            char_byte.value for char_byte in self._ot_trash
        ).decode("utf-16le")

    def __str__(self) -> str:
        return f"OT: {self.original_trainer} TID: {self.g9tid} SID: {self.g9sid}"
