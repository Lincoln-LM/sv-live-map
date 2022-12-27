"""Temporary testing of save reading"""

from bytechomp import Reader, ByteOrder
from sv_live_map_core.save.save_file_9 import SaveFile9
from sv_live_map_core.save.my_status_9 import MyStatus9

COORDINATE_KEY = 0x708D1511
MYSTATUS_KEY = 0xE3E89BD1

with open("./misc_hidden/main", "rb") as save_file:
    save_file = SaveFile9(bytearray(save_file.read()))


byte_reader = Reader[MyStatus9](ByteOrder.LITTLE).allocate()
byte_reader.feed(save_file.read_block(MYSTATUS_KEY))
trainer_info = byte_reader.build()

player_coords = save_file.read_block(COORDINATE_KEY)

print(trainer_info)
print(f"{player_coords=}")
