"""Fixed symbol data stored in the save file"""
from dataclasses import dataclass
from bytechomp import Annotated
from bytechomp.datatypes import U64, U32, U16, U8
from sv_live_map_core.pk9 import EK9, PK9
from sv_live_map_core.bytechomp_additions import ByteChompByte, ByteChompF32

@dataclass
class FixedSymbol:
    """Fixed symbol data stored in the save file"""
    fnv_hash: U64
    active: U8
    _ekm: EK9
    _party_data: Annotated[list[ByteChompByte], 0x10]
    _pad_0: Annotated[list[ByteChompByte], 15]

    def __post_init__(self):
        self.pkm: PK9 = self._ekm.pk9

@dataclass
class FixedSymbolRetainer:
    """List of FixedSymbols"""
    _pad_0: U32
    _pad_1: U8
    symbols: Annotated[list[FixedSymbol], 0x80]
