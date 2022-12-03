"""Overworld data stored in the save file"""
from dataclasses import dataclass
from bytechomp import Annotated
from sv_live_map_core.pk9 import EK9, PK9
from sv_live_map_core.bytechomp_additions import ByteChompByte, ByteChompF32

@dataclass
class KOverworldPokemon:
    """Inner data of KOveworld array"""
    _val_0: Annotated[list[ByteChompByte], 5]
    _ekm: EK9
    _party_data: Annotated[list[ByteChompByte], 0x10]
    position: Annotated[list[ByteChompF32], 3]
    _val_1: Annotated[list[ByteChompByte], 0x6B]

    def __post_init__(self):
        self.pkm: PK9 = self._ekm.pk9

@dataclass
class KOverworld:
    """KOveworld save block"""
    inner_data: Annotated[list[KOverworldPokemon], 20]
