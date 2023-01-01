"""Subclass of NXReader with functions specifically for raids"""

import contextlib
import socket
import io
import struct
from typing import Type
import bytechomp
from PIL import Image
from .nxreader import NXReader
from ..enums import StarLevel, StoryProgress, Game
from ..fbs.raid_enemy_table_array import RaidEnemyTableArray
from ..fbs.delivery_raid_priority_array import DeliveryRaidPriorityArray
from ..fbs.raid_fixed_reward_item_array import RaidFixedRewardItemArray
from ..fbs.raid_lottery_reward_item_array import RaidLotteryRewardItemArray
from ..save.raid_block import RaidBlock, process_raid_block
from ..rng import SCXorshift32
from ..save.my_status_9 import MyStatus9

# TODO: exceptions.py
class SaveBlockError(Exception):
    """Error when reading save block"""

class RaidReader(NXReader):
    """Subclass of NXReader with functions specifically for raids"""
    RAID_BINARY_SIZES = (0x3128, 0x3058, 0x4400, 0x5A78, 0x6690, 0x4FB0)
    RAID_BINARY_OFS = (0x8, 0x8, 0x4, 0x4, 0x4, 0x4, None)
    # https://github.com/Manu098vm/SVResearches/blob/master/RAM%20Pointers/RAM%20Pointers.txt
    RAID_BLOCK_PTR = ("[[main+43A77C8]+160]+40", 0xC98) # ty skylink!
    SAVE_BLOCK_PTR = "[[[main+4385F30]+80]+8]"
    GAME_ID_OFS = 0x4385FD0 # game_id = *(main + GAME_ID_OFS)
    # save block locations and keys: (ofs, key)
    DIFFICULTY_FLAG_LOCATIONS = (
        (0x2BF20, 0xEC95D8EF),
        (0x1F400, 0xA9428DFE),
        (0x1B640, 0x9535F471),
        (0x13EC0, 0x6E7F8220)
    )
    MY_STATUS_LOCATION = (0x29F40, 0xE3E89BD1)
    BCAT_RAID_BINARY_LOCATION = (0x1040, 0x520A1B0)
    BCAT_RAID_PRIORITY_LOCATION = (0x1860, 0x95451E4)
    BCAT_RAID_FIXED_REWARD_LOCATION = (0x16D40, 0x7D6C2B82)
    BCAT_RAID_LOTTERY_REWARD_LOCATION = (0x1E6A0, 0xA52B4811)
    TRAINER_ICON_WIDTH_LOCATION = (0x1A3C0, 0x8FAB2C4D)
    TRAINER_ICON_HEIGHT_LOCATION = (0x1DA0, 0xB384C24)
    TRAINER_ICON_LOCATION = (0x273E0, 0xD41F4FC4)

    def __init__(
        self,
        ip_address: str = None,
        port: int = 6000,
        usb_connection: bool = False,
        read_safety: bool = False,
        raid_enemy_table_arrays: tuple[bytes, 7] = None,
        raid_item_table_arrays: tuple[bytes, 2] = None,
    ):
        super().__init__(ip_address, port, usb_connection)
        self.read_safety = read_safety
        if raid_enemy_table_arrays is None:
            self.raid_enemy_table_arrays: tuple[RaidEnemyTableArray, 7] = \
                self.read_raid_enemy_table_arrays()
        else:
            self.raid_enemy_table_arrays = \
                [RaidEnemyTableArray(table) for table in raid_enemy_table_arrays]
            self.raid_enemy_table_arrays.append(
                RaidEnemyTableArray(
                    self.read_raid_binary(
                        StarLevel.EVENT
                    )
                )
            )
        if raid_item_table_arrays is None:
            self.raid_item_table_arrays: \
                tuple[RaidFixedRewardItemArray | RaidLotteryRewardItemArray, 4] = \
                self.read_raid_item_table_arrays()
        else:
            self.raid_item_table_arrays: \
                tuple[RaidFixedRewardItemArray | RaidLotteryRewardItemArray, 4] = (
                    RaidFixedRewardItemArray(raid_item_table_arrays[0]),
                    RaidLotteryRewardItemArray(raid_item_table_arrays[1]),
                    *self.read_delivery_item_binaries()
                )
        self.delivery_raid_priority: tuple[int] = self.read_delivery_raid_priority()
        self.story_progress: StoryProgress = self.read_story_progess()
        self.game_version: Game = self.read_game_version()
        self.my_status: MyStatus9 = self.read_my_status()
        print(f"Trainer Info | {self.my_status}")

    def read_delivery_raid_priority(self) -> tuple[int]:
        """Read the delivery priority flatbuffer from the save"""
        delivery_raid_priority_array = DeliveryRaidPriorityArray(
            self.read_save_block_object(*self.BCAT_RAID_PRIORITY_LOCATION)
        )
        if len(delivery_raid_priority_array.delivery_raid_prioritys) == 0:
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        return delivery_raid_priority_array \
            .delivery_raid_prioritys[0] \
            .delivery_group_id \
            .group_counts

    def read_raid_fixed_item_binary(self) -> bytes:
        """Read raid fixed item flatbuffer binary from memory"""
        return self.read_pointer("[[[[[[[[main+43A77B8]+20]+2B0]+60]+30]+208]]+5D0]", 0x1CA8)

    def read_raid_lottery_item_binary(self) -> bytes:
        """Read raid lottery item flatbuffer binary from memory"""
        return self.read_absolute(
            self.read_pointer_int(
                "[[[[[[[main+43A77B8]+20]+2B0]+60]+28]+200]]+E8",
                8
            ) - 0xC,
            0x3AC8
        )

    def read_delivery_item_binaries(
        self
    ) -> tuple[RaidFixedRewardItemArray | RaidLotteryRewardItemArray, 2]:
        """Read delivery item flatbuffer binaries from save blocks"""
        return (
            RaidFixedRewardItemArray(
                self.read_save_block_object(
                    *self.BCAT_RAID_FIXED_REWARD_LOCATION
                )
            ),
            RaidLotteryRewardItemArray(
                self.read_save_block_object(
                    *self.BCAT_RAID_LOTTERY_REWARD_LOCATION
                )
            ),
        )

    def read_raid_item_table_arrays(
        self
    ) -> tuple[RaidFixedRewardItemArray | RaidLotteryRewardItemArray, 4]:
        """Read raid item table arrays from flatbuffer binaries stored in memory"""
        return (
            RaidFixedRewardItemArray(self.read_raid_fixed_item_binary()),
            RaidLotteryRewardItemArray(self.read_raid_lottery_item_binary()),
            *self.read_delivery_item_binaries()
        )

    def read_raid_binary(self, star_level: StarLevel) -> bytes:
        """Read raid flatbuffer binary from memory"""
        if star_level == StarLevel.EVENT:
            return self.read_save_block_object(*self.BCAT_RAID_BINARY_LOCATION)
        return self.read_absolute(
            self.read_pointer_int(
                f"[[[[[[[[main+43A77B8]+20]+2B0]+60]+10]+208]]+198]+{(star_level + 1) * 0xB0:X}",
                8
            ) - self.RAID_BINARY_OFS[star_level],
            self.RAID_BINARY_SIZES[star_level]
        )

    def read_story_progess(self) -> StoryProgress:
        """Read and decrypt story progress from save blocks"""
        progress = StoryProgress.SIX_STAR_UNLOCKED
        for (ofs, key) in reversed(self.DIFFICULTY_FLAG_LOCATIONS):
            if self.read_save_block_bool(ofs, key = key):
                return StoryProgress(progress)
            progress -= 1
        return StoryProgress.DEFAULT

    def read_my_status(self) -> MyStatus9:
        """Read trainer info"""
        ofs, key = self.MY_STATUS_LOCATION
        return self.read_save_block_struct(ofs, MyStatus9, key = key)

    def _search_save_block(self, base_offset: int, key: int = None) -> tuple[int, int]:
        """Search memory for the correct save block offset"""
        if key is None:
            return base_offset, self.read_pointer_int(f"{self.SAVE_BLOCK_PTR}+{base_offset:X}", 4)
        read_key = self.read_pointer_int(f"{self.SAVE_BLOCK_PTR}+{base_offset:X}", 4)
        if read_key != key:
            print(f"WARNING: {base_offset=:X} contains the key {read_key=:X} and not {key=:X}")
            print("Searching for correct block")
            direction = 1 if key > read_key else -1
            for offset in range(base_offset, base_offset + direction * 0x1000, direction * 0x20):
                read_key = self.read_pointer_int(f"{self.SAVE_BLOCK_PTR}+{offset:X}", 4)
                print(f"Testing {offset=:X}, {read_key=:X}")
                if read_key == key:
                    print(f"Found at {offset=:X}")
                    return offset, key
            raise SaveBlockError("Save block not found")
        return base_offset, key

    @staticmethod
    def _decrypt_save_block(key: int, block: bytearray) -> bytearray:
        rng = SCXorshift32(key)
        for i, byte in enumerate(block):
            block[i] = byte ^ rng.next()
        return block

    # TODO: read save blocks more like save_file_9 does
    def read_save_block_struct(self, offset: int, _struct: Type, key: int = None):
        """Read decrypted save block of bytechomp struct at offset"""
        offset, key = self._search_save_block(offset, key)
        byte_reader = bytechomp.Reader[_struct](bytechomp.ByteOrder.LITTLE).allocate()
        byte_reader.feed(self.read_save_block_object(offset, key))
        assert byte_reader.is_complete(), "Invalid data size"
        return byte_reader.build()

    def read_save_block_int(self, offset: int, key: int = None) -> int:
        """Read decrypted save block u32 at offset"""
        return int.from_bytes(self.read_save_block(offset, 5, key = key)[1:], 'little')

    def read_save_block_bool(self, offset: int, key: int = None) -> int:
        """Read decrypted save block boolean at offset"""
        return int.from_bytes(self.read_save_block(offset, 1, key = key), 'little') == 2

    def read_save_block(self, offset: int, size: int, key: int = None) -> bytearray:
        """Read decrypted save block at offset"""
        offset, key = self._search_save_block(offset, key)
        block = bytearray(self.read_pointer(f"[{self.SAVE_BLOCK_PTR}+{offset + 8:X}]", size))
        return self._decrypt_save_block(key, block)

    def read_save_block_object(self, offset: int, key: int = None) -> bytearray:
        """Read decrypted save block object at offset"""
        offset, key = self._search_save_block(offset, key)
        header = bytearray(self.read_pointer(f"[{self.SAVE_BLOCK_PTR}+{offset + 8:X}]", 5))
        header = self._decrypt_save_block(key, header)
        # discard type byte
        size = int.from_bytes(header[1:], 'little')
        full_object = bytearray(
            self.read_pointer(
                f"[{self.SAVE_BLOCK_PTR}+{offset + 8:X}]",
                5 + size
            )
        )
        # discard type and size bytes
        return self._decrypt_save_block(key, full_object)[5:]

    def read_trainer_icon(self) -> Image.Image:
        """Read trainer icon as PIL image"""
        # thanks NPO! https://github.com/NPO-197
        def build_dxt1_header(width, height):
            """Build DXT1 header"""
            return b'\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x08\x00' \
                + struct.pack("<II", height, width) \
                + b'\x00\x7E\x09\x00\x00\x00\x00\x00\x01\x00\x00\x00' \
                b'\x49\x4D\x41\x47\x45\x4D\x41\x47\x49\x43\x4B\x00' \
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00' \
                b'\x04\x00\x00\x00\x44\x58\x54\x31\x00\x00\x00\x00' \
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                b'\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00' \
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        return Image.open(
            io.BytesIO(
                build_dxt1_header(
                    self.read_save_block_int(*self.TRAINER_ICON_WIDTH_LOCATION),
                    self.read_save_block_int(*self.TRAINER_ICON_HEIGHT_LOCATION)
                ) + self.read_save_block_object(*self.TRAINER_ICON_LOCATION)
            )
        )

    def read_game_version(self) -> Game:
        """Read game version"""
        return Game.from_game_id(self.read_main_int(self.GAME_ID_OFS, 4))

    def read_raid_enemy_table_arrays(self) -> tuple[RaidEnemyTableArray, 7]:
        """Read all raid flatbuffer binaries from memory"""
        binaries = []
        for difficulty in StarLevel:
            if difficulty == StarLevel.SEVEN_STAR:
                continue
            print(f"Reading binary for {difficulty=}")
            binaries.append(
                RaidEnemyTableArray(
                    self.read_raid_binary(difficulty)
                )
            )
        print("Done reading raid binaries!")
        return tuple(binaries)

    def read_raid_block_data(self) -> RaidBlock:
        """Read raid block data from memory and process"""
        raid_block = process_raid_block(self.read_pointer(*self.RAID_BLOCK_PTR))
        raid_block.initialize_data(
            self.raid_enemy_table_arrays,
            self.raid_item_table_arrays,
            self.story_progress,
            self.game_version,
            self.my_status,
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
        with contextlib.suppress(TimeoutError):
            while self.check_if_data_avaiable():
                self.socket.recv(0x8000)

    def read(self, address: int, size: int) -> bytes:
        """Read bytes from heap"""
        if self.read_safety and not self.usb_connection:
            self.clear_all_data()
        return super().read(address, size)

    def read_absolute(self, address: int, size: int) -> bytes:
        """Read bytes from heap"""
        if self.read_safety and not self.usb_connection:
            self.clear_all_data()
        return super().read_absolute(address, size)

    def read_main(self, address: int, size: int) -> bytes:
        """Read bytes from main"""
        if self.read_safety and not self.usb_connection:
            self.clear_all_data()
        return super().read_main(address, size)

    def read_pointer(self, pointer: str, size: int) -> bytes:
        """Read bytes from pointer"""
        if self.read_safety and not self.usb_connection:
            self.clear_all_data()
        return super().read_pointer(pointer, size)
