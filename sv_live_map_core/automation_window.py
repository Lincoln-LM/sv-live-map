"""Automation window"""

import customtkinter

class AutomationWindow(customtkinter.CTkToplevel):
    """Automation window"""
    def __init__(self, settings: dict, *args, fg_color="default_theme", **kwargs):
        self.settings: dict = settings
        super().__init__(*args, fg_color=fg_color, **kwargs)

        self.title("Automation Customization")
        self.handle_close_events()

        self.draw_filter_frame()
        self.draw_settings_frame()
        self.draw_start_button_frame()
        self.parse_settings()

    def draw_start_button_frame(self):
        """Draw start button frame"""
        self.start_button_frame = customtkinter.CTkFrame(master = self, width = 800)
        self.start_button_frame.grid(row = 1, column = 0, columnspan = 4, sticky = "nwse")
        self.start_button = customtkinter.CTkButton(
            master = self.start_button_frame,
            text = "Start Automation",
            width = 800
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
