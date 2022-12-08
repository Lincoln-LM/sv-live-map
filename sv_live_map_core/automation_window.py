"""Automation window"""

from __future__ import annotations
import sys
from threading import Thread
from functools import partial
from typing import TYPE_CHECKING
import customtkinter
from .raid_info_widget import RaidInfoWidget

if TYPE_CHECKING:
    from .application import Application
    from .raid_block import TeraRaid

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

        self.title("Automation Customization")
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
                # TODO: extract methods + clean + check for target_found between commands
                self.master.reader.click("HOME")
                self.master.reader.click("HOME")
                self.master.reader.click("HOME")
                self.master.reader.pause(1)
                self.master.reader.touch_hold(845, 545, 50)
                self.master.reader.touch_hold(845, 545, 50)
                self.master.reader.touch_hold(845, 545, 50)
                self.master.reader.pause(1.5)
                self.master.reader.press("DDOWN")
                self.master.reader.press("DDOWN")
                self.master.reader.press("DDOWN")
                self.master.reader.pause(2.5)
                self.master.reader.release("DDOWN")
                self.master.reader.press("A")
                self.master.reader.pause(0.1)
                self.master.reader.release("A")
                self.master.reader.press("DDOWN")
                self.master.reader.pause(0.825)
                self.master.reader.release("DDOWN")
                self.master.reader.press("A")
                self.master.reader.pause(0.1)
                self.master.reader.release("A")
                self.master.reader.pause(0.4)
                self.master.reader.touch_hold(1006, 386, 50)
                self.master.reader.pause(0.2)
                self.master.reader.touch_hold(151, 470, 50)
                self.master.reader.pause(0.2)
                self.master.reader.touch_hold(1102, 470, 50)
                self.master.reader.pause(0.2)
                self.master.reader.press("HOME")
                self.master.reader.pause(0.1)
                self.master.reader.release("HOME")
                self.master.reader.pause(0.8)
                self.master.reader.press("HOME")
                self.master.reader.pause(0.1)
                self.master.reader.release("HOME")
                self.master.reader.pause(5)
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

                # popup display of marker info for alers
                def popup_display_builder(raid: TeraRaid, _ = None):
                    self.master.widget_message_window(
                        f"Shiny {raid.species.name.title()} ★"
                        if raid.is_shiny else raid.species.name.title(),
                        RaidInfoWidget,
                        poke_sprite_handler = self.master.sprite_handler,
                        raid_data = raid,
                        fg_color = customtkinter.ThemeManager.theme["color"]["frame_low"],
                    )

                # webhook display of marker info for both shiny alerts and on_click events
                def webhook_display_builder(raid: TeraRaid, _ = None):
                    # TODO: webhook
                    pass

                for raid in raid_block.raids:
                    if not raid.is_enabled:
                        continue
                    popup_display = partial(popup_display_builder, raid)
                    webhook_display = partial(webhook_display_builder, raid)

                    # TODO: filters
                    matches_filters = raid.is_shiny
                    self.target_found |= matches_filters

                    if matches_filters:
                        if self.popup_check.get():
                            popup_display()
                        if self.webhook_check.get():
                            webhook_display()
        self.target_found = True
        sys.exit()

    def check_on_automation(self):
        """Check on the progress of automation"""
        if not self.target_found:
            self.after(1000, self.check_on_automation)
        else:
            print("TARGET FOUND")
            self.stop_automation()

    def draw_start_button_frame(self):
        """Draw start button frame"""
        self.start_button_frame = customtkinter.CTkFrame(master = self, width = 800)
        self.start_button_frame.grid(row = 1, column = 0, columnspan = 4, sticky = "nwse")
        self.start_button = customtkinter.CTkButton(
            master = self.start_button_frame,
            text = "Start Automation",
            width = 800,
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
            'WebhookUrl': self.webhook_entry.get()
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

    def parse_settings(self):
        """Load settings"""
        automation_settings: dict = self.settings.setdefault('Automation', {})
        self.map_render_check.check_state = automation_settings.get('MapRender', False)
        self.popup_check.check_state = automation_settings.get('Popup', False)
        self.webhook_check.check_state = automation_settings.get('Webhook', False)
        self.embed_select.check_state = automation_settings.get('Embed', False)
        self.webhook_entry.insert(0, automation_settings.get('WebhookUrl', ''))
        self.toggle_webhook_settings()

        # redraw all settings widgets
        self.map_render_check.draw()
        self.popup_check.draw()
        self.webhook_check.draw()
        self.embed_select.draw()
        self.webhook_entry.draw()

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

    def draw_filter_frame(self):
        """Draw frame with filter information"""
        self.filter_frame = customtkinter.CTkFrame(master = self, width = 400)
        self.filter_frame.grid(row = 0, column = 0, columnspan = 2, sticky = "nsew")
        self.grid_columnconfigure(0, minsize = 400)
