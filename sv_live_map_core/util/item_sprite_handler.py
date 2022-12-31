"""Sprite handler to grab item sprites"""

import os
import json
from PIL import Image, ImageTk
from ..enums import Item
from .path_handler import get_path

# type union not yet supported by pylint
# pylint: disable=unsupported-binary-operation

class ItemSpriteHandler:
    """Sprite handler to grab item sprites"""
    def __init__(self, tk_image = False):
        self.tk_image = tk_image
        self.cache: dict[Item, Image.Image | ImageTk.PhotoImage] = {}
        sprite_path = get_path("./resources/item_sprites/")
        with open(get_path("./resources/item_id_map.json"), encoding = "utf-8") as item_id_map_file:
            item_id_map = json.load(item_id_map_file)
        for file in os.listdir(sprite_path):
            title = file.split(".")[0]
            item_id = int(title)
            img = Image.open(f"{sprite_path}{file}")
            # convert to tk image for gui
            if self.tk_image:
                img = ImageTk.PhotoImage(img)
            # duplicate sprites are only stored once
            for mapped_item_id in item_id_map[str(item_id)]:
                self.cache[Item(mapped_item_id)] = img

    def grab_sprite(self, item_id: Item) -> Image.Image | ImageTk.PhotoImage:
        """Grab a sprite from cache"""
        return self.cache.get(item_id)
