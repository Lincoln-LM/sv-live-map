"""Main Application for sv-live-map"""

from sv_live_map_core.nxreader import NXReader
from sv_live_map_core.sv_enums import StarLevel, StoryProgress
from sv_live_map_core.raid_enemy_table_array import RaidEnemyTableArray
from sv_live_map_core.raid_block import process_raid_block
from sv_live_map_core.rng import SCXorshift32

RAID_BINARY_SIZES = (0x3128, 0x3058, 0x4400, 0x5A78, 0x6690, 0x4FB0)
# https://github.com/Manu098vm/SVResearches/blob/master/RAM%20Pointers/RAM%20Pointers.txt
RAID_BLOCK_PTR = ("[[main+42FD560]+160]+40", 0xC98) # ty skylink!
RAID_BINARY_EVENT_PTR = ("[[[[[main+42DA820]+30]+388]+300]+28]+414", 0x7530)

def raid_binary_ptr(star_level: StarLevel) -> tuple[str, int]:
    """Get the pointer to the raid binary in memory"""
    return (
        f"[[[[[[[[main+42FD670]+C0]+E8]]+10]+4A8]+{0xD0 + star_level * 0xB0:X}]+1E8]",
        RAID_BINARY_SIZES[star_level]
    )

def get_story_progress(_reader: NXReader) -> StoryProgress:
    """Read and decrypt story progress from save blocks"""
    difficulty_6_key = _reader.read_pointer_int("[[[[[main+42F3130]+B0]]]+30]+8]+13E80", 4)
    difficulty_6_val = _reader.read_pointer_int("[[[[[[main+42F3130]+B0]]]+30]+8]+13E88]", 1) \
        ^ SCXorshift32(difficulty_6_key).next()
    if difficulty_6_val == 2:
        return StoryProgress.SIX_STAR_UNLOCKED
    difficulty_5_key = _reader.read_pointer_int("[[[[[main+42F3130]+B0]]]+30]+8]+1B600", 4)
    difficulty_5_val = _reader.read_pointer_int("[[[[[[main+42F3130]+B0]]]+30]+8]+1B608]", 1) \
        ^ SCXorshift32(difficulty_5_key).next()
    if difficulty_5_val == 2:
        return StoryProgress.FIVE_STAR_UNLOCKED
    difficulty_4_key = _reader.read_pointer_int("[[[[[main+42F3130]+B0]]]+30]+8]+1F3C0", 4)
    difficulty_4_val = _reader.read_pointer_int("[[[[[[main+42F3130]+B0]]]+30]+8]+1F3C8]", 1) \
        ^ SCXorshift32(difficulty_4_key).next()
    if difficulty_4_val == 2:
        return StoryProgress.FOUR_STAR_UNLOCKED
    difficulty_3_key = _reader.read_pointer_int("[[[[[main+42F3130]+B0]]]+30]+8]+2BEE0", 4)
    difficulty_3_val = _reader.read_pointer_int("[[[[[[main+42F3130]+B0]]]+30]+8]+2BEE8]", 1) \
        ^ SCXorshift32(difficulty_3_key).next()
    if difficulty_3_val == 2:
        return StoryProgress.THREE_STAR_UNLOCKED
    return StoryProgress.DEFAULT

def main():
    """Main function of the appliation"""
    reader = NXReader("192.168.0.19")

    story_progress = get_story_progress(reader)
    raid_enemy_table_arrays = (
        RaidEnemyTableArray(
            reader.read_pointer(*raid_binary_ptr(StarLevel.ONE_STAR))
        ),
        RaidEnemyTableArray(
            reader.read_pointer(*raid_binary_ptr(StarLevel.TWO_STAR))
        ),
        RaidEnemyTableArray(
            reader.read_pointer(*raid_binary_ptr(StarLevel.THREE_STAR))
        ),
        RaidEnemyTableArray(
            reader.read_pointer(*raid_binary_ptr(StarLevel.FOUR_STAR))
        ),
        RaidEnemyTableArray(
            reader.read_pointer(*raid_binary_ptr(StarLevel.FIVE_STAR))
        ),
        RaidEnemyTableArray(
            reader.read_pointer(*raid_binary_ptr(StarLevel.SIX_STAR))
        ),
        RaidEnemyTableArray(
            reader.read_pointer(*RAID_BINARY_EVENT_PTR)
        ),
    )
    raid_block = process_raid_block(reader.read_pointer(*RAID_BLOCK_PTR))
    raid_block.initialize_data(raid_enemy_table_arrays, story_progress)
    for raid in raid_block.raids:
        print(raid)

if __name__ == "__main__":
    main()
