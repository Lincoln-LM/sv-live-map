"""Sprite handler to grab pokemon sprites"""

import os
from PIL import Image, ImageTk
from ..enums import Species
from .path_handler import get_path

# type union not yet supported by pylint
# pylint: disable=unsupported-binary-operation


class PokeSpriteHandler:
    """Sprite handler to grab pokemon sprites"""

    def __init__(self, tk_image: bool = False):
        self.tk_image = tk_image
        self.cache: dict[(Species, int, bool), Image.Image | ImageTk.PhotoImage] = {}
        sprite_path = get_path("./resources/sprites/")
        for file in os.listdir(sprite_path):
            title = file.split(".")[0]
            split = title.split("-")
            species = Species(int(split[0].replace("f", "")))
            form = None if "-" not in title else int(split[-1].replace("f", ""))
            female = title.endswith("f")
            img = Image.open(f"{sprite_path}{file}")
            # convert to tk image for gui
            if self.tk_image:
                img = ImageTk.PhotoImage(img)
            self.cache[(species, form, female)] = img

    def grab_sprite(
        self, species: Species, form: int, female: bool
    ) -> Image.Image | ImageTk.PhotoImage:
        """Grab a sprite from cache"""
        if form == 0:
            form = None
        return self.cache.get(
            (species, form, female), self.cache.get((species, form, False), None)
        )
