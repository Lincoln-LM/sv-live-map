"""customtkinter widget for displaying raid info"""

from typing import Callable
import customtkinter
from PIL import Image, ImageTk
from sv_live_map_core.raid_block import TeraRaid
from sv_live_map_core.poke_sprite_handler import PokeSpriteHandler
from sv_live_map_core.image_widget import ImageWidget
from sv_live_map_core.sv_enums import TeraType, Gender
from sv_live_map_core.path_handler import get_path

# type union not yet supported by pylint
# pylint: disable=unsupported-binary-operation

class RaidInfoWidget(customtkinter.CTkFrame):
    """customtkinter widget for displaying raid info"""
    # pylint: disable=too-many-instance-attributes, too-many-ancestors
    EMPTY_SPRITE: ImageTk.PhotoImage = None
    EVENT_SPRITE: ImageTk.PhotoImage = None
    SHINY_SPRITE: ImageTk.PhotoImage = None
    TERA_SPRITES: list[ImageTk.PhotoImage] = []

    def __init__(
        self,
        *args,
        poke_sprite_handler: PokeSpriteHandler = None,
        raid_data: TeraRaid = None,
        is_popup = True,
        focus_command: Callable = None,
        swap_command: Callable = None,
        has_alternate_location: bool = False,
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
        self.is_popup = is_popup
        self.focus_command = focus_command
        self.swap_command = swap_command

        # pylint doesnt handle nested initialization well
        self.tera_sprite: ImageTk.PhotoImage
        self.empty_sprite: ImageTk.PhotoImage
        self.event_sprite: ImageTk.PhotoImage
        self.shiny_sprite: ImageTk.PhotoImage
        self.tera_sprite_display: customtkinter.CTkButton | ImageWidget
        self.sprite_display: ImageWidget
        self.info_display: customtkinter.CTkLabel
        self.event_sprite_display: ImageWidget
        self.shiny_sprite_display: ImageWidget
        self.swap_location_button: customtkinter.CTkButton

        self.initialize_components(raid_data, has_alternate_location)

    def initialize_components(self, raid_data: TeraRaid, has_alternate_location: bool):
        """Draw all components of the widget"""
        self.poke_sprite = self.grab_poke_sprite()
        self.cache_sprites()
        self.tera_sprite = RaidInfoWidget.TERA_SPRITES[raid_data.tera_type]
        self.empty_sprite = RaidInfoWidget.EMPTY_SPRITE
        self.event_sprite = RaidInfoWidget.EVENT_SPRITE
        self.shiny_sprite = RaidInfoWidget.SHINY_SPRITE

        self.draw_main_sprites()
        self.draw_info(raid_data)
        self.draw_action_buttons(has_alternate_location)

    def draw_action_buttons(self, has_alternate_location: bool):
        """Draw swap button"""
        if not self.is_popup:
            if has_alternate_location:
                # TODO: tooltip text
                self.swap_location_button = customtkinter.CTkButton(
                    master = self,
                    text = "Swap",
                    width = 50,
                    command = self.swap_command
                )
            else:
                # padding
                self.swap_location_button = customtkinter.CTkLabel(
                    master = self,
                    text = "",
                    width = 50
                )
            self.swap_location_button.pack(side = "left", padx = (0, 15))

    def draw_info(self, raid_data: TeraRaid):
        """Draw pokemon info display"""
        self.info_display = customtkinter.CTkLabel(
            master = self,
            text = raid_data,
            text_font = (
                customtkinter.ThemeManager.theme["text"]["font"],
                8
            ),
            width = 200
        )
        self.info_display.pack(side = "left", fill = "x")
        self.draw_info_sprites(raid_data)

    def draw_info_sprites(self, raid_data: TeraRaid):
        """Draw info sprites"""
        self.event_sprite_display = ImageWidget(
            master = self,
            image = self.event_sprite if raid_data.is_event else self.empty_sprite,
            fg_color = self.fg_color
        )
        self.event_sprite_display.pack(side = "left", fill = "y", pady = (20, 0))

        self.shiny_sprite_display = ImageWidget(
            master = self,
            image = self.shiny_sprite if raid_data.is_shiny else self.empty_sprite,
            fg_color = self.fg_color
        )
        self.shiny_sprite_display.pack(side = "left", fill = "y", pady = (20, 0))

    def draw_main_sprites(self):
        """Draw tera_sprite and poke_sprite"""
        if self.is_popup:
            self.tera_sprite_display = ImageWidget(
                master = self,
                image = self.tera_sprite,
                fg_color = self.fg_color
            )
        else:
            self.tera_sprite_display = customtkinter.CTkButton(
                master = self,
                text = "",
                width = self.tera_sprite.width(),
                height = self.tera_sprite.height(),
                image = self.tera_sprite,
                command = self.focus_command,
                fg_color = self.fg_color
            )
        self.tera_sprite_display.pack(
            side = "left",
            fill = "y",
            padx = (40, 0),
            pady = (40, 0) if self.is_popup else (20, 0)
        )

        self.sprite_display = ImageWidget(
            master = self,
            image = self.poke_sprite,
            fg_color = self.fg_color
        )
        self.sprite_display.pack(
            side = "left",
            fill = "y",
            pady = (35, 0) if self.is_popup else (45, 0)
        )

    def cache_sprites(self):
        """Grab and cache sprites if not present"""
        if len(RaidInfoWidget.TERA_SPRITES) == 0:
            RaidInfoWidget.TERA_SPRITES = [
                ImageTk.PhotoImage(
                    Image.open(
                        get_path(f"./resources/gem/{tera_type.name}.png")
                    )
                )
                for tera_type in TeraType
            ]
        if RaidInfoWidget.EMPTY_SPRITE is None:
            RaidInfoWidget.EMPTY_SPRITE = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/info_icons/empty.png")
                )
            )
        if RaidInfoWidget.EVENT_SPRITE is None:
            RaidInfoWidget.EVENT_SPRITE = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/info_icons/event.png")
                )
            )
        if RaidInfoWidget.SHINY_SPRITE is None:
            RaidInfoWidget.SHINY_SPRITE = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/info_icons/shiny.png")
                )
            )

    def grab_poke_sprite(self) -> Image:
        """Grab poke_sprite from the sprite handler"""
        return self.poke_sprite_handler.grab_sprite(
            self.raid_data.species,
            self.raid_data.form,
            self.raid_data.gender == Gender.FEMALE
        )
