"""Additions to make bytechomp behave properly"""
from dataclasses import dataclass
from bytechomp.datatypes import U8, F32

@dataclass
class ByteChompByte:
    """Class representing a U8 for use in lists as bytechomp handles this improperly"""
    value: U8

    def __repr__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return int(self.value)

@dataclass
class ByteChompF32:
    """Class representing a F32 for use in lists as bytechomp handles this improperly"""
    value: F32

    def __repr__(self) -> str:
        return str(self.value)

    def __float__(self) -> float:
        return float(self.value)
