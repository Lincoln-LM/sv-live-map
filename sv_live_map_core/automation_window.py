"""Automation window"""

from __future__ import annotations
import sys
import os
import io
import time
from threading import Thread
from typing import TYPE_CHECKING
from PIL import ImageGrab, ImageTk
import customtkinter
import discord_webhook
from .raid_info_widget import RaidInfoWidget
from .raid_filter import RaidFilter
from .iv_filter_widget import IVFilterWidget
from .sv_enums import Nature, AbilityIndex, Gender, Species, StarLevel
from .checked_combobox import CheckedCombobox

if TYPE_CHECKING:
    from typing import Type, Callable
    from PIL import Image
    from .application import Application
    from .raid_block import TeraRaid, RaidBlock

class AutomationWindow(customtkinter.CTkToplevel):
    """Automation window"""
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

        self.draw_filter_frame()
        self.draw_settings_frame()
        self.draw_start_button_frame()
        self.parse_settings()

    def start_automation(self):
        """Start automation"""
        self.target_found = False
        self.start_button.configure(require_redraw = True, text = "Stop Automation")
        self.start_button.configure(command = self.stop_automation)
        self.automation_thread = Thread(target = self.automation_work)
        self.automation_thread.start()
        self.update_check = self.after(1000, self.check_on_automation)

    def stop_automation(self):
        """Stop automation"""
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
        while not self.target_found:
            if self.master.reader:
                total_raid_count, total_reset_count, last_seed, raid_block = \
                    self.read_raids(total_raid_count, total_reset_count, last_seed)

                popup_display_builder, webhook_display_builder = self.define_builders()

                self.filter_raids(raid_block, popup_display_builder, webhook_display_builder)

                if self.target_found:
                    break

                self.full_dateskip()
            else:
                self.master.connection_error("Not connected to switch.")
                self.target_found = True
        self.target_found = True
        sys.exit()

    def advance_date(self):
        """Full process of dateskipping w/o checks for target_found"""
        self.leave_to_home()
        self.open_settings()
        self.open_datetime()
        self.skip_date()
        self.reopen_game()

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
                hide_sensitive_info=self.hide_info_check.get(),
                fg_color = customtkinter.ThemeManager.theme["color"]["frame_low"],
            )

        # webhook display of info
        def webhook_display_builder(raid: TeraRaid, _ = None):
            if self.embed_select.get():
                webhook = discord_webhook.webhook.DiscordWebhook(
                    url = self.webhook_entry.get(),
                    content = f"<@{self.ping_entry.get()}>"
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
                    hide_sensitive_info=self.hide_info_check.get(),
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

                webhook.add_embed(embed)
                webhook.execute()
            else:
                popup_window, _ = popup_display_builder(raid)
                x_pos, y_pos = popup_window.winfo_x() + 8, popup_window.winfo_y() + 5
                time.sleep(1)
                img = ImageGrab.grab(
                    (
                        x_pos,
                        y_pos,
                        x_pos + popup_window.winfo_width(),
                        y_pos + popup_window.winfo_height() + 23
                    )
                )
                time.sleep(1)
                popup_window.destroy()
                if not os.path.exists("./found_screenshots/"):
                    os.mkdir("./found_screenshots/")
                img.save(f"./found_screenshots/{raid.seed}.png")
                with open(f"./found_screenshots/{raid.seed}.png", "rb") as img:
                    webhook = discord_webhook.webhook.DiscordWebhook(
                        url = self.webhook_entry.get(),
                        content = f"<@{self.ping_entry.get()}>"
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
        raid_filter = RaidFilter(
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
            star_filter = self.difficulty_filter.get()
        )

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

    def full_dateskip(self):
        """Full process of dateskipping w/checks for target_found"""
        self.leave_to_home()
        if self.target_found:
            return
        self.open_settings()
        if self.target_found:
            return
        self.open_datetime()
        if self.target_found:
            return
        self.skip_date()
        if self.target_found:
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
        # scroll down to datetime, this is not fully consistent but will not break execution
        self.master.reader.manual_click("DDOWN", 0.7 if self.master.reader.usb_connection else 0.825)
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
        self.advance_date_button = customtkinter.CTkButton(
            master = self.start_button_frame,
            text = "Advance Date",
            width = 300,
            command = self.advance_date
        )
        self.advance_date_button.grid(row = 1, column = 0, columnspan = 4, sticky = "nwse")
        self.start_button_frame.grid(row = 2, column = 0, columnspan = 4, sticky = "nwse")
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
        self.settings['Automation'] = {
            'MapRender': self.map_render_check.get(),
            'Popup': self.popup_check.get(),
            'Webhook': self.webhook_check.get(),
            'Embed': self.embed_select.get(),
            'WebhookUrl': self.webhook_entry.get(),
            'PingId': self.ping_entry.get()
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
        self.ping_entry_label.configure(require_redraw = True, state = new_state)
        self.ping_entry.configure(require_redraw = True, state = new_state)

    def parse_settings(self):
        """Load settings"""
        automation_settings: dict = self.settings.setdefault('Automation', {})
        self.map_render_check.check_state = bool(automation_settings.get('MapRender', False))
        self.popup_check.check_state = bool(automation_settings.get('Popup', False))
        self.webhook_check.check_state = bool(automation_settings.get('Webhook', False))
        self.embed_select.check_state = bool(automation_settings.get('Embed', False))
        self.webhook_entry.insert(0, automation_settings.get('WebhookUrl', ''))
        self.ping_entry.insert(0, automation_settings.get('PingId', ''))
        self.toggle_webhook_settings()

        # redraw all settings widgets
        self.map_render_check.draw()
        self.popup_check.draw()
        self.webhook_check.draw()
        self.embed_select.draw()
        self.webhook_entry.draw()
        self.ping_entry.draw()

    def draw_settings_frame(self):
        """Draw frame with settings information"""
        self.settings_frame = customtkinter.CTkFrame(master = self, width = 400)
        self.settings_frame.grid(row = 0, column = 2, columnspan = 2, sticky = "nsew")
        self.grid_columnconfigure(2, minsize = 400)

        # gui indication settings
        self.map_render_check = customtkinter.CTkCheckBox(
            master = self.settings_frame,
            text = "Render on map each reset (slow)"
        )
        self.map_render_check.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)

        self.popup_check = customtkinter.CTkCheckBox(
            master = self.settings_frame,
            text = "Display popup when found"
        )
        self.popup_check.grid(row = 1, column = 0, columnspan = 2, padx = 10, pady = 10)

        # webhook settings
        self.webhook_check = customtkinter.CTkCheckBox(
            master = self.settings_frame,
            text = "Send webhook when found",
            command = self.toggle_webhook_settings
        )
        self.webhook_check.grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 10)

        self.widget_label = customtkinter.CTkLabel(
            master = self.settings_frame,
            text = "Widget display"
        )
        self.widget_label.grid(row = 3, column = 0, padx = (10, 0), pady = 10)

        self.embed_select = customtkinter.CTkSwitch(
            master = self.settings_frame,
            # padding
            text = "     Embed display"
        )
        self.embed_select.grid(row = 3, column = 1, padx = (0, 10), pady = 10)

        # webook entry
        self.webhook_entry_label = customtkinter.CTkLabel(
            master = self.settings_frame,
            text = "Webhook URL:"
        )
        self.webhook_entry_label.grid(row = 4, column = 0, padx = 10, pady = 10)

        self.webhook_entry = customtkinter.CTkEntry(
            master = self.settings_frame,
            width = 150
        )
        self.webhook_entry.grid(row = 4, column = 1, padx = 10, pady = 10)

        self.ping_entry_label = customtkinter.CTkLabel(
            master = self.settings_frame,
            text = "ID to Ping:"
        )
        self.ping_entry_label.grid(row = 5, column = 0, padx = 10, pady = 10)

        self.ping_entry = customtkinter.CTkEntry(
            master = self.settings_frame,
            width = 150
        )
        self.ping_entry.grid(row = 5, column = 1, padx = 10, pady = 10)

    def draw_filter_frame(self):
        """Draw frame with filter information"""
        self.filter_frame = customtkinter.CTkFrame(master = self, width = 400)
        self.filter_frame.grid(row = 0, column = 0, columnspan = 2, sticky = "nsew")
        self.grid_columnconfigure(0, minsize = 450)

        self.hp_filter = IVFilterWidget(self.filter_frame, title = "HP")
        self.hp_filter.grid(row = 0, column = 0, padx = 10, pady = (10, 0))

        self.atk_filter = IVFilterWidget(self.filter_frame, title = "ATK")
        self.atk_filter.grid(row = 1, column = 0, padx = 10)

        self.def_filter = IVFilterWidget(self.filter_frame, title = "DEF")
        self.def_filter.grid(row = 2, column = 0, padx = 10)

        self.spa_filter = IVFilterWidget(self.filter_frame, title = "SPA")
        self.spa_filter.grid(row = 3, column = 0, padx = 10)

        self.spd_filter = IVFilterWidget(self.filter_frame, title = "SPD")
        self.spd_filter.grid(row = 4, column = 0, padx = 10)

        self.spe_filter = IVFilterWidget(self.filter_frame, title = "SPE")
        self.spe_filter.grid(row = 5, column = 0, padx = 10)

        self.nature_label = customtkinter.CTkLabel(
            self.filter_frame,
            text = "Nature:"
        )
        self.nature_label.grid(row = 0, column = 1, pady = (10, 0))

        self.nature_filter = CheckedCombobox(
            self.filter_frame,
            values = list(Nature)
        )
        self.nature_filter.grid(row = 0, column = 2, padx = 10, pady = (10, 0))

        self.ability_label = customtkinter.CTkLabel(
            self.filter_frame,
            text = "Ability:"
        )
        self.ability_label.grid(row = 1, column = 1)

        self.ability_filter = CheckedCombobox(
            self.filter_frame,
            values = list(AbilityIndex)
        )
        self.ability_filter.grid(row = 1, column = 2, padx = 10)

        self.gender_label = customtkinter.CTkLabel(
            self.filter_frame,
            text = "Gender:"
        )
        self.gender_label.grid(row = 2, column = 1)

        self.gender_filter = CheckedCombobox(
            self.filter_frame,
            values = list(Gender)
        )
        self.gender_filter.grid(row = 2, column = 2, padx = 10)

        self.species_label = customtkinter.CTkLabel(
            self.filter_frame,
            text = "Species:"
        )
        self.species_label.grid(row = 3, column = 1)

        self.species_filter = CheckedCombobox(
            self.filter_frame,
            values = sorted(list(Species), key = lambda species: species.name)
        )
        self.species_filter.grid(row = 3, column = 2, padx = 10)

        self.difficulty_label = customtkinter.CTkLabel(
            self.filter_frame,
            text = "Difficulty:"
        )
        self.difficulty_label.grid(row = 4, column = 1)

        self.difficulty_filter = CheckedCombobox(
            self.filter_frame,
            values = list(StarLevel)
        )
        self.difficulty_filter.grid(row = 4, column = 2, padx = 10)

        self.shiny_filter = customtkinter.CTkCheckBox(self.filter_frame, text = "Shiny Only")
        self.shiny_filter.grid(row = 5, column = 1, columnspan = 2)
