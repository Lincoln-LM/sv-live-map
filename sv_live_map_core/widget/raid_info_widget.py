"""customtkinter widget for displaying raid info"""

from typing import Callable
from tkinter import filedialog
import os
import customtkinter
from PIL import Image, ImageTk, ImageDraw, ImageFont
from ..save.raid_block import TeraRaid
from ..util.poke_sprite_handler import PokeSpriteHandler
from ..util.item_sprite_handler import ItemSpriteHandler
from .image_widget import ImageWidget
from ..enums import TeraType, Gender, StarLevel
from ..util.path_handler import get_path
from ..window.reward_window import RewardWindow

# type union not yet supported by pylint
# pylint: disable=unsupported-binary-operation

class RaidInfoWidget(customtkinter.CTkFrame):
    """customtkinter widget for displaying raid info"""
    # pylint: disable=too-many-instance-attributes, too-many-ancestors
    STAR_UNDERLAY: ImageTk.PhotoImage = None
    EVENT_UNDERLAY: ImageTk.PhotoImage = None
    SHINY_OVERLAY: ImageTk.PhotoImage = None
    COPY_IMAGE: ImageTk.PhotoImage = None
    BAG_IMAGE: ImageTk.PhotoImage = None
    CAMERA_IMAGE: ImageTk.PhotoImage = None
    TERA_SPRITES: list[ImageTk.PhotoImage] = []
    TERA_6_SPRITES: list[ImageTk.PhotoImage] = []
    SEPARATOR_COLOR = "#949392"

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
        hide_sensitive_info: bool = False,
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

        self.raid_data = raid_data
        self.raid_data.hide_sensitive_info = hide_sensitive_info

        self.poke_sprite_handler = poke_sprite_handler
        self.is_popup = is_popup
        self.focus_command = focus_command
        self.swap_command = swap_command

        # pylint doesnt handle nested initialization well
        self.tera_sprite: ImageTk.PhotoImage
        self.tera_sprite_display: customtkinter.CTkButton | ImageWidget
        self.sprite_display: ImageWidget
        self.info_display: customtkinter.CTkLabel
        self.swap_location_button: customtkinter.CTkButton
        self.raid_reward_button: customtkinter.CTkButton
        self.copy_info_button: customtkinter.CTkButton
        self.save_image_button: customtkinter.CTkButton
        self.horizontal_sep: customtkinter.CTkFrame

        self.initialize_components(raid_data, has_alternate_location)

    def initialize_components(self, raid_data: TeraRaid, has_alternate_location: bool):
        """Draw all components of the widget"""
        self.cache_sprites()
        self.poke_sprite = self.grab_poke_sprite()
        self.tera_sprite = self.grab_tera_sprite(raid_data)

        if not self.is_popup:
            self.draw_horizontal_separator()
        self.draw_main_sprites()
        self.draw_info(raid_data)
        self.draw_action_buttons(has_alternate_location)

    def draw_horizontal_separator(self):
        """Draw horizontal separator"""
        self.horizontal_sep = \
            customtkinter.CTkFrame(
                self,
                bg_color = self.SEPARATOR_COLOR,
                fg_color = customtkinter.ThemeManager.theme["color"]["frame_low"],
                width = 500,
                height = 5,
                bd = 0
            )
        self.horizontal_sep.pack(
            side = "top",
            fill = "x",
            pady = (0, 6)
        )
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
        self.raid_reward_button = customtkinter.CTkButton(
            master = self,
            text = "",
            width = self.BAG_IMAGE.width(),
            height = self.BAG_IMAGE.height(),
            image = self.BAG_IMAGE,
            command = self.open_raid_rewards,
            fg_color = self.fg_color
        )
        self.raid_reward_button.pack(side = "left", padx = (0, 15), fill = "y")
        self.copy_info_button = customtkinter.CTkButton(
            master = self,
            text = "",
            width = self.COPY_IMAGE.width(),
            height = self.COPY_IMAGE.height(),
            image = self.COPY_IMAGE,
            command = self.copy_info,
            fg_color = self.fg_color
        )
        self.copy_info_button.pack(side = "left", padx = (0, 15), fill = "y")
        self.save_image_button = customtkinter.CTkButton(
            master = self,
            text = "",
            width = self.CAMERA_IMAGE.width(),
            height = self.CAMERA_IMAGE.height(),
            image = self.CAMERA_IMAGE,
            command = self.save_image,
            fg_color = self.fg_color
        )
        # bind middle click to save w/ items
        self.save_image_button.bind(
            '<Enter>',
            lambda _: self.save_image_button.bind_all(
                "<Button-2>",
                lambda _: self.save_image(
                    include_rewards = True
                )
            )
        )
        self.save_image_button.bind(
            '<Leave>',
            lambda _: self.save_image_button.unbind_all("<Button-2>")
        )
        self.save_image_button.pack(side = "left", padx = (0, 15), fill = "y")

    def open_raid_rewards(self):
        """Open raid reward display"""
        reward_window = RewardWindow(raid_data = self.raid_data, fg_color = self.fg_color)
        reward_window.focus_force()

    def save_image(self, include_rewards: bool = False):
        """Save image to file"""
        if not os.path.exists(get_path("./found_screenshots/")):
            os.mkdir(get_path("./found_screenshots/"))
        filename = filedialog.asksaveasfilename(
            filetypes = (("PNG File", "*.png"),),
            initialdir = get_path("./found_screenshots/")
        )
        if not filename:
            return
        if not filename.endswith(".png"):
            filename = f"{filename}.png"
        self.create_image(include_rewards = include_rewards).save(filename)

    def create_image(self, include_rewards = False) -> Image.Image:
        """Create image representation of widget"""
        size = (
            self.winfo_width()
            # exclude buttons
             - (
                 self.copy_info_button.winfo_width()
                 + self.save_image_button.winfo_width()
                 + self.raid_reward_button.winfo_width()
                 + (0 if self.is_popup else self.swap_location_button.winfo_width())
               ),
            self.winfo_height() + (len(self.raid_data.rewards) * 21 + 5 if include_rewards else 0)
        )
        bbox = (0, 0) + size
        img = Image.new("RGBA", size = size)
        img_draw = ImageDraw.Draw(img)
        img_draw.rectangle(bbox, fill = self.fg_color[1])
        tera_sprite = ImageTk.getimage(self.tera_sprite)
        poke_sprite = ImageTk.getimage(self.poke_sprite)
        img.paste(
            tera_sprite,
            (
                self.tera_sprite_display.winfo_x(),
                (self.winfo_height() - self.tera_sprite.height()) // 2
            ),
            tera_sprite
        )
        img.paste(
            poke_sprite,
            (
                self.sprite_display.winfo_x(),
                (self.winfo_height() - self.poke_sprite.height()) // 2
            ),
            poke_sprite
        )
        font = ImageFont.truetype(get_path("./resources/fonts/Inter/static/Inter-Regular.ttf"), 10)
        img_draw.text(
            (
                self.info_display.text_label.winfo_x() + self.info_display.winfo_x(),
                (self.winfo_height() - self.info_display.winfo_height()) // 2
            ),
            self.info_display.text_label['text'],
            font = font,
            align = 'center'
        )
        if include_rewards:
            if RewardWindow.ITEM_SPRITE_HANDLER is None:
                RewardWindow.ITEM_SPRITE_HANDLER = ItemSpriteHandler(True)

            for i, reward in enumerate(self.raid_data.rewards):
                tk_sprite = RewardWindow.ITEM_SPRITE_HANDLER.grab_sprite(reward[0])
                sprite = ImageTk.getimage(tk_sprite)
                img.paste(
                    sprite,
                    (
                        5,
                        self.winfo_height() + i * 21 - 8
                    ),
                    sprite
                )
                img_draw.text(
                    (
                        5 + 37,
                        self.winfo_height() + i * 21
                    ),
                    f"{reward[1]}x {reward[0]}",
                    font = font,
                    align = 'center'
                )
                img_draw.text(
                    (
                        5 + 37 + 200,
                        self.winfo_height() + i * 21
                    ),
                    f"{reward[2]:img}",
                    font = font,
                    align = 'center'
                )
                img_draw.text(
                    (
                        5 + 37 + 300,
                        self.winfo_height() + i * 21
                    ),
                    f"{reward[3]:img}",
                    font = font,
                    align = 'center'
                )
        return img

    def copy_info(self):
        """Copy info to clipboard"""
        self.master.clipboard_clear()
        self.master.clipboard_append(self.raid_data)

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
        self.info_display.pack(side = "left", fill = "x", pady = (13, 0))

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
            padx = (40, 0)
        )

        self.sprite_display = ImageWidget(
            master = self,
            image = self.poke_sprite,
            fg_color = self.fg_color
        )
        self.sprite_display.pack(
            side = "left",
            fill = "y"
        )
        self.update_padding()

    def update_padding(self):
        """Update padding on ImageWidgets based on hide_sensitive_info"""
        self.tera_sprite_display.pack_configure(
            pady = (36 if self.raid_data.hide_sensitive_info else 49, 0) if self.is_popup
            else (2 if self.raid_data.hide_sensitive_info else 6, 0)
        )
        self.sprite_display.pack_configure(
            pady = (29 if self.raid_data.hide_sensitive_info else 42, 0) if self.is_popup
            else (27 if self.raid_data.hide_sensitive_info else 40, 0)
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
        if len(RaidInfoWidget.TERA_6_SPRITES) == 0:
            RaidInfoWidget.TERA_6_SPRITES = [
                ImageTk.PhotoImage(
                    Image.open(
                        get_path(f"./resources/gem_6/{tera_type.name}.png")
                    )
                )
                for tera_type in TeraType
            ]
        if RaidInfoWidget.SHINY_OVERLAY is None:
            RaidInfoWidget.SHINY_OVERLAY = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/overlay/shiny.png")
                )
            )
        if RaidInfoWidget.EVENT_UNDERLAY is None:
            RaidInfoWidget.EVENT_UNDERLAY = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/overlay/event.png")
                )
            )
        if RaidInfoWidget.STAR_UNDERLAY is None:
            RaidInfoWidget.STAR_UNDERLAY = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/overlay/star.png")
                )
            )
        if RaidInfoWidget.COPY_IMAGE is None:
            RaidInfoWidget.COPY_IMAGE = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/icons8/clipboard.png")
                )
            )
        if RaidInfoWidget.CAMERA_IMAGE is None:
            RaidInfoWidget.CAMERA_IMAGE = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/icons8/camera.png")
                )
            )
        if RaidInfoWidget.BAG_IMAGE is None:
            RaidInfoWidget.BAG_IMAGE = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/icons8/bag.png")
                )
            )

    def grab_tera_sprite(self, raid_data):
        """Grab tera_sprite from cache"""
        underlay = None
        if self.raid_data.difficulty < StarLevel.SIX_STAR:
            sprite = RaidInfoWidget.TERA_SPRITES[raid_data.tera_type]
        else:
            sprite = RaidInfoWidget.TERA_6_SPRITES[raid_data.tera_type]
            underlay = ImageTk.getimage(self.STAR_UNDERLAY)
        if self.raid_data.is_event:
            underlay = underlay or ImageTk.getimage(self.EVENT_UNDERLAY)
        if underlay:
            basic_sprite: Image = ImageTk.getimage(sprite)
            basic_sprite = basic_sprite.resize((basic_sprite.height - 4, basic_sprite.width - 4))
            underlay.paste(im = basic_sprite, box = (2, 2), mask = basic_sprite)
            sprite = ImageTk.PhotoImage(underlay)
        return sprite

    def grab_poke_sprite(self) -> Image.Image:
        """Grab poke_sprite from the sprite handler"""
        sprite = self.poke_sprite_handler.grab_sprite(
            self.raid_data.species,
            self.raid_data.form,
            self.raid_data.gender == Gender.FEMALE
        )
        if self.raid_data.is_shiny:
            basic_sprite: Image = ImageTk.getimage(sprite)
            shiny_overlay = ImageTk.getimage(self.SHINY_OVERLAY)
            basic_sprite.paste(im = shiny_overlay, box = (0, 0), mask = shiny_overlay)
            sprite = ImageTk.PhotoImage(basic_sprite)
        return sprite
