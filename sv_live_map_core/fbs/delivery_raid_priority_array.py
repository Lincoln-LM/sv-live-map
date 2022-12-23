"""Array of DeliveryRaidPriority"""

from .flatbuffer_object import (
    I8,
    I32,
    FlatBufferObject,
)

class DeliveryRaidPriorityArray(FlatBufferObject):
    """Array of DeliveryRaidPriority (root object)"""
    def __init__(self, buf: bytearray):
        FlatBufferObject.__init__(self, buf)
        self.delivery_raid_prioritys: list[DeliveryRaidPriority] = \
            self.read_init_object_array(DeliveryRaidPriority)

class DeliveryRaidPriority(FlatBufferObject):
    """Data that describes the priority of event dens"""
    def __init__(self, buf: bytearray, offset: int):
        super().__init__(buf, offset)
        self.version_no: int = self.read_init_int(I32)
        self.delivery_group_id: DeliveryGroupID = self.read_init_object(DeliveryGroupID)

class DeliveryGroupID(FlatBufferObject):
    """Data that describes how many dens are in each group"""
    # pylint: disable=too-many-instance-attributes
    def __init__(self, buf: bytearray, offset: int):
        super().__init__(buf, offset)
        self.group_id_01 = self.read_init_int(I8)
        self.group_id_02 = self.read_init_int(I8)
        self.group_id_03 = self.read_init_int(I8)
        self.group_id_04 = self.read_init_int(I8)
        self.group_id_05 = self.read_init_int(I8)
        self.group_id_06 = self.read_init_int(I8)
        self.group_id_07 = self.read_init_int(I8)
        self.group_id_08 = self.read_init_int(I8)
        self.group_id_09 = self.read_init_int(I8)
        self.group_id_10 = self.read_init_int(I8)

    @property
    def group_counts(self) -> tuple[int]:
        """Grab the amount of each group in tuple form"""
        return (
            0, # padding to ensure that id == index
            self.group_id_01,
            self.group_id_02,
            self.group_id_03,
            self.group_id_04,
            self.group_id_05,
            self.group_id_06,
            self.group_id_07,
            self.group_id_08,
            self.group_id_09,
            self.group_id_10,
        )
