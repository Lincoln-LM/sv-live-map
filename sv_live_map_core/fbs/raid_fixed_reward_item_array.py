"""Array of RaidFixedRewardItem"""

from __future__ import annotations
from ..enums import Item, RaidRewardItemSubjectType, RaidRewardItemCategoryType
from .flatbuffer_object import (
    U64,
    I8,
    I32,
    FlatBufferObject,
)

class RaidFixedRewardItemArray(FlatBufferObject):
    """Array of RaidFixedRewardItem (root object)"""
    def __init__(self, buf: bytearray):
        FlatBufferObject.__init__(self, buf)
        self.raid_fixed_reward_items: list[RaidFixedRewardItem] = \
            self.read_init_object_array(RaidFixedRewardItem)

    @property
    def raid_fixed_reward_item_dict(self) -> dict[int, tuple[RaidFixedRewardItemInfo]]:
        """Grab reward item table as a dict"""
        return {
            table.table_name: table.reward_items for table in self.raid_fixed_reward_items
        }

class RaidFixedRewardItem(FlatBufferObject):
    """Table containing RaidFixedRewardItemInfo"""
    def __init__(self, buf: bytearray, offset: int):
        FlatBufferObject.__init__(self, buf, offset)
        self.table_name = self.read_init_int(U64)
        self.reward_item_00 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_01 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_02 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_03 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_04 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_05 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_06 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_07 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_08 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_09 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_10 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_11 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_12 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_13 = self.read_init_object(RaidFixedRewardItemInfo)
        self.reward_item_14 = self.read_init_object(RaidFixedRewardItemInfo)

    @property
    def reward_items(self) -> tuple[RaidFixedRewardItemInfo]:
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
        )

class RaidFixedRewardItemInfo(FlatBufferObject):
    """Table describing a guaranteed raid drop item"""
    def __init__(self, buf: bytearray, offset: int):
        FlatBufferObject.__init__(self, buf, offset)
        self.category = self.read_init_int_enum(I32, RaidRewardItemCategoryType)
        self.subject_type = self.read_init_int_enum(I32, RaidRewardItemSubjectType)
        self.item_id = self.read_init_int_enum(I32, Item)
        self.num = self.read_init_int(I8)
