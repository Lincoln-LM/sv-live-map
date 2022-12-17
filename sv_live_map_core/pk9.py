"""Stored pokemon information https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/PKM/PK9.cs"""
from dataclasses import dataclass
from bytechomp import Annotated, ByteOrder, Reader
from bytechomp.datatypes import U8, U16, U32, U64
from .bytechomp_additions import ByteChompByte
from .sv_enums import Species

BLOCK_POSITION = [
    0, 1, 2, 3,
    0, 1, 3, 2,
    0, 2, 1, 3,
    0, 3, 1, 2,
    0, 2, 3, 1,
    0, 3, 2, 1,
    1, 0, 2, 3,
    1, 0, 3, 2,
    2, 0, 1, 3,
    3, 0, 1, 2,
    2, 0, 3, 1,
    3, 0, 2, 1,
    1, 2, 0, 3,
    1, 3, 0, 2,
    2, 1, 0, 3,
    3, 1, 0, 2,
    2, 3, 0, 1,
    3, 2, 0, 1,
    1, 2, 3, 0,
    1, 3, 2, 0,
    2, 1, 3, 0,
    3, 1, 2, 0,
    2, 3, 1, 0,
    3, 2, 1, 0,

    # duplicates of 0-7 to eliminate modulus
    0, 1, 2, 3,
    0, 1, 3, 2,
    0, 2, 1, 3,
    0, 3, 1, 2,
    0, 2, 3, 1,
    0, 3, 2, 1,
    1, 0, 2, 3,
    1, 0, 3, 2,
]

SIZE_9BLOCK = 0x50

def read_int(data: bytearray, location: int, size: int) -> int:
    """Read LE integer from data"""
    return int.from_bytes(data[location:location + size], 'little')

def decrypt_array9(ek9: bytearray) -> bytearray:
    """Decrypt an EK9"""
    decrypted = bytearray(ek9[0:8])

    # encryption constant
    encryption_constant = read_int(ek9, 0, 4)
    shuffle_value = (encryption_constant >> 13) & 31

    seed = encryption_constant
    for index in range(8, 4 * SIZE_9BLOCK + 8, 2):
        # TODO: move to rng.py class?
        # LCRNG :)
        seed = ((seed * 0x41C64E6D) + 0x6073) & 0xFFFFFFFF
        xor = seed >> 16
        # uint16
        decrypted.extend(
            (
                ek9[index] ^ (xor & 0xFF),
                ek9[index + 1] ^ (xor >> 8)
            )
        )

    unshuffled = decrypted.copy()
    index = shuffle_value * 4
    for block in range(4):
        ofs = BLOCK_POSITION[index + block]
        # swap positions of blocks
        unshuffled[8 + (SIZE_9BLOCK * block) : 8 + (SIZE_9BLOCK * (ofs + 1))] = \
            decrypted[8 + (SIZE_9BLOCK * ofs) : 8 + (SIZE_9BLOCK * (ofs + 1))]

    return unshuffled

def is_shiny(pid, tid, sid):
    """Calculate shiniess"""
    return ((pid & 0xFFFF) ^ (pid >> 16) ^ tid ^ sid) < 0x10

@dataclass
class PK9:
    """Stored pokemon information"""
    encryption_constant: U32 # 0x0
    sanity: U16 # 0x4
    checksum: U16 # 0x6

    # Block A
    _species: U16 # 0x8
    _held_item: U16 # 0xA
    tid: U16 # 0xC
    sid: U16 # 0xE
    exp: U32 # 0x10
    _ability: U16 # 0x14
    _ability_favorite_bits: U8 # 0x16
    _unused_17: U8 # 0x17
    mark_value: U16 # 0x18
    _unused_1a: U8 # 0x1A
    _unused_1b: U8 # 0x1B
    pid: U32 # 0x1C
    _nature: U8 # 0x20
    _stat_nature: U8 # 0x21
    _fateful_gender_bits: U8 # 0x22
    _unused_23: U8 # 0x23
    form: U8 # 0x24
    _unused_25: U8 # 0x25
    ev_hp: U8 # 0x26
    ev_atk: U8 # 0x27
    ev_def: U8 # 0x28
    ev_spa: U8 # 0x29
    ev_spd: U8 # 0x2A
    ev_spd: U8 # 0x2B
    cnt_cool: U8 # 0x2C
    cnt_beauty: U8 # 0x2D
    cnt_cute: U8 # 0x2E
    cnt_smart: U8 # 0x2F
    cnt_tough: U8 # 0x30
    cnt_sheen: U8 # 0x31
    pokerus: U8 # 0x32
    _unused_33: U8 # 0x33
    _ribbon_flags_0: U64 # 0x34
    _unused_3e: U8 # 0x3E
    _unused_3f: U8 # 0x3F
    _ribbon_flags_1: U64 # 0x40
    height: U8 # 0x48
    weight: U8 # 0x49
    scale: U8 # 0x4A
    _unused_52: U8 # 0x52
    _unused_53: U8 # 0x53
    _unused_54: U8 # 0x54
    _unused_55: U8 # 0x55
    _unused_56: U8 # 0x56
    _unused_57: U8 # 0x57

    # TODO: Blocks B-D
    _unused = Annotated[list[ByteChompByte], SIZE_9BLOCK * 3]

    def __post_init__(self):
        self.species: Species = Species(self._species)
        self.is_shiny: bool = is_shiny(self.pid, self.tid, self.sid)

@dataclass
class EK9:
    """Encrypted pokemon information"""
    _data: Annotated[list[ByteChompByte], 8 + SIZE_9BLOCK * 4]

    def __post_init__(self):
        self._data = self.decrypt()
        reader = Reader[PK9](ByteOrder.LITTLE).allocate()
        reader.feed(self._data)
        self.pk9: PK9 = reader.build()

    def decrypt(self) -> bytearray:
        """Decrypt data"""
        # bytearray is dumb and wont use int()
        data = bytearray(int(x) for x in self._data)
        # should both be 0 if unencrypted
        if int.from_bytes(data[0x70:0x72], 'little') != 0 or int.from_bytes(data[0x110:0x112], 'little'):
            return decrypt_array9(data)
        return bytes(data)
