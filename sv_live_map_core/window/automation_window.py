"""Automation window"""

from __future__ import annotations
from typing import TYPE_CHECKING
from PIL import ImageTk, Image
import customtkinter
from .automation_settings_window import AutomationSettingsWindow
from ..auto.tera_raid_routine import TeraRaidRoutine
from ..widget.tera_raid_filter_widget import TeraRaidFilterWidget
from ..widget.webhook_settings_widget import WebhookSettingsWidget
from ..util.path_handler import get_path

if TYPE_CHECKING:
    from .application import Application


class AutomationWindow(customtkinter.CTkToplevel):
    """Automation window"""

    SETTINGS_IMAGE: ImageTk.PhotoImage = None

    def __init__(
        self,
        *args,
        settings: dict = None,
        master: Application = None,
        fg_color: str = "default_theme",
        **kwargs,
    ):
        self.settings: dict = settings or {}
        super().__init__(*args, master=master, fg_color=fg_color, **kwargs)
        self.master: Application

        self.routine: TeraRaidRoutine = TeraRaidRoutine()  # TODO: webhooks

        self.title("Filters & Automation")
        self.handle_close_events()
        self.cache_images()
        self.draw_filter_frame()
        self.draw_webhook_frame()
        self.draw_start_button_frame()

    def cache_images(self):
        """Cache GUI images"""
        if AutomationWindow.SETTINGS_IMAGE is None:
            AutomationWindow.SETTINGS_IMAGE = ImageTk.PhotoImage(
                Image.open(get_path("./resources/icons8/gear.png"))
            )

    def start_routine(self):
        """Start a routine as well as the after to check on it"""
        self.webhook_frame.save_webhook()
        self.filter_frame.save_filter()
        self.start_button.configure(text="Stop Automation")
        self.start_button.configure(command=self.stop_routine)
        if self.master.reader is not None:
            self.routine.reader = self.master.reader
        self.routine.webhooks = self.webhook_frame.get_webhook_dicts()
        self.routine.filters = self.filter_frame.get_filter_objects()
        self.routine.settings = self.settings.get("Automation", {})
        self.routine.parent_application = self.master
        self.routine.start_routine()
        self.check_on_routine()

    def stop_routine(self):
        """Manually stop a routine"""
        self.start_button.configure(text="Start Automation")
        self.start_button.configure(command=self.start_routine)
        self.routine.stop_routine()

    def check_on_routine(self):
        """Check on the progress of automation routine"""
        if self.routine.check_on_routine():
            self.after(1000, self.check_on_routine)
        else:
            self.start_button.configure(text="Start Automation")
            self.start_button.configure(command=self.start_routine)

    def advance_date(self):
        """Call routine's advance_date function"""
        if self.master.reader is not None:
            self.routine.reader = self.master.reader
        self.routine.webhooks = self.webhook_frame.get_webhook_dicts()
        self.routine.advance_date()

    def handle_close_events(self):
        """Handle close events"""
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle closing of the window"""
        self.webhook_frame.save_webhook()
        self.filter_frame.save_filter()
        self.master.automation_window = None
        self.destroy()

    def open_automation_settings(self):
        """Open automation settings toplevel"""
        # assign settings window to the main window in order to pass settings json easier
        AutomationSettingsWindow(self.master)

    def draw_webhook_frame(self):
        """Draw frame with settings information"""
        self.webhook_frame = WebhookSettingsWidget(master=self, width=400)
        self.webhook_frame.grid(row=0, column=2, columnspan=2, sticky="nsew")
        self.grid_columnconfigure(2, minsize=400)

    def draw_filter_frame(self):
        """Draw frame with filter information"""
        self.filter_frame = TeraRaidFilterWidget(master=self, width=400)
        self.filter_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def draw_start_button_frame(self):
        """Draw start button frame"""
        self.start_button_frame = customtkinter.CTkFrame(master=self, width=1250)
        self.start_button_frame.grid(row=1, column=0, columnspan=4, sticky="nwse")
        self.start_button = customtkinter.CTkButton(
            master=self.start_button_frame,
            text="Start Automation",
            width=1220,
            height=30,
            command=self.start_routine,
        )
        self.start_button.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="nwse",
            padx=5,
            pady=0,
        )
        self.automation_settings_button = customtkinter.CTkButton(
            master=self.start_button_frame,
            text="",
            image=self.SETTINGS_IMAGE,
            fg_color=customtkinter.ThemeManager.theme["color"]["frame_low"],
            width=self.SETTINGS_IMAGE.width(),
            height=self.SETTINGS_IMAGE.height() * 2,
            command=self.open_automation_settings,
        )
        self.automation_settings_button.grid(
            row=0,
            rowspan=3,
            column=5,
            pady=(0, 5),
            sticky="nwse",
        )
        self.advance_date_button = customtkinter.CTkButton(
            master=self.start_button_frame,
            text="Advance Date (Singular)",
            command=self.advance_date,
            height=30,
        )
        self.advance_date_button.grid(
            row=2, column=0, columnspan=4, sticky="nwse", padx=5, pady=5
        )
