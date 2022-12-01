"""customtkinter widget for displaying raid info"""

import customtkinter
from PIL import Image, ImageTk
from sv_live_map_core.raid_block import TeraRaid
from sv_live_map_core.poke_sprite_handler import PokeSpriteHandler
from sv_live_map_core.image_widget import ImageWidget
from sv_live_map_core.sv_enums import TeraType

class RaidInfoWidget(customtkinter.CTkFrame):
    """customtkinter widget for displaying raid info"""
    EMPTY_SPRITE: ImageTk.PhotoImage = None
    EVENT_SPRITE: ImageTk.PhotoImage = None
    SHINY_SPRITE: ImageTk.PhotoImage = None
    TERA_SPRITES: list[ImageTk.PhotoImage] = None

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
        if RaidInfoWidget.TERA_SPRITES is None:
            RaidInfoWidget.TERA_SPRITES = []
            for tera_type in TeraType:
                RaidInfoWidget.TERA_SPRITES.append(
                    ImageTk.PhotoImage(
                        Image.open(f"./resources/gem/{tera_type.name}.png")
                    )
                )
        self.tera_sprite = RaidInfoWidget.TERA_SPRITES[raid_data.tera_type]
        if RaidInfoWidget.EMPTY_SPRITE is None:
            RaidInfoWidget.EMPTY_SPRITE = ImageTk.PhotoImage(
                Image.open("./resources/info_icons/empty.png")
            )
        self.empty_sprite = RaidInfoWidget.EMPTY_SPRITE
        if RaidInfoWidget.EVENT_SPRITE is None:
            RaidInfoWidget.EVENT_SPRITE = ImageTk.PhotoImage(
                Image.open("./resources/info_icons/event.png")
            )
        self.event_sprite = RaidInfoWidget.EVENT_SPRITE
        if RaidInfoWidget.SHINY_SPRITE is None:
            RaidInfoWidget.SHINY_SPRITE = ImageTk.PhotoImage(
                Image.open("./resources/info_icons/shiny.png")
            )
        self.shiny_sprite = RaidInfoWidget.SHINY_SPRITE

        self.tera_sprite_display = ImageWidget(
            master = self,
            image = self.tera_sprite,
            fg_color = self.fg_color
        )
        self.tera_sprite_display.pack(side = "left", fill = "y", padx = (40, 0), pady = (20, 0))

        self.sprite_display = ImageWidget(
            master = self,
            image = self.poke_sprite,
            fg_color = self.fg_color
        )
        self.sprite_display.pack(side = "left", fill = "y", pady = (10, 0))

        species_str = self.raid_data.species.name.capitalize()
        form_str = f"-{self.raid_data.form}" if self.raid_data.form else ""
        shiny_str = "Shiny " if self.raid_data.is_shiny else ""
        event_str = "Event " if self.raid_data.is_event else ""
        star_str = "★" * (self.raid_data.difficulty + 1)
        iv_str = "/".join(map(str, self.raid_data.ivs))
        nature_str = self.raid_data.nature.name.title()
        # TODO: ability and gender enums from personalinfo
        ability_str = str(self.raid_data.ability)
        gender_str = str(self.raid_data.gender)
        tera_type_str = self.raid_data.tera_type.name.title()
        # TODO: better location names (and coords)
        location_str = f"{self.raid_data.area_id}-{self.raid_data.den_id}"
        seed_str = f"{self.raid_data.seed:08X}"
        pid_str = f"{self.raid_data.pid:08X}"
        ec_str = f"{self.raid_data.encryption_constant:08X}"
        sidtid_str = f"{self.raid_data.sidtid:08X}"
        info_str = f"{species_str}{form_str}\n" \
                   f"{shiny_str}{event_str}{star_str}\n" \
                   f"IVs: {iv_str}\n" \
                   f"Nature: {nature_str} Ability: {ability_str} Gender: {gender_str}\n" \
                   f"Tera Type: {tera_type_str}\n" \
                   f"Location: {location_str}\n" \
                   f"Seed: {seed_str} EC: {ec_str}\n" \
                   f"PID: {pid_str} SIDTID: {sidtid_str}\n"

        self.info_display = customtkinter.CTkLabel(
            master = self,
            text = info_str,
            text_font = (
                customtkinter.ThemeManager.theme["text"]["font"],
                8
            ),
            width = 200
        )
        self.info_display.pack(side = "left", fill = "x")
        if raid_data.is_event:
            self.event_sprite_display = ImageWidget(
                master = self,
                image = self.event_sprite,
                fg_color = self.fg_color
            )
        else:
            self.event_sprite_display = ImageWidget(
                master = self,
                image = self.empty_sprite,
                fg_color = self.fg_color
            )
        self.event_sprite_display.pack(side = "left", fill = "y", pady = (20, 0))

        if raid_data.is_shiny:
            self.shiny_sprite_display = ImageWidget(
                master = self,
                image = self.shiny_sprite,
                fg_color = self.fg_color
            )
        else:
            self.shiny_sprite_display = ImageWidget(
                master = self,
                image = self.empty_sprite,
                fg_color = self.fg_color
            )
        self.shiny_sprite_display.pack(side = "left", fill = "y", pady = (20, 0))
