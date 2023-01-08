"""Decrypt and read blocks from a SV save file
   https://github.com/kwsch/PKHeX/tree/master/PKHeX.Core/Saves/Encryption/SwishCrypto"""

import struct
from typing import Type
import bytechomp
from ..rng.xorshift import SCXorshift32
from ..enums.save_block import SCTypeCode
from ..enums.difficulty import StoryProgress
from ..save.my_status_9 import MyStatus9
from ..save.raid_block import RaidBlock, process_raid_block
from ..fbs.raid_enemy_table_array import RaidEnemyTableArray
from ..fbs.delivery_raid_priority_array import DeliveryRaidPriorityArray
from ..fbs.raid_fixed_reward_item_array import RaidFixedRewardItemArray
from ..fbs.raid_lottery_reward_item_array import RaidLotteryRewardItemArray

def parse_int(block_type: SCTypeCode, data: bytearray) -> int:
    """Parse bytes for integer SCTypeCodes"""
    return int.from_bytes(
        data,
        'little',
        signed = block_type.is_signed()
    )[0]

def parse_float(block_type: SCTypeCode, data: bytearray) -> float:
    """Parse bytes for float SCTypeCodes"""
    return struct.unpack(
        'f' if block_type == SCTypeCode.FLOAT else 'd',
        data
    )[0]

class SaveFile9:
    """SV save file and save block accessor"""
    STATIC_XORPAD = [
        0xA0, 0x92, 0xD1, 0x06, 0x07, 0xDB, 0x32, 0xA1, 0xAE, 0x01, 0xF5, 0xC5, 0x1E, 0x84, 0x4F,
        0xE3, 0x53, 0xCA, 0x37, 0xF4, 0xA7, 0xB0, 0x4D, 0xA0, 0x18, 0xB7, 0xC2, 0x97, 0xDA, 0x5F,
        0x53, 0x2B, 0x75, 0xFA, 0x48, 0x16, 0xF8, 0xD4, 0x8A, 0x6F, 0x61, 0x05, 0xF4, 0xE2, 0xFD,
        0x04, 0xB5, 0xA3, 0x0F, 0xFC, 0x44, 0x92, 0xCB, 0x32, 0xE6, 0x1B, 0xB9, 0xB1, 0x2E, 0x01,
        0xB0, 0x56, 0x53, 0x36, 0xD2, 0xD1, 0x50, 0x3D, 0xDE, 0x5B, 0x2E, 0x0E, 0x52, 0xFD, 0xDF,
        0x2F, 0x7B, 0xCA, 0x63, 0x50, 0xA4, 0x67, 0x5D, 0x23, 0x17, 0xC0, 0x52, 0xE1, 0xA6, 0x30,
        0x7C, 0x2B, 0xB6, 0x70, 0x36, 0x5B, 0x2A, 0x27, 0x69, 0x33, 0xF5, 0x63, 0x7B, 0x36, 0x3F,
        0x26, 0x9B, 0xA3, 0xED, 0x7A, 0x53, 0x00, 0xA4, 0x48, 0xB3, 0x50, 0x9E, 0x14, 0xA0, 0x52,
        0xDE, 0x7E, 0x10, 0x2B, 0x1B, 0x77, 0x6E,
    ]

    DIFFICULTY_FLAG_LOCATIONS = (
        0xEC95D8EF,
        0xA9428DFE,
        0x9535F471,
        0x6E7F8220,
    )
    MY_STATUS_LOCATION = 0xE3E89BD1
    BCAT_RAID_BINARY_LOCATION = 0x520A1B0
    BCAT_RAID_PRIORITY_LOCATION = 0x95451E4
    BCAT_RAID_FIXED_REWARD_LOCATION = 0x7D6C2B82
    BCAT_RAID_LOTTERY_REWARD_LOCATION = 0xA52B4811
    RAID_BLOCK_LOCATION = 0xCAAC8800

    def __init__(self, save_data: bytearray):
        self.save_data = save_data
        self.decrypt_main()

    def decrypt_main(self):
        """Decrypt main"""
        for i in range(len(self.save_data) - 0x20):
            self.save_data[i] ^= self.STATIC_XORPAD[i % len(self.STATIC_XORPAD)]

    def decrypt_bytes(self, rng: SCXorshift32, ofs: int, size: int):
        """Decrypt SCXorshift encrypted bytearray"""
        return bytearray(
            byte ^ rng.next()
            for byte in self.save_data[ofs:ofs + size]
        )

    def read_block(
        self,
        block_key: int
    ) -> bool | bytearray | int | float | list[bytearray] | list[int] | list[float]:
        """Read and decrypt save block from block_key"""
        rng = SCXorshift32(block_key)
        ofs = self.save_data.find(block_key.to_bytes(4, 'little')) + 4
        block_type = SCTypeCode(self.save_data[ofs] ^ rng.next())
        ofs += 1
        match block_type:
            case SCTypeCode.BOOL_FALSE:
                return False
            case SCTypeCode.BOOL_TRUE:
                return True
            case SCTypeCode.BOOL_ARRAY:
                raise NotImplementedError("BOOL_ARRAY is an invalid block type.")
            case SCTypeCode.OBJECT:
                return self.decrypt_bytes(
                    rng,
                    ofs + 4,
                    size = int.from_bytes(
                        self.save_data[ofs:ofs + 4],
                        'little'
                    ) ^ rng.next_32()
                )
            case SCTypeCode.ARRAY:
                arr_size = int.from_bytes(self.save_data[ofs:ofs + 4], 'little') ^ rng.next_32()
                ofs += 4
                sub_type = SCTypeCode(self.save_data[ofs] ^ rng.next())
                ofs += 1
                sub_type_size = sub_type.byte_size()
                arr = []
                for _ in range(arr_size):
                    data = self.decrypt_bytes(rng, ofs, sub_type_size)
                    match sub_type:
                        case (
                            SCTypeCode.U8
                            | SCTypeCode.U16
                            | SCTypeCode.U32
                            | SCTypeCode.I8
                            | SCTypeCode.I16
                            | SCTypeCode.I32
                        ):
                            data = parse_int(sub_type, data)
                        case SCTypeCode.FLOAT | SCTypeCode.DOUBLE:
                            data = parse_float(sub_type, data)
                    arr.append(data)
                    ofs += sub_type_size
                return arr
            case (
                SCTypeCode.U8
                | SCTypeCode.U16
                | SCTypeCode.U32
                | SCTypeCode.I8
                | SCTypeCode.I16
                | SCTypeCode.I32
            ):
                return parse_int(
                    block_type,
                    self.decrypt_bytes(
                        rng,
                        ofs,
                        block_type.byte_size()
                    )
                )
            case SCTypeCode.FLOAT | SCTypeCode.DOUBLE:
                return parse_float(
                    block_type,
                    self.decrypt_bytes(
                        rng,
                        ofs,
                        block_type.byte_size()
                    )
                )
            case _:
                raise NotImplementedError(f"{block_type:!r} is not an implemented block type.")

    def read_block_struct(self, key: int, _struct: Type):
        """Read decrypted save block as bytechomp struct"""
        byte_reader = bytechomp.Reader[_struct](bytechomp.ByteOrder.LITTLE).allocate()
        byte_reader.feed(self.read_block(key))
        assert byte_reader.is_complete(), "Invalid data size"
        return byte_reader.build()

    def read_story_progess(self) -> StoryProgress:
        """Read and decrypt story progress from save blocks"""
        progress = StoryProgress.SIX_STAR_UNLOCKED
        for key in reversed(self.DIFFICULTY_FLAG_LOCATIONS):
            if self.read_block(key):
                return StoryProgress(progress)
            progress -= 1
        return StoryProgress.DEFAULT

    def read_my_status(self) -> MyStatus9:
        """Read trainer info"""
        return self.read_block_struct(self.MY_STATUS_LOCATION, MyStatus9)

    def read_event_binary(self) -> RaidEnemyTableArray:
        """Read event binary from save"""
        return RaidEnemyTableArray(self.read_block(self.BCAT_RAID_BINARY_LOCATION))

    def read_delivery_item_binaries(
        self
    ) -> tuple[RaidFixedRewardItemArray | RaidLotteryRewardItemArray, 2]:
        """Read delivery item flatbuffer binaries from save blocks"""
        return (
            RaidFixedRewardItemArray(
                self.read_block(
                    self.BCAT_RAID_FIXED_REWARD_LOCATION
                )
            ),
            RaidLotteryRewardItemArray(
                self.read_block(
                    self.BCAT_RAID_LOTTERY_REWARD_LOCATION
                )
            ),
        )

    def read_event_priority(self) -> DeliveryRaidPriorityArray:
        """Read event priority binary from save"""
        delivery_raid_priority_array = \
            DeliveryRaidPriorityArray(self.read_block(self.BCAT_RAID_PRIORITY_LOCATION))
        if len(delivery_raid_priority_array.delivery_raid_prioritys) == 0:
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        return delivery_raid_priority_array \
            .delivery_raid_prioritys[0] \
            .delivery_group_id \
            .group_counts

    def read_raid_block(self) -> RaidBlock:
        """Read and process raid block"""
        return process_raid_block(self.read_block(self.RAID_BLOCK_LOCATION))
