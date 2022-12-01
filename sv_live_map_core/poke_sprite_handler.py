"""Sprite handler to grab pokemon sprites from PKHex"""

import requests
from PIL import Image, ImageTk
from .sv_enums import Species

# type union not yet supported by pylint
# pylint: disable=unsupported-binary-operation

class PokeSpriteHandler:
    """Sprite handler to grab pokemon sprites from PKHex"""
    SPRITE_LINK = "https://raw.githubusercontent.com/kwsch/PKHeX/master/PKHeX.Drawing.PokeSprite/Resources/img/Artwork%20Pokemon%20Sprites/a_{title}.png"
    def __init__(self, tk_image = False):
        self.tk_image = tk_image
        self.cache: dict[(Species, int), Image.Image | ImageTk.PhotoImage] = {}

    def grab_sprite(self, species: Species, form: int) -> Image.Image:
        """Grab a sprite from PKHex's github"""
        if (species, form) not in self.cache:
            title = f"{species}"
            if form:
                title += f"-{form}"
            sprite_location = self.SPRITE_LINK.replace("{title}", title)
            req = requests.get(sprite_location, stream = True, timeout = 5.0)
            img = Image.open(req.raw)
            # convert to tk image for gui
            if self.tk_image:
                img = ImageTk.PhotoImage(img)
            self.cache[(species, form)] = img

        return self.cache[(species, form)]
