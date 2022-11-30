"""Live Map GUI"""

import os.path
from typing import Any
import json
import customtkinter
from sv_live_map_core.nxreader import NXReader
from sv_live_map_core.paldea_map_view import PaldeaMapView

DEFAULT_IP = "192.168.0.0"

customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")

class Application(customtkinter.CTk):
    """Live Map GUI"""
    APP_NAME = "SV Live Map"
    WIDTH = 800
    HEIGHT = 512

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initialize for later
        self.reader: NXReader = None
        self.settings: dict[str, Any] = {}

        # if settings file exists then access it
        if os.path.exists("settings.json"):
            with open("settings.json", "r", encoding = "utf-8") as settings_file:
                self.settings = json.load(settings_file)

        # window settings
        self.title(self.APP_NAME)
        self.geometry(str(self.WIDTH) + "x" + str(self.HEIGHT))
        self.minsize(self.WIDTH, self.HEIGHT)

        # handle closing the application
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        # initialize widgets
        self.settings_frame = customtkinter.CTkFrame(master = self, width = 150)
        self.settings_frame.grid(row = 0, column = 0, columnspan = 2, sticky = "nsew")

        self.ip_label = customtkinter.CTkLabel(master = self.settings_frame, text = "IP Address:")
        self.ip_label.grid(row = 0, column = 0)

        self.ip_entry = customtkinter.CTkEntry(master = self.settings_frame)
        self.ip_entry.grid(row = 0, column = 1)
        self.ip_entry.insert(0, self.settings.get("IP", DEFAULT_IP))

        self.map_frame = customtkinter.CTkFrame(master = self, width = 150)
        self.map_frame.grid(row = 0, column = 2, sticky = "nsew")

        self.map_widget = PaldeaMapView(self.map_frame)
        self.map_widget.grid(row = 1, column = 0, sticky = "nw")

    def on_closing(self, _ = None):
        """Handle closing of the application"""
        # save settings on termination
        with open("settings.json", "w+", encoding = "utf-8") as settings_file:
            self.settings['IP'] = self.ip_entry.get()
            json.dump(self.settings, settings_file)

        # close reader on termination
        if self.reader:
            self.reader.close()

        self.destroy()

def main():
    """Main function of the appliation"""
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
