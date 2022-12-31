"""Array of RaidLotteryRewardItem"""

from __future__ import annotations
from ..enums import Item, RaidRewardItemCategoryType
from .flatbuffer_object import (
    U64,
    I8,
    I32,
    FlatBufferObject,
)

class RaidLotteryRewardItemArray(FlatBufferObject):
    """Array of RaidLotteryRewardItem (root object)"""
    def __init__(self, buf: bytearray):
        FlatBufferObject.__init__(self, buf)
        self.raid_lottery_reward_items: list[RaidLotteryRewardItem] = \
            self.read_init_object_array(RaidLotteryRewardItem)

    @property
    def raid_lottery_reward_item_dict(self) -> dict[int, tuple[RaidLotteryRewardItemInfo]]:
        """Grab reward item table as a dict"""
        return {
            table.table_name: table.reward_items for table in self.raid_lottery_reward_items
        }

class RaidLotteryRewardItem(FlatBufferObject):
    """Table containing RaidLotteryRewardItemInfo"""
    def __init__(self, buf: bytearray, offset: int):
        FlatBufferObject.__init__(self, buf, offset)
        self.table_name = self.read_init_int(U64)
        self.reward_item_00 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_01 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_02 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_03 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_04 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_05 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_06 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_07 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_08 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_09 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_10 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_11 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_12 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_13 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_14 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_15 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_16 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_17 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_18 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_19 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_20 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_21 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_22 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_23 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_24 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_25 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_26 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_27 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_28 = self.read_init_object(RaidLotteryRewardItemInfo)
        self.reward_item_29 = self.read_init_object(RaidLotteryRewardItemInfo)

    @property
    def reward_items(self) -> tuple[RaidLotteryRewardItemInfo]:
        """Grab the reward items in tuple form"""
        return (
            self.reward_item_00,
            self.reward_item_01,
            self.reward_item_02,
            self.reward_item_03,
            self.reward_item_04,
            self.reward_item_05,
            self.reward_item_06,
            self.reward_item_07,
            self.reward_item_08,
            self.reward_item_09,
            self.reward_item_10,
            self.reward_item_11,
            self.reward_item_12,
            self.reward_item_13,
            self.reward_item_14,
            self.reward_item_15,
            self.reward_item_16,
            self.reward_item_17,
            self.reward_item_18,
            self.reward_item_19,
            self.reward_item_20,
            self.reward_item_21,
            self.reward_item_22,
            self.reward_item_23,
            self.reward_item_24,
            self.reward_item_25,
            self.reward_item_26,
            self.reward_item_27,
            self.reward_item_28,
            self.reward_item_29,
        )

class RaidLotteryRewardItemInfo(FlatBufferObject):
    """Table describing a random raid drop item"""
    def __init__(self, buf: bytearray, offset: int):
        FlatBufferObject.__init__(self, buf, offset)
        self.category = self.read_init_int_enum(I32, RaidRewardItemCategoryType)
        self.item_id = self.read_init_int_enum(I32, Item)
        self.num = self.read_init_int(I8)
        self.rate = self.read_init_int(I32)
        self.rare_item_flag = self.read_init_int_enum(I8, bool)
