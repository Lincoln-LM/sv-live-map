"""Live Map GUI"""

import os.path
from typing import Any
import json
import struct
import customtkinter
from tkintermapview import osm_to_decimal
from sv_live_map_core.nxreader import NXReader
from sv_live_map_core.paldea_map_view import PaldeaMapView

customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")

class Application(customtkinter.CTk):
    """Live Map GUI"""
    APP_NAME = "SV Live Map"
    WIDTH = 800
    HEIGHT = 512
    DEFAULT_IP = "192.168.0.0"
    PLAYER_POS_ADDRESS = 0x42D6110

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
        self.ip_label.grid(row = 0, column = 0, pady = 5)

        self.ip_entry = customtkinter.CTkEntry(master = self.settings_frame)
        self.ip_entry.grid(row = 0, column = 1, pady = 5)
        self.ip_entry.insert(0, self.settings.get("IP", self.DEFAULT_IP))

        self.connect_button = customtkinter.CTkButton(
            master = self.settings_frame,
            text = "Connect!",
            width = 300,
            command=self.toggle_connection
        )
        self.connect_button.grid(row = 1, column = 0, columnspan = 2, padx = 10, pady = 5)

        self.position_button = customtkinter.CTkButton(
            master = self.settings_frame,
            text = "Track Player",
            width = 300,
            command=self.toggle_position_work
        )
        self.position_button.grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 5)

        self.map_frame = customtkinter.CTkFrame(master = self, width = 150)
        self.map_frame.grid(row = 0, column = 2, sticky = "nsew")

        self.map_widget = PaldeaMapView(self.map_frame)
        self.map_widget.grid(row = 1, column = 0, sticky = "nw")

        # background work
        self.background_workers: dict[str, dict] = {}

    def connect(self):
        """Connect to switch"""
        # TODO: warning for when this casues an exception as well as timing out while running
        self.reader = NXReader(self.ip_entry.get())

    def toggle_connection(self):
        """Toggle connection to switch"""
        if self.reader:
            self.reader.close()
            self.reader = None
            self.connect_button.configure(text = "Connect")
        else:
            self.connect()
            self.connect_button.configure(text = "Disconnect")

    def toggle_position_work(self):
        """Toggle player tracking"""
        # TODO: own class instead of dict?
        if 'position' not in self.background_workers:
            self.background_workers['position'] = {'active': False}
        if self.background_workers['position']['active']:
            self.after_cancel(self.background_workers['position']['worker'])
            self.background_workers['position']['active'] = False
            self.position_button.configure(text = "Track Player")
        else:
            self.position_button.configure(text = "Stop Tracking Player")
            self.background_workers['position']['active'] = True
            self.after(1000, self.position_work)

    def position_work(self):
        """Work to be done to update the player's position"""
        if self.reader:
            # omit Y (height) coordinate
            game_x, _, game_z = \
                struct.unpack("fff", self.reader.read_main(self.PLAYER_POS_ADDRESS, 12))
            # TODO: more accurate conversion
            pos_x, pos_y = osm_to_decimal(
                (game_x + 2.072021484) / 5000,
                (game_z + 5505.240018) / 5000,
                0
            )
            if 'marker' not in self.background_workers['position']:
                self.background_workers['position']['marker'] = \
                    self.map_widget.set_marker(pos_x, pos_y, "PLAYER")
            else:
                self.background_workers['position']['marker'].set_position(pos_x, pos_y)

            self.background_workers['position']['worker'] = self.after(1000, self.position_work)
        else:
            # TODO: warning for when not connected
            pass

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
