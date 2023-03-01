"""Enums relating to save block reading"""

from enum import IntEnum


class SCTypeCode(IntEnum):
    """Save block type codes"""

    NONE = 0
    BOOL_FALSE = 1
    BOOL_TRUE = 2
    BOOL_ARRAY = 3
    OBJECT = 4
    ARRAY = 5
    U8 = 8
    U16 = 9
    U32 = 10
    U64 = 11
    I8 = 12
    I16 = 13
    I32 = 14
    I64 = 15
    FLOAT = 16
    DOUBLE = 17

    def byte_size(self) -> int:
        """Size of type in bytes"""
        match self:
            case SCTypeCode.BOOL_FALSE | SCTypeCode.BOOL_TRUE | SCTypeCode.U8 | SCTypeCode.I8:
                return 1
            case SCTypeCode.U16 | SCTypeCode.I16:
                return 2
            case SCTypeCode.U32 | SCTypeCode.I32 | SCTypeCode.FLOAT:
                return 4
            case SCTypeCode.U64 | SCTypeCode.I64 | SCTypeCode.DOUBLE:
                return 8
            case _:
                raise NotImplementedError(
                    f"{self:!r} does not have an implemented size."
                )

    def is_signed(self) -> bool:
        """Whether or not a type is a signed int"""
        return SCTypeCode.U64 < self < SCTypeCode.FLOAT
