"""Generic FlatBuffer object"""

from io import FileIO
from enum import IntEnum
from typing import Type, Self, Callable
import flatbuffers

# type union not yet supported by pylint
# pylint: disable=unsupported-binary-operation

U8 = flatbuffers.number_types.Uint8Flags
U16 = flatbuffers.number_types.Uint16Flags
U32 = flatbuffers.number_types.Uint32Flags
U64 = flatbuffers.number_types.Uint64Flags
I8 = flatbuffers.number_types.Int8Flags
I16 = flatbuffers.number_types.Int16Flags
I32 = flatbuffers.number_types.Int32Flags
I64 = flatbuffers.number_types.Int64Flags

INT_TYPES = (
    Type[U8]
    | Type[U16]
    | Type[U32]
    | Type[U64]
    | Type[I8]
    | Type[I16]
    | Type[I32]
    | Type[I64]
)

class FlatBufferObject:
    """Generic FlatBuffer object"""
    def __init__(self, buf: bytearray, offset: int = None):
        # offset is None implies this is a root object
        if offset is None:
            offset = flatbuffers.encode.Get(
                flatbuffers.packer.uoffset,
                buf,
                0
            )
        self._table = flatbuffers.table.Table(
            buf,
            offset
        )
        self._offset = offset
        self._counter = 4

    def dump_binary(self, stream: FileIO):
        """Dump binary to file stream"""
        stream.write(self._table.Bytes)

    def read_int(self, _type: INT_TYPES, position: int, default = None):
        """Read value of _type at position"""
        if pos_offset := self._table.Offset(position):
            return self._table.Get(_type, pos_offset + self._offset)
        return default

    def read_int_enum(
        self,
        _type: INT_TYPES,
        position: int,
        _enum: Type[IntEnum] | Callable,
        default = None
    ):
        """Read value of _type at position as _enum"""
        if pos_offset := self._table.Offset(position):
            return _enum(self._table.Get(_type, pos_offset + self._offset))
        return default

    def read_init_int(self, _type: INT_TYPES, default = None):
        """Read value of _type at the position of self._counter
           and increment the counter"""
        value = self.read_int(_type, self._counter, default = default)
        self._counter += 2
        return value

    def read_init_int_enum(self, _type: INT_TYPES, _enum: Type[IntEnum] | Callable, default = None):
        """Read value of _type at the position of self._counter as _enum
           and increment the counter"""
        value = self.read_int_enum(_type, self._counter, _enum, default = default)
        self._counter += 2
        return value

    def read_object(self, _object_type: Type[Self], position: int, default = None):
        """Read FlatBufferObject of _object_type at position"""
        if pos_offset := self._table.Offset(position):
            val_offset = self._table.Indirect(pos_offset + self._offset)
            return _object_type(
                self._table.Bytes,
                offset = val_offset
            )
        return default

    def read_init_object(self, _object_type: Type[Self], default = None):
        """Read FlatBufferObject of _object_type at the position of self._counter
           and increment the counter"""
        value = self.read_object(_object_type, self._counter, default = default)
        self._counter += 2
        return value

    def read_object_array(self, _object_type: Type[Self], position: int):
        """Read an array of FlatBufferObjects of _object_type at position"""
        array = []
        if pos_offset := self._table.Offset(position):
            array_offset = self._table.Vector(pos_offset)
            array_len = self._table.VectorLen(pos_offset)
            for array_offset in range(array_offset, array_offset + array_len * 4, 4):
                val_offset = self._table.Indirect(array_offset)
                array.append(_object_type(
                    self._table.Bytes,
                    offset = val_offset
                ))
        return array

    def read_init_object_array(self, _object_type: Type[Self]):
        """Read an array of FlatBufferObjects of _object_type at the position of self._counter
           and increment the counter"""
        array = self.read_object_array(_object_type, self._counter)
        self._counter += 2
        return array
