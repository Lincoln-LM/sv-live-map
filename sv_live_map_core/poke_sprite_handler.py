"""Sprite handler to grab pokemon sprites from PKHex"""

import os
import requests
from PIL import Image, ImageTk
from .sv_enums import Species

# type union not yet supported by pylint
# pylint: disable=unsupported-binary-operation

class PokeSpriteHandler:
    """Sprite handler to grab pokemon sprites from PKHex"""
    # pylint: disable=line-too-long
    SPRITE_LINK = "https://raw.githubusercontent.com/kwsch/PKHeX/master/PKHeX.Drawing.PokeSprite/Resources/img/Artwork%20Pokemon%20Sprites/a_{title}.png"
    def __init__(self, tk_image = False):
        self.tk_image = tk_image
        self.cache: dict[(Species, int, bool), Image.Image | ImageTk.PhotoImage] = {}
        if not os.path.exists("./cached_sprites/"):
            os.mkdir("./cached_sprites/")
        for file in os.listdir("./cached_sprites/"):
            title = file.split(".")[0]
            split = title.split("-")
            species = Species(int(split[0].replace("f", "")))
            form = None if "-" not in title else int(split[-1].replace("f", ""))
            female = title.endswith("f")
            img = Image.open(f"./cached_sprites/{file}")
            # convert to tk image for gui
            if self.tk_image:
                img = ImageTk.PhotoImage(img)
            self.cache[(species, form, female)] = img

    def grab_sprite(self, species: Species, form: int, female: bool) -> Image.Image:
        """Grab a sprite from cache or request"""
        if form == 0:
            form = None
        if (species, form, female) not in self.cache:
            title = f"{species}"
            if form:
                title += f"-{form}"
            if female:
                title += "f"
            self.cache[(species, form, female)] = self.request_sprite(title)

        return self.cache[(species, form, female)]

    def request_sprite(self, title: str):
        """Request a sprite from PKHex's github"""
        sprite_location = self.SPRITE_LINK.replace("{title}", title)
        req = requests.get(sprite_location, stream = True, timeout = 1.0)
        # female-specific image does not exist, try normal
        if req.status_code == 404 and title.endswith("f"):
            sprite_location = sprite_location.replace("f.png", ".png")
            req = requests.get(sprite_location, stream = True, timeout = 1.0)
        img = Image.open(req.raw)
        img.save(f"./cached_sprites/{title}.png")
        # convert to tk image for gui
        if self.tk_image:
            img = ImageTk.PhotoImage(img)
        return img
