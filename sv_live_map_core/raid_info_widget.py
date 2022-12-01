"""customtkinter widget for displaying raid info"""

import customtkinter
from PIL import Image, ImageTk
from sv_live_map_core.raid_block import TeraRaid
from sv_live_map_core.poke_sprite_handler import PokeSpriteHandler
from sv_live_map_core.image_widget import ImageWidget

class RaidInfoWidget(customtkinter.CTkFrame):
    """customtkinter widget for displaying raid info"""
    def __init__(
        self,
        *args,
        poke_sprite_handler: PokeSpriteHandler = None,
        raid_data: TeraRaid = None,
        width: int = 200,
        height: int = 200,
        **kwargs
    ):
        super().__init__(
            *args,
            width = width,
            height = height,
            **kwargs
        )
        assert poke_sprite_handler is not None
        assert raid_data is not None

        self.poke_sprite_handler = poke_sprite_handler
        self.raid_data = raid_data

        self.poke_sprite = \
            self.poke_sprite_handler.grab_sprite(self.raid_data.species, self.raid_data.form)
        self.tera_sprite = ImageTk.PhotoImage(
            Image.open(f"./resources/gem/{self.raid_data.tera_type.name}.png")
        )

        self.tera_sprite_display = ImageWidget(master = self, image = self.tera_sprite)
        self.tera_sprite_display.pack(side = "left", fill = "y")

        self.sprite_display = ImageWidget(master = self, image = self.poke_sprite)
        self.sprite_display.pack(side = "left", fill = "y")

        self.info_display = customtkinter.CTkEntry(master = self)
        self.info_display.pack(side = "right", fill = "both")
        self.info_display.insert(0, self.raid_data.species.name)
