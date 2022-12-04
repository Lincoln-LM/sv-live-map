"""Sprite handler to grab pokemon sprites from PKHex"""

import requests
import os
from PIL import Image, ImageTk
from .sv_enums import Species

# type union not yet supported by pylint
# pylint: disable=unsupported-binary-operation

class PokeSpriteHandler:
    """Sprite handler to grab pokemon sprites from PKHex"""
    SPRITE_LINK = "https://raw.githubusercontent.com/kwsch/PKHeX/master/PKHeX.Drawing.PokeSprite/Resources/img/Artwork%20Pokemon%20Sprites/a_{title}.png"
    def __init__(self, tk_image = False):
        self.tk_image = tk_image
        self.cache: dict[(Species, int, bool), Image.Image | ImageTk.PhotoImage] = {}
        if not os.path.exists("./cached_sprites/"):
            os.mkdir("./cached_sprites/")
        for file in os.listdir("./cached_sprites/"):
            title = file.split(".")[0]
            split = title.split("-")
            species = Species(int(split[0]))
            if "-" not in title:
                form = None
            else:
                form = int(split[-1])
            female = title.endswith("f")
            img = Image.open(f"./cached_sprites/{file}")
            # convert to tk image for gui
            if self.tk_image:
                img = ImageTk.PhotoImage(img)
            self.cache[(species, form, female)] = img

    def grab_sprite(self, species: Species, form: int, female: bool) -> Image.Image:
        """Grab a sprite from PKHex's github"""
        if form == 0:
            form = None
        if (species, form, female) not in self.cache:
            title = f"{species}"
            if form:
                title += f"-{form}"
            if female:
                title += "f"
            sprite_location = self.SPRITE_LINK.replace("{title}", title)
            req = requests.get(sprite_location, stream = True, timeout = 5.0)
            img = Image.open(req.raw)
            img.save(f"./cached_sprites/{title}.png")
            # convert to tk image for gui
            if self.tk_image:
                img = ImageTk.PhotoImage(img)
            self.cache[(species, form, female)] = img

        return self.cache[(species, form, female)]
