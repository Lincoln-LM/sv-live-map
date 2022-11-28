"""Main Application for sv-live-map"""

from nxreader import NXReader
from sv_fbs.sv_enums import StarLevel
from sv_fbs.raid_enemy_table_array import RaidEnemyTableArray

RAID_BINARY_SIZES = (0x3128, 0x3058, 0x4400, 0x5A78, 0x6690, 0x4FB0)

def raid_binary_ptr(star_level: StarLevel) -> tuple[str, int]:
    """Get the pointer to the raid binary in memory"""
    return (
        f"[[[[[[[[main+42FD670]+C0]+E8]]+10]+4A8]+{0xD0 + star_level * 0xB0:X}]+1E8]",
        RAID_BINARY_SIZES[star_level]
    )

reader = NXReader("192.168.0.19")

reta = RaidEnemyTableArray(reader.read_pointer(*raid_binary_ptr(StarLevel.ONE_STAR)))
for table in reta.raid_enemy_tables:
    print(f"{table.raid_enemy_info.rate} {table.raid_enemy_info.boss_poke_para.dev_id!r}")
