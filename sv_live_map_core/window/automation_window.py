"""Automation window"""

from __future__ import annotations
import sys
import os
import io
import time
from tkinter import filedialog
from threading import Thread
from typing import TYPE_CHECKING
import json
import struct
import binascii
import contextlib
import tkinter
from PIL import ImageTk, Image
import customtkinter
import discord_webhook
from ..widget.raid_info_widget import RaidInfoWidget
from ..util.raid_filter import RaidFilter
from ..widget.iv_filter_widget import IVFilterWidget
from ..enums import Nature, AbilityIndex, Gender, Species, StarLevel, Item
from ..widget.checked_combobox import CheckedCombobox
from ..widget.listviewcombobox import ListViewCombobox
from ..widget.spinbox import Spinbox
from ..util.path_handler import get_path
from ..nxreader.nxreader import SocketError

if TYPE_CHECKING:
    from typing import Type, Callable
    from .application import Application
    from ..save.raid_block import TeraRaid, RaidBlock

class AutomationWindow(customtkinter.CTkToplevel):
    """Automation window"""
    SAVE_IMAGE: ImageTk.PhotoImage = None
    LOAD_IMAGE: ImageTk.PhotoImage = None
    def __init__(
        self,
        *args,
        settings: dict = None,
        master: Application = None,
        fg_color="default_theme",
        **kwargs
    ):
        self.settings: dict = settings or {}
        super().__init__(*args, master = master, fg_color=fg_color, **kwargs)
        self.master: Application

        self.target_found = False
        self.automation_thread: Thread = None
        self.update_check = None

        self.title("Automation Settings")
        self.handle_close_events()
        self.cache_images()
        self.draw_filter_frame()
        self.draw_settings_frame()
        self.draw_start_button_frame()
        self.parse_settings()

    def cache_images(self):
        """Cache GUI images"""
        if AutomationWindow.SAVE_IMAGE is None:
            AutomationWindow.SAVE_IMAGE = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/icons8/save.png")
                )
            )
        if AutomationWindow.LOAD_IMAGE is None:
            AutomationWindow.LOAD_IMAGE = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/icons8/load.png")
                )
            )

    def send_webhook_log(self, log_message: str):
        """Send simple string log to webhook if applicable"""
        if self.webhook_check.get():
            webhook = discord_webhook.webhook.DiscordWebhook(
                url = self.webhook_entry.get(),
                content = log_message
            )
            webhook.execute()

    def start_automation(self):
        """Start automation"""
        self.send_webhook_log("Automation Starting.")
        self.target_found = False
        self.start_button.configure(require_redraw = True, text = "Stop Automation")
        self.start_button.configure(command = self.stop_automation)
        self.automation_thread = Thread(target = self.automation_work)
        self.automation_thread.start()
        self.update_check = self.after(1000, self.check_on_automation)

    def stop_automation(self):
        """Stop automation"""
        self.send_webhook_log("Automation Ending.")
        if self.automation_thread:
            self.target_found = True
            self.automation_thread = None
            self.after_cancel(self.update_check)
            self.update_check = None
            self.start_button.configure(require_redraw = True, text = "Start Automation")
            self.start_button.configure(command = self.start_automation)
            if self.master.reader:
                self.master.reader.detach()

    def automation_work(self):
        """Work for automation"""
        total_raid_count = 0
        total_reset_count = 0
        last_seed = None
        try:
            while not self.target_found:
                if self.master.reader:
                    total_raid_count, total_reset_count, last_seed, raid_block = \
                        self.read_raids(total_raid_count, total_reset_count, last_seed)

                    popup_display_builder, webhook_display_builder = self.define_builders()

                    self.filter_raids(raid_block, popup_display_builder, webhook_display_builder)

                    if self.target_found:
                        break

                    self.full_dateskip(check_target_found = True)
                else:
                    self.master.connection_error("Not connected to switch.")
                    self.target_found = True
        except (TimeoutError, struct.error, binascii.Error, SocketError) as error:
            self.stop_automation()
            self.send_webhook_log(f"Exception: <@{self.exception_ping_entry.get()}> ``{error}``")
            raise error
        self.target_found = True
        sys.exit()

    def read_raids(
        self,
        total_raid_count: int,
        total_reset_count: int,
        last_seed: int
    ) -> tuple[int, int, int, RaidBlock]:
        """Read and parse raids"""
        raid_block = self.master.read_all_raids(self.map_render_check.get())
        if raid_block.current_seed != last_seed:
            last_seed = raid_block.current_seed
            total_reset_count += 1
            total_raid_count += 69
        else:
            print("WARNING raid seed is a duplicate of the previous day")
        print(
            f"RAIDS PROCESSED {total_reset_count=} "
            f"{total_raid_count=} "
            f"{raid_block.current_seed=:X}"
        )
        # wait until rendering is done
        while self.master.render_thread is not None:
            self.master.reader.pause(0.2)
        return total_raid_count, total_reset_count, last_seed, raid_block

    def define_builders(self) -> tuple[Callable, Callable]:
        """Define popup and webhook display builders"""
        # popup display of marker info for alerts
        def popup_display_builder(
            raid: TeraRaid,
            _ = None
        ) -> tuple[customtkinter.CTkToplevel, Type[customtkinter.CTkBaseClass]]:
            return self.master.widget_message_window(
                f"Shiny {raid.species} ★"
                if raid.is_shiny else str(raid.species),
                RaidInfoWidget,
                poke_sprite_handler = self.master.sprite_handler,
                raid_data = raid,
                hide_sensitive_info = self.master.hide_info_check.get(),
                fg_color = customtkinter.ThemeManager.theme["color"]["frame_low"],
            )

        # webhook display of info
        def webhook_display_builder(raid: TeraRaid, _ = None):
            if self.embed_select.get():
                webhook = discord_webhook.webhook.DiscordWebhook(
                    url = self.webhook_entry.get(),
                    content = f"<@{self.raid_found_ping_entry.get()}>"
                )
                embed = discord_webhook.webhook.DiscordEmbed(
                    title = f"Shiny {raid.species} ★"
                        if raid.is_shiny else str(raid.species),
                    color = 0xF8C8DC
                )
                embed.set_image("attachment://poke.png")
                embed.set_author(
                    f"{raid.tera_type} Tera Type",
                    icon_url = "attachment://tera.png"
                )
                dummy_widget = RaidInfoWidget(
                    poke_sprite_handler = self.master.sprite_handler,
                    raid_data = raid,
                    hide_sensitive_info = self.master.hide_info_check.get(),
                )

                poke_sprite_img: Image = ImageTk.getimage(dummy_widget.poke_sprite)
                with io.BytesIO() as poke_sprite_bytes:
                    poke_sprite_img.save(poke_sprite_bytes, format = "PNG")
                    webhook.add_file(
                        poke_sprite_bytes.getvalue(),
                        "poke.png"
                    )

                tera_sprite_img: Image = ImageTk.getimage(dummy_widget.tera_sprite)
                with io.BytesIO() as tera_sprite_bytes:
                    tera_sprite_img.save(tera_sprite_bytes, format = "PNG")
                    webhook.add_file(
                        tera_sprite_bytes.getvalue(),
                        "tera.png"
                    )
                embed.add_embed_field("Info", str(dummy_widget.info_display.text))
                if self.include_rewards_check.get():
                    item_embed = discord_webhook.webhook.DiscordEmbed(
                        title = f"{raid.species} Items",
                        color = 0xF8C8DC
                    )
                    item_embed.add_embed_field(
                        "Items",
                        "\n".join(
                            f"{reward[1]}x {reward[0]}" for reward in raid.rewards
                        )
                    )

                webhook.add_embed(embed)
                if self.include_rewards_check.get():
                    webhook.add_embed(item_embed)
                webhook.execute()
            else:
                popup_window, widget = popup_display_builder(raid)
                time.sleep(1)
                widget: RaidInfoWidget
                img = widget.create_image(self.include_rewards_check.get())
                # unsure why this happens even when window is properly destroyed
                with contextlib.suppress(tkinter.TclError):
                    popup_window.destroy()
                if not os.path.exists(get_path("./found_screenshots/")):
                    os.mkdir(get_path("./found_screenshots/"))
                img.save(get_path(f"./found_screenshots/{raid.seed}.png"))
                with open(get_path(f"./found_screenshots/{raid.seed}.png"), "rb") as img:
                    webhook = discord_webhook.webhook.DiscordWebhook(
                        url = self.webhook_entry.get(),
                        content = f"<@{self.raid_found_ping_entry.get()}>"
                    )
                    webhook.add_file(img.read(), "img.png")
                    webhook.execute()
        return popup_display_builder, webhook_display_builder

    def filter_raids(
        self,
        raid_block: RaidBlock,
        popup_display_builder: Callable,
        webhook_display_builder: Callable
    ):
        """Filter through all raids"""
        raid_filter = self.build_filter()

        for raid in raid_block.raids:
            if not raid.is_enabled:
                continue

            matches_filters = raid_filter.compare(raid)
            self.target_found |= matches_filters

            self.handle_displays(
                popup_display_builder,
                webhook_display_builder,
                raid,
                matches_filters
            )
        # render map if target found
        if self.target_found:
            self.master.read_all_raids(True)
            # wait until rendering is done
            while self.master.render_thread is not None:
                self.master.reader.pause(0.2)

    def build_filter(self) -> RaidFilter:
        """Build RaidFilter"""
        return RaidFilter(
            hp_filter = self.hp_filter.get(),
            atk_filter = self.atk_filter.get(),
            def_filter = self.def_filter.get(),
            spa_filter = self.spa_filter.get(),
            spd_filter = self.spd_filter.get(),
            spe_filter = self.spe_filter.get(),
            ability_filter = self.ability_filter.get(),
            gender_filter = self.gender_filter.get(),
            nature_filter = self.nature_filter.get(),
            species_filter = self.species_filter.get(),
            shiny_filter = self.shiny_filter.get(),
            star_filter = self.difficulty_filter.get(),
            reward_filter = self.reward_filter.get(),
            reward_count_filter = self.reward_count_filter.get(),
        )

    def handle_displays(
        self,
        popup_display_builder: Callable,
        webhook_display_builder: Callable,
        raid: TeraRaid,
        matches_filters: bool
    ):
        """Handle popup and webhooks"""
        if matches_filters:
            if self.popup_check.get():
                popup_display_builder(raid)
            if self.webhook_check.get():
                webhook_display_builder(raid)

    def full_dateskip(self, check_target_found = False):
        """Full process of dateskipping w/checks for target_found"""
        self.leave_to_home()
        if check_target_found and self.target_found:
            return
        self.open_settings()
        if check_target_found and self.target_found:
            return
        self.open_datetime()
        if check_target_found and self.target_found:
            return
        self.skip_date()
        if check_target_found and self.target_found:
            return
        self.reopen_game()

    def reopen_game(self):
        """Reopen game from datetime menu"""
        # go back to game
        self.master.reader.manual_click("HOME")
        self.master.reader.pause(0.8)
        self.master.reader.manual_click("HOME")
        self.master.reader.pause(3 if self.master.reader.usb_connection else 5)

    def skip_date(self):
        """Skip date with touch screen"""
        # deselect month (day for non-america) (neccesary for skip to be registered)
        self.master.reader.touch_hold(151, 470, 50)
        self.master.reader.pause(0.2)
        # confirm date
        self.master.reader.touch_hold(1102, 470, 50)
        self.master.reader.pause(0.2)

    def open_datetime(self):
        """Scroll down and open the date change menu"""
        # scroll down to System
        self.master.reader.manual_click("DDOWN", 2.5, 3)
        self.master.reader.manual_click("A")
        # scroll down to datetime
        if self.safe_mode_check.get():
            # https://github.com/LegoFigure11/RaidCrawler/blob/cc9e9176bfcfc1cbc22c6f8c9d6ebaaad78ddc05/Properties/Settings.settings#L32
            for _ in range(38):
                self.master.reader.manual_click("DDOWN", 0.1)
            self.master.reader.pause(0.2)
        else:
            # this is not fully consistent but will not break execution
            self.master.reader.manual_click(
                "DDOWN",
                0.7 if self.master.reader.usb_connection else 0.825
            )
        self.master.reader.manual_click("A")
        self.master.reader.pause(0.4)
        # select Date and Time
        self.master.reader.touch_hold(1006, 386, 50)
        self.master.reader.pause(0.2)

    def open_settings(self):
        """Open settings with touch screen"""
        # select settings icon -> open settings + a third press to be safe
        # touch screen is much faster than dpad
        for _ in range(3):
            self.master.reader.touch_hold(845, 545, 50)
        self.master.reader.pause(0.5 if self.master.reader.usb_connection else 1.5)

    def leave_to_home(self):
        """Leave the game to the home menu"""
        # home button struggles to be recognized
        # this is why zoom must be disabled
        for _ in range(3):
            self.master.reader.click("HOME")
        self.master.reader.pause(1)

    def check_on_automation(self):
        """Check on the progress of automation"""
        if not self.target_found:
            self.after(1000, self.check_on_automation)
        else:
            print("Automation ending.")
            self.stop_automation()

    def draw_start_button_frame(self):
        """Draw start button frame"""
        self.start_button_frame = customtkinter.CTkFrame(master = self, width = 850)
        self.start_button_frame.grid(row = 1, column = 0, columnspan = 4, sticky = "nwse")
        self.start_button = customtkinter.CTkButton(
            master = self.start_button_frame,
            text = "Start Automation",
            width = 850,
            command = self.start_automation
        )
        self.start_button.grid(
            row = 0,
            column = 0,
            columnspan = 4,
            sticky = "nwse",
            padx = 5,
            pady = 0
        )
        self.advance_date_button = customtkinter.CTkButton(
            master = self.start_button_frame,
            text = "Advance Date",
            width = 850,
            command = self.full_dateskip
        )
        self.advance_date_button.grid(
            row = 2,
            column = 0,
            columnspan = 4,
            sticky = "nwse",
            padx = 5,
            pady = 5
        )

    def handle_close_events(self):
        """Handle close events"""
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)

    def on_closing(self):
        """Handle closing of the window"""
        # save settings
        self.master.settings['Automation'] = {
            'SafeMode': self.safe_mode_check.get(),
            'MapRender': self.map_render_check.get(),
            'Popup': self.popup_check.get(),
            'Webhook': self.webhook_check.get(),
            'Embed': self.embed_select.get(),
            'WebhookUrl': self.webhook_entry.get(),
            'PingId': self.raid_found_ping_entry.get(),
            'ExceptionPingId': self.exception_ping_entry.get(),
            'IncludeRewards': self.include_rewards_check.get(),
        }

        # TODO: make this less hacky
        self.master.automation_window = None

        self.destroy()

    def toggle_webhook_settings(self):
        """Toggle webhook settings on and off"""
        new_state = 'normal' if self.webhook_check.get() else 'disabled'
        self.widget_label.configure(require_redraw = True, state = new_state)
        self.embed_select.configure(require_redraw = True, state = new_state)
        self.webhook_entry_label.configure(require_redraw = True, state = new_state)
        self.webhook_entry.configure(require_redraw = True, state = new_state)
        self.raid_found_ping_entry_label.configure(require_redraw = True, state = new_state)
        self.raid_found_ping_entry.configure(require_redraw = True, state = new_state)
        self.exception_ping_entry_label.configure(require_redraw = True, state = new_state)
        self.exception_ping_entry.configure(require_redraw = True, state = new_state)
        self.include_rewards_check.configure(require_redraw = True, state = new_state)

    def parse_settings(self):
        """Load settings"""
        automation_settings: dict = self.settings.setdefault('Automation', {})
        self.safe_mode_check.check_state = bool(automation_settings.get('SafeMode', False))
        self.map_render_check.check_state = bool(automation_settings.get('MapRender', False))
        self.popup_check.check_state = bool(automation_settings.get('Popup', False))
        self.webhook_check.check_state = bool(automation_settings.get('Webhook', False))
        self.embed_select.check_state = bool(automation_settings.get('Embed', False))
        self.webhook_entry.insert(0, automation_settings.get('WebhookUrl', ''))
        self.raid_found_ping_entry.insert(0, automation_settings.get('PingId', ''))
        self.exception_ping_entry.insert(0, automation_settings.get('ExceptionPingId', ''))
        self.include_rewards_check.check_state = \
            bool(automation_settings.get('IncludeRewards', False))
        self.toggle_webhook_settings()

        # redraw all settings widgets
        self.map_render_check.draw()
        self.popup_check.draw()
        self.webhook_check.draw()
        self.embed_select.draw()
        self.webhook_entry.draw()
        self.raid_found_ping_entry.draw()
        self.exception_ping_entry.draw()
        self.include_rewards_check.draw()

    def draw_settings_frame(self):
        """Draw frame with settings information"""
        self.settings_frame = customtkinter.CTkFrame(master = self, width = 400)
        self.settings_frame.grid(row = 0, column = 2, columnspan = 2, sticky = "nsew")
        self.grid_columnconfigure(2, minsize = 400)

        self.safe_mode_check = customtkinter.CTkCheckBox(
            master = self.settings_frame,
            text = "Safe mode (slower, more consistent)"
        )
        self.safe_mode_check.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)

        # gui indication settings
        self.map_render_check = customtkinter.CTkCheckBox(
            master = self.settings_frame,
            text = "Render on map each reset (slow)"
        )
        self.map_render_check.grid(row = 1, column = 0, columnspan = 2, padx = 10, pady = 10)

        self.popup_check = customtkinter.CTkCheckBox(
            master = self.settings_frame,
            text = "Display popup when found"
        )
        self.popup_check.grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 10)

        # webhook settings
        self.webhook_check = customtkinter.CTkCheckBox(
            master = self.settings_frame,
            text = "Webhook Alerts",
            command = self.toggle_webhook_settings
        )
        self.webhook_check.grid(row = 3, column = 0, columnspan = 2, padx = 10, pady = 10)

        self.include_rewards_check = customtkinter.CTkCheckBox(
            master = self.settings_frame,
            text = "Include Raid Rewards",
        )
        self.include_rewards_check.grid(row = 4, column = 0, columnspan = 2, padx = 10, pady = 10)

        self.widget_label = customtkinter.CTkLabel(
            master = self.settings_frame,
            text = "Widget display"
        )
        self.widget_label.grid(row = 5, column = 0, padx = (10, 0), pady = 10)

        self.embed_select = customtkinter.CTkSwitch(
            master = self.settings_frame,
            # padding
            text = "     Embed display"
        )
        self.embed_select.grid(row = 5, column = 1, padx = (0, 10), pady = 10)

        # webook entry
        self.webhook_entry_label = customtkinter.CTkLabel(
            master = self.settings_frame,
            text = "Webhook URL:"
        )
        self.webhook_entry_label.grid(row = 6, column = 0, padx = 10, pady = 10)

        self.webhook_entry = customtkinter.CTkEntry(
            master = self.settings_frame,
            width = 150
        )
        self.webhook_entry.grid(row = 6, column = 1, padx = 10, pady = 10)

        self.raid_found_ping_entry_label = customtkinter.CTkLabel(
            master = self.settings_frame,
            text = "Raid Found ID to Ping:"
        )
        self.raid_found_ping_entry_label.grid(row = 7, column = 0, padx = 10, pady = 10)

        self.raid_found_ping_entry = customtkinter.CTkEntry(
            master = self.settings_frame,
            width = 150
        )
        self.raid_found_ping_entry.grid(row = 7, column = 1, padx = 10, pady = 10)

        self.exception_ping_entry_label = customtkinter.CTkLabel(
            master = self.settings_frame,
            text = "Exception ID to Ping:"
        )
        self.exception_ping_entry_label.grid(row = 8, column = 0, padx = 10, pady = 10)

        self.exception_ping_entry = customtkinter.CTkEntry(
            master = self.settings_frame,
            width = 150
        )
        self.exception_ping_entry.grid(row = 8, column = 1, padx = 10, pady = 10)

    def draw_filter_frame(self):
        """Draw frame with filter information"""
        self.filter_frame = customtkinter.CTkFrame(master = self, width = 400)
        self.filter_frame.grid(row = 0, column = 0, columnspan = 2, sticky = "nsew")
        self.grid_columnconfigure(0, minsize = 450)

        self.hp_filter = IVFilterWidget(self.filter_frame, title = "HP")
        self.hp_filter.grid(row = 0, column = 0, padx = 10, pady = (10, 0), columnspan = 2)

        self.atk_filter = IVFilterWidget(self.filter_frame, title = "ATK")
        self.atk_filter.grid(row = 1, column = 0, padx = 10, columnspan = 2)

        self.def_filter = IVFilterWidget(self.filter_frame, title = "DEF")
        self.def_filter.grid(row = 2, column = 0, padx = 10, columnspan = 2)

        self.spa_filter = IVFilterWidget(self.filter_frame, title = "SPA")
        self.spa_filter.grid(row = 3, column = 0, padx = 10, columnspan = 2)

        self.spd_filter = IVFilterWidget(self.filter_frame, title = "SPD")
        self.spd_filter.grid(row = 4, column = 0, padx = 10, columnspan = 2)

        self.spe_filter = IVFilterWidget(self.filter_frame, title = "SPE")
        self.spe_filter.grid(row = 5, column = 0, padx = 10, columnspan = 2)

        self.nature_label = customtkinter.CTkLabel(
            self.filter_frame,
            text = "Nature:"
        )
        self.nature_label.grid(row = 0, column = 2, pady = (10, 0))

        self.nature_filter = CheckedCombobox(
            self.filter_frame,
            values = list(Nature)
        )
        self.nature_filter.grid(row = 0, column = 3, padx = 10, pady = (10, 0))

        self.ability_label = customtkinter.CTkLabel(
            self.filter_frame,
            text = "Ability:"
        )
        self.ability_label.grid(row = 1, column = 2)

        self.ability_filter = CheckedCombobox(
            self.filter_frame,
            values = list(AbilityIndex)
        )
        self.ability_filter.grid(row = 1, column = 3, padx = 10)

        self.gender_label = customtkinter.CTkLabel(
            self.filter_frame,
            text = "Gender:"
        )
        self.gender_label.grid(row = 2, column = 2)

        self.gender_filter = CheckedCombobox(
            self.filter_frame,
            values = list(Gender)
        )
        self.gender_filter.grid(row = 2, column = 3, padx = 10)

        self.species_label = customtkinter.CTkLabel(
            self.filter_frame,
            text = "Species:"
        )
        self.species_label.grid(row = 3, column = 2)

        self.species_filter = ListViewCombobox(
            self.filter_frame,
            value_enum = Species
        )
        self.species_filter.grid(row = 3, column = 3, rowspan = 5, padx = 10)

        self.difficulty_label = customtkinter.CTkLabel(
            self.filter_frame,
            text = "Difficulty:"
        )
        self.difficulty_label.grid(row = 8, column = 2)

        self.difficulty_filter = CheckedCombobox(
            self.filter_frame,
            values = list(StarLevel)
        )
        self.difficulty_filter.grid(row = 8, column = 3, padx = 10)

        self.reward_label = customtkinter.CTkLabel(
            self.filter_frame,
            text = "Reward Items:"
        )
        self.reward_label.grid(row = 9, column = 2)

        self.reward_filter = CheckedCombobox(
            self.filter_frame,
            values = sorted(list(Item), key = lambda item: item.name)
        )
        self.reward_filter.grid(row = 9, column = 3, padx = 10)

        self.reward_count_filter_label = customtkinter.CTkLabel(
            self.filter_frame,
            text = "Min Reward Count:"
        )
        self.reward_count_filter_label.grid(row = 10, column = 2)

        self.reward_count_filter = Spinbox(self.filter_frame)
        self.reward_count_filter.grid(row = 10, column = 3, padx = 10)

        self.shiny_filter = customtkinter.CTkCheckBox(self.filter_frame, text = "Shiny Only")
        self.shiny_filter.grid(row = 11, column = 2, columnspan = 2)

        self.save_filter_button = customtkinter.CTkButton(
            self.filter_frame,
            text = "",
            image = self.SAVE_IMAGE,
            fg_color = customtkinter.ThemeManager.theme["color"]["frame_low"],
            width = self.SAVE_IMAGE.width(),
            height = self.SAVE_IMAGE.height(),
            command = self.save_filter
        )
        self.save_filter_button.grid(row = 12, column = 0, padx = 5, pady = (125, 5))

        self.load_filter_button = customtkinter.CTkButton(
            self.filter_frame,
            text = "",
            image = self.LOAD_IMAGE,
            fg_color = customtkinter.ThemeManager.theme["color"]["frame_low"],
            width = self.LOAD_IMAGE.width(),
            height = self.LOAD_IMAGE.height(),
            command = self.load_filter
        )
        self.load_filter_button.grid(row = 12, column = 1, padx = 5, pady = (125, 5))

    def save_filter(self):
        """Save current filter to file"""
        filename = filedialog.asksaveasfilename(
            filetypes = (("Filter Json", "*.json"),),
            initialdir = get_path("./resources/filter_settings/")
        )
        if not filename:
            return
        if not filename.endswith(".json"):
            filename = f"{filename}.json"
        filter_json = self.build_filter_json()
        with open(filename, "w+", encoding = "utf-8") as filter_json_file:
            json.dump(filter_json, filter_json_file, indent = 2)

    def build_filter_json(self):
        """Build filter json"""
        return {
            "IVFilter": [
                self.hp_filter.get_tuple(),
                self.atk_filter.get_tuple(),
                self.def_filter.get_tuple(),
                self.spa_filter.get_tuple(),
                self.spd_filter.get_tuple(),
                self.spe_filter.get_tuple()
            ],
            "NatureFilter": self.nature_filter.get(),
            "AbilityFilter": self.ability_filter.get(),
            "GenderFilter": self.gender_filter.get(),
            "SpeciesFilter": self.species_filter.get(),
            "DifficultyFilter": self.difficulty_filter.get(),
            "ShinyFilter": self.shiny_filter.get(),
            "RewardFilter": self.reward_filter.get(),
            "RewardCountFilter": self.reward_count_filter.get(),
        }

    def load_filter(self):
        """Load filter from file"""
        filename = filedialog.askopenfilename(
            filetypes = (("Filter Json", "*.json"),),
            initialdir = get_path("./resources/filter_settings/")
        )
        if not filename:
            return
        if not filename.endswith(".json"):
            filename = f"{filename}.json"
        with open(filename, "r", encoding = "utf-8") as filter_json_file:
            filter_json: dict = json.load(filter_json_file)
        self.read_filter_json(filter_json)

    def read_filter_json(self, filter_json):
        """Read filter json"""
        self.load_iv_filter(filter_json)
        self.load_combobox(self.nature_filter, filter_json, "NatureFilter")
        self.load_combobox(self.ability_filter, filter_json, "AbilityFilter")
        self.load_combobox(self.gender_filter, filter_json, "GenderFilter")
        self.load_combobox(self.species_filter, filter_json, "SpeciesFilter")
        self.load_combobox(self.difficulty_filter, filter_json, "DifficultyFilter")
        self.load_combobox(self.reward_filter, filter_json, "RewardFilter")
        self.reward_count_filter.set(filter_json.get("RewardCountFilter", 0))
        if filter_json.get("ShinyFilter", False):
            self.shiny_filter.select()
        else:
            self.shiny_filter.deselect()

    def load_iv_filter(self, filter_json: dict):
        """Load iv filter from filter_json"""
        iv_filters = filter_json.get(
            "IVFilter",
            [
                (0, 31),
                (0, 31),
                (0, 31),
                (0, 31),
                (0, 31),
                (0, 31),
            ]
        )
        self.hp_filter.set_tuple(
            iv_filters[0]
        )
        self.atk_filter.set_tuple(
            iv_filters[1]
        )
        self.def_filter.set_tuple(
            iv_filters[2]
        )
        self.spa_filter.set_tuple(
            iv_filters[3]
        )
        self.spd_filter.set_tuple(
            iv_filters[4]
        )
        self.spe_filter.set_tuple(
            iv_filters[5]
        )

    @staticmethod
    def load_combobox(combobox: CheckedCombobox | ListViewCombobox, filter_json: dict, key: str):
        """Load combobox from filter_json"""
        filter_data = filter_json.get(key, [])
        if isinstance(combobox, CheckedCombobox):
            for variable, value in zip(
                combobox.dropdown_menu.variables,
                combobox.dropdown_menu.values
            ):
                variable.set(value in filter_data)
            combobox.dropdown_callback()
        else:
            for value in filter_data:
                combobox.add_item(value)
