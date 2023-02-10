"""Window for editing automation settings"""

import customtkinter


class AutomationSettingsWindow(customtkinter.CTkToplevel):
    """Window for editing automation settings"""

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super().__init__(
            *args,
            **kwargs
        )
        self.title("Automation Settings")
        self.handle_close_events()
        self.draw_settings_frame()
        self.parse_settings()
        self.grab_set()

    def draw_settings_frame(self):
        """Draw settings widgets"""
        self.map_render_check = customtkinter.CTkCheckBox(
            master=self,
            text="Render on map each reset (slow)"
        )
        self.map_render_check.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.popup_check = customtkinter.CTkCheckBox(
            master=self,
            text="Display popup when found"
        )
        self.popup_check.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    def parse_settings(self):
        """Load settings"""
        automation_settings: dict = self.master.settings.setdefault('Automation', {})
        self.map_render_check.check_state = bool(automation_settings.get('MapRender', False))
        self.popup_check.check_state = bool(automation_settings.get('Popup', False))

        self.map_render_check.draw()
        self.popup_check.draw()

    def handle_close_events(self):
        """Handle close events"""
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle closing of the window"""
        # save settings
        self.master.settings['Automation'] = {
            'MapRender': self.map_render_check.get(),
            'Popup': self.popup_check.get(),
        }
        self.destroy()
