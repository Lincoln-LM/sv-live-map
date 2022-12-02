"""Subclass of NXReader with functions specifically for raids"""

import socket
from sv_live_map_core.nxreader import NXReader
from sv_live_map_core.sv_enums import StarLevel, StoryProgress, Game
from sv_live_map_core.raid_enemy_table_array import RaidEnemyTableArray
from sv_live_map_core.delivery_raid_priority_array import DeliveryRaidPriorityArray
from sv_live_map_core.raid_block import RaidBlock, process_raid_block
from sv_live_map_core.rng import SCXorshift32

class RaidReader(NXReader):
    """Subclass of NXReader with functions specifically for raids"""
    RAID_BINARY_SIZES = (0x3128, 0x3058, 0x4400, 0x5A78, 0x6690, 0x4FB0)
    RAID_PRIORITY_PTR = ("[[[[main+43A7798]+08]+2C0]+10]+88", 0x58)
    # https://github.com/Manu098vm/SVResearches/blob/master/RAM%20Pointers/RAM%20Pointers.txt
    RAID_BLOCK_PTR = ("[[main+43A77C8]+160]+40", 0xC98) # ty skylink!
    SAVE_BLOCK_PTR = "[[[main+4385F30]+80]+8]"
    DIFFICULTY_FLAG_LOCATIONS = (0x2BF20, 0x1F400, 0x1B640, 0x13EC0)

    def __init__(
        self,
        ip_address: str = None,
        port: int = 6000,
        read_safety: bool = False,
        raid_enemy_table_arrays: tuple[RaidEnemyTableArray, 7] = None,
    ):
        super().__init__(ip_address, port)
        self.read_safety = read_safety
        self.raid_enemy_table_arrays: tuple[RaidEnemyTableArray, 7] = \
            raid_enemy_table_arrays or self.read_raid_enemy_table_arrays()
        # TODO: cache
        self.delivery_raid_priority: tuple[int] = self.read_delivery_raid_priority()
        self.story_progress: StoryProgress = self.read_story_progess()
        self.game_version: Game = self.read_game_version()

    def read_delivery_raid_priority(self) -> tuple[int]:
        """Read the delivery priority flatbuffer from memory"""
        return DeliveryRaidPriorityArray(self.read_pointer(*self.RAID_PRIORITY_PTR)) \
            .delivery_raid_prioritys[0] \
            .delivery_group_id \
            .group_counts

    @staticmethod
    def raid_binary_ptr(star_level: StarLevel) -> tuple[str, int]:
        """Get a pointer to the raid flatbuffer binary in memory"""
        if star_level == StarLevel.EVENT:
            return ("[[[[[[main+4384A50]+30]+288]+290]+280]+28]+414", 0x7530)
        return (
            f"[[[[[[[[main+43A78D8]+C0]+E8]]+10]+4A8]+{0xD0 + star_level * 0xB0:X}]+1E8]",
            RaidReader.RAID_BINARY_SIZES[star_level]
        )

    def read_story_progess(self) -> StoryProgress:
        """Read and decrypt story progress from save blocks"""
        # each key remains constant and SCXorshift32(difficulty_{n}_key).next() can be precomputed
        # for the sake of showing how to decrypt it this is not done
        loc = self.DIFFICULTY_FLAG_LOCATIONS[3]
        difficulty_6_key = self.read_pointer_int(f"{self.SAVE_BLOCK_PTR}+{loc:X}", 4)
        difficulty_6_val = self.read_pointer_int(f"[{self.SAVE_BLOCK_PTR}+{loc+8:X}]", 1) \
            ^ SCXorshift32(difficulty_6_key).next()
        if difficulty_6_val == 2:
            return StoryProgress.SIX_STAR_UNLOCKED
        loc = self.DIFFICULTY_FLAG_LOCATIONS[2]
        difficulty_5_key = self.read_pointer_int(f"{self.SAVE_BLOCK_PTR}+{loc:X}", 4)
        difficulty_5_val = self.read_pointer_int(f"[{self.SAVE_BLOCK_PTR}+{loc+8:X}]", 1) \
            ^ SCXorshift32(difficulty_5_key).next()
        if difficulty_5_val == 2:
            return StoryProgress.FIVE_STAR_UNLOCKED
        loc = self.DIFFICULTY_FLAG_LOCATIONS[1]
        difficulty_4_key = self.read_pointer_int(f"{self.SAVE_BLOCK_PTR}+{loc:X}", 4)
        difficulty_4_val = self.read_pointer_int(f"[{self.SAVE_BLOCK_PTR}+{loc+8:X}]", 1) \
            ^ SCXorshift32(difficulty_4_key).next()
        if difficulty_4_val == 2:
            return StoryProgress.FOUR_STAR_UNLOCKED
        loc = self.DIFFICULTY_FLAG_LOCATIONS[0]
        difficulty_3_key = self.read_pointer_int(f"{self.SAVE_BLOCK_PTR}+{loc:X}", 4)
        difficulty_3_val = self.read_pointer_int(f"[{self.SAVE_BLOCK_PTR}+{loc+8:X}]", 1) \
            ^ SCXorshift32(difficulty_3_key).next()
        if difficulty_3_val == 2:
            return StoryProgress.THREE_STAR_UNLOCKED
        return StoryProgress.DEFAULT

    def read_game_version(self) -> Game:
        """Read game version"""
        return Game(self.read_main_int(0x4385FD0, 4) - 49)

    def read_raid_enemy_table_arrays(self) -> tuple[RaidEnemyTableArray, 7]:
        """Read all raid flatbuffer binaries from memory"""
        return (
            RaidEnemyTableArray(
                self.read_pointer(*self.raid_binary_ptr(StarLevel.ONE_STAR))
            ),
            RaidEnemyTableArray(
                self.read_pointer(*self.raid_binary_ptr(StarLevel.TWO_STAR))
            ),
            RaidEnemyTableArray(
                self.read_pointer(*self.raid_binary_ptr(StarLevel.THREE_STAR))
            ),
            RaidEnemyTableArray(
                self.read_pointer(*self.raid_binary_ptr(StarLevel.FOUR_STAR))
            ),
            RaidEnemyTableArray(
                self.read_pointer(*self.raid_binary_ptr(StarLevel.FIVE_STAR))
            ),
            RaidEnemyTableArray(
                self.read_pointer(*self.raid_binary_ptr(StarLevel.SIX_STAR))
            ),
            RaidEnemyTableArray(
                self.read_pointer(*self.raid_binary_ptr(StarLevel.EVENT))
            ),
        )

    def read_raid_block_data(self) -> RaidBlock:
        """Read raid block data from memory and process"""
        raid_block = process_raid_block(self.read_pointer(*self.RAID_BLOCK_PTR))
        raid_block.initialize_data(
            self.raid_enemy_table_arrays, 
            self.story_progress,
            self.game_version,
            self.delivery_raid_priority
        )
        return raid_block

    def check_if_data_avaiable(self):
        """Check if data is avaiable to be read from socket"""
        try:
            self.socket.recv(1, socket.MSG_PEEK)
            return True
        except TimeoutError:
            return False

    def clear_all_data(self):
        """Clear all data waiting to be read"""
        try:
            while self.check_if_data_avaiable():
                self.socket.recv(0x8000)
        except TimeoutError:
            pass

    def read(self, address, size):
        if self.read_safety:
            self.clear_all_data()
        return super().read(address, size)

    def read_absolute(self, address, size):
        if self.read_safety:
            self.clear_all_data()
        return super().read_absolute(address, size)

    def read_main(self, address, size):
        if self.read_safety:
            self.clear_all_data()
        return super().read_main(address, size)

    def read_pointer(self, pointer, size):
        if self.read_safety:
            self.clear_all_data()
        return super().read_pointer(pointer, size)
