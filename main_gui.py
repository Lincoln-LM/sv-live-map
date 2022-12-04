"""Live Map GUI"""

import binascii
from functools import partial
import pickle
import os
import os.path
import threading
from typing import Any
import json
import struct
from PIL import Image, ImageTk
import customtkinter
from tkintermapview import osm_to_decimal
from sv_live_map_core.raid_reader import RaidReader
from sv_live_map_core.paldea_map_view import PaldeaMapView
from sv_live_map_core.poke_sprite_handler import PokeSpriteHandler
from sv_live_map_core.scrollable_frame import ScrollableFrame
from sv_live_map_core.raid_info_widget import RaidInfoWidget
from sv_live_map_core.sv_enums import StarLevel
from sv_live_map_core.raid_enemy_table_array import RaidEnemyTableArray
from sv_live_map_core.raid_block import RaidBlock
from sv_live_map_core.corrected_marker import CorrectedMarker

customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")

class Application(customtkinter.CTk):
    """Live Map GUI"""
    APP_NAME = "SV Live Map"
    WIDTH = 1330
    HEIGHT = 512
    DEFAULT_IP = "192.168.0.0"
    PLAYER_POS_ADDRESS = 0x4380340
    ICON_PATH = "./resources/icons8/icon.png"
    SEPARATOR_COLOR = "#949392"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initialize for later
        self.reader: RaidReader = None
        self.sprite_handler: PokeSpriteHandler = PokeSpriteHandler(tk_image = True)
        self.settings: dict[str, Any] = {}

        # if settings file exists then access it
        if os.path.exists("settings.json"):
            with open("settings.json", "r", encoding = "utf-8") as settings_file:
                self.settings = json.load(settings_file)

        with open("./resources/den_locations.json", "r", encoding = "utf-8") as location_file:
            self.den_locations: dict[str, list[int, int, int]] = json.load(location_file)

        # window settings
        self.title(self.APP_NAME)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(self.WIDTH, self.HEIGHT)
        self.iconphoto(True, ImageTk.PhotoImage(Image.open(self.ICON_PATH)))

        # handle closing the application
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        # initialize widgets
        # leftmost frame
        self.settings_frame = customtkinter.CTkFrame(master = self, width = 150)
        self.settings_frame.grid(row = 0, column = 0, columnspan = 2, sticky = "nsew")
        self.grid_columnconfigure(0, minsize = 150)

        self.ip_label = customtkinter.CTkLabel(master = self.settings_frame, text = "IP Address:")
        self.ip_label.grid(row = 0, column = 0, pady = 5)

        self.ip_entry = customtkinter.CTkEntry(master = self.settings_frame)
        self.ip_entry.grid(row = 0, column = 1, pady = 5)
        self.ip_entry.insert(0, self.settings.get("IP", self.DEFAULT_IP))

        self.use_cached_tables = customtkinter.CTkCheckBox(
            master = self.settings_frame,
            text = "Use Cached Tables"
        )
        self.use_cached_tables.grid(row = 1, column = 0, columnspan = 2, padx = 10, pady = 5)
        if self.settings.get("UseCachedTables", False):
            self.use_cached_tables.select()

        self.connect_button = customtkinter.CTkButton(
            master = self.settings_frame,
            text = "Connect!",
            width = 300,
            command=self.toggle_connection
        )
        self.connect_button.grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 5)

        self.position_button = customtkinter.CTkButton(
            master = self.settings_frame,
            text = "Track Player",
            width = 300,
            command=self.toggle_position_work
        )
        self.position_button.grid(row = 3, column = 0, columnspan = 2, padx = 10, pady = 5)

        self.read_raids_button = customtkinter.CTkButton(
            master = self.settings_frame,
            text = "Read All Raids",
            width = 300,
            command=self.read_all_raids
        )
        self.read_raids_button.grid(row = 4, column = 0, columnspan = 2, padx = 10, pady = 5)

        self.raid_progress = customtkinter.CTkProgressBar(
            master = self.settings_frame,
            width = 300
        )
        self.raid_progress.grid(row = 5, column = 0, columnspan = 2, padx = 10, pady = 5)
        self.raid_progress.set(0)

        # middle frame
        self.map_frame = customtkinter.CTkFrame(master = self, width = 150)
        self.map_frame.grid(row = 0, column = 2, sticky = "nsew")
        self.grid_columnconfigure(2, minsize = 150)

        self.map_widget = PaldeaMapView(self.map_frame)
        self.map_widget.grid(row = 1, column = 0, sticky = "nw")

        # rightmost frame
        self.info_frame = ScrollableFrame(master = self, width = 500)
        self.info_frame.grid(row = 0, column = 3, sticky = "nsew")
        self.grid_columnconfigure(3, minsize = 500)

        self.info_frame_label = customtkinter.CTkLabel(
            master = self.info_frame.scrollable_frame,
            text = "Raid Info:",
        )
        self.info_frame_label.grid(
            row = 0,
            column = 0,
            columnspan = 4,
            sticky = "ew",
            padx = 10,
            pady = 5
        )

        self.info_frame_horizontal_separator = \
            customtkinter.CTkFrame(
                self.info_frame.scrollable_frame,
                bg_color = self.SEPARATOR_COLOR,
                fg_color = customtkinter.ThemeManager.theme["color"]["frame_low"],
                width = 500,
                height = 5,
                bd = 0
            )
        self.info_frame_horizontal_separator.grid(
            row = 1,
            column = 0,
            columnspan = 4,
            sticky = "ew",
        )
        self.raid_info_widgets: list[RaidInfoWidget] = []
        self.raid_markers: list[CorrectedMarker] = []
        self.raid_ids: list[str] = []

        # background work
        self.background_workers: dict[str, dict] = {}

    def read_cached_tables(self) -> tuple[RaidEnemyTableArray]:
        """Read cached encounter tables"""
        tables = []
        for level in StarLevel:
            if not os.path.exists(f"./cached_tables/{level.name}.pkl"):
                self.error_message_window(
                    "File Missing",
                    f"cached table ./cached_tables/{level.name}.pkl does not exist."
                )
                return None
            with open(f"./cached_tables/{level.name}.pkl", "rb") as file:
                tables.append(pickle.load(file))
        return tuple(tables)

    def dump_cached_tables(self):
        """Dump cached encounter tables"""
        if not os.path.exists("./cached_tables/"):
            os.mkdir("./cached_tables/")
        for level in StarLevel:
            with open(f"./cached_tables/{level.name}.pkl", "wb+") as file:
                index = level
                if level == StarLevel.EVENT:
                    index = -1
                pickle.dump(self.reader.raid_enemy_table_arrays[index], file)

    def connect(self) -> bool:
        """Connect to switch and return True if success"""
        try:
            if self.use_cached_tables.get():
                cached_tables = self.read_cached_tables()
                if cached_tables is not None:
                    self.reader = RaidReader(
                        self.ip_entry.get(),
                        read_safety = False,
                        raid_enemy_table_arrays = cached_tables
                    )
                    if len(self.reader.raid_enemy_table_arrays[0].raid_enemy_tables) == 0:
                        self.reader = None
                        self.error_message_window(
                            "Invalid",
                            "Cached raid data is invalid. " \
                            "Ensure the game is loaded in when reading."
                        )
                        return False
                else:
                    return False
            else:
                self.reader = RaidReader(self.ip_entry.get(), read_safety = True)
                # disable after the tables are read
                self.reader.read_safety = False
                if len(self.reader.raid_enemy_table_arrays[0].raid_enemy_tables) == 0:
                    self.reader = None
                    self.error_message_window(
                        "Invalid",
                        "Raid data is invalid. Ensure the game is loaded in."
                    )
                    return False
                self.dump_cached_tables()
            return True
        except TimeoutError:
            self.reader = None
            self.error_message_window("TimeoutError", "Connection timed out.")
            return False

    def toggle_connection(self):
        """Toggle connection to switch"""
        if self.reader:
            self.reader.close()
            self.reader = None
            self.connect_button.configure(text = "Connect")
        else:
            if self.connect():
                self.connect_button.configure(text = "Disconnect")

    def read_all_raids(self):
        """Read and display all raid information"""
        for info_widget in self.raid_info_widgets:
            info_widget.grid_forget()
        for marker in self.raid_markers:
            marker.delete()
        self.raid_info_widgets.clear()
        self.raid_markers.clear()
        self.raid_ids.clear()
        if self.reader:
            # struct.error/binascii.Error when connection terminates before all 12 bytes are read
            try:
                raid_block_data = self.reader.read_raid_block_data()
                self.connect_button.configure(require_redraw = True, state = "disabled")
                work = partial(self.read_all_raids_work, raid_block_data)
                work_thread = threading.Thread(target = work)
                work_thread.start()
                self.connect_button.configure(require_redraw = True, state = "enabled")
            except (TimeoutError, struct.error, binascii.Error):
                self.toggle_connection()
                if 'position' in self.background_workers \
                  and self.background_workers['position']['active']:
                    self.toggle_position_work()
                self.error_message_window("TimeoutError", "Connection timed out.")
                return
        else:
            self.error_message_window("Invalid", "Not connected to switch.")

    def read_all_raids_work(self, raid_block_data: RaidBlock):
        """Threading wokr for read all raids"""
        count = 0
        for raid in raid_block_data.raids:
            if raid.is_enabled:
                info_widget = RaidInfoWidget(
                    master = self.info_frame.scrollable_frame,
                    poke_sprite_handler = self.sprite_handler,
                    raid_data = raid,
                    fg_color = customtkinter.ThemeManager.theme["color"]["frame_low"],
                )
                self.raid_info_widgets.append(info_widget)
                count += 1
                id_str = f"{raid.area_id}-{raid.den_id}"
                if id_str in self.raid_ids:
                    print(f"WARNING duplicate raid id {id_str} is treated as {id_str}_")
                    id_str += "_"
                self.raid_ids.append(id_str)
                if id_str in self.den_locations:
                    game_x,_,game_z = self.den_locations[id_str]
                    pos_x, pos_y = osm_to_decimal(
                        (game_x + 2.072021484) / 5000,
                        (game_z + 5505.240018) / 5000,
                        0
                    )
                    # TODO: event/shiny icons
                    tera_sprite: Image.Image = ImageTk.getimage(info_widget.tera_sprite)
                    tera_sprite = tera_sprite.resize(
                        (
                            tera_sprite.height // 2,
                            tera_sprite.width // 2
                        )
                    )
                    tera_sprite = ImageTk.PhotoImage(tera_sprite)
                    poke_sprite = ImageTk.getimage(info_widget.poke_sprite)
                    poke_sprite = ImageTk.PhotoImage(poke_sprite)
                    self.raid_markers.append(
                        self.map_widget.set_marker(
                            pos_x,
                            pos_y,
                            icon = tera_sprite,
                            image = poke_sprite
                        )
                    )
                else:
                    # TODO: document all den locs, deal with dupes
                    print(f"WARNING den {id_str} location not present")
                self.raid_progress.set(count/69)
                info_widget.grid(row = count + 1, column = 0)

    def toggle_position_work(self):
        """Toggle player tracking"""
        # TODO: own class instead of dict?
        if 'position' not in self.background_workers:
            self.background_workers['position'] = {'active': False}
        if self.background_workers['position']['active']:
            self.background_workers['position']['marker'].delete()
            self.background_workers['position'].pop('marker')
            self.after_cancel(self.background_workers['position']['worker'])
            self.background_workers['position']['active'] = False
            self.position_button.configure(text = "Track Player")
        else:
            if self.reader:
                self.position_button.configure(text = "Stop Tracking Player")
                self.background_workers['position']['active'] = True
                self.after(1000, self.position_work)
            else:
                self.error_message_window("Invalid", "Not connected to switch.")

    def position_work(self):
        """Work to be done to update the player's position"""
        if self.reader:
            try:
                # omit Y (height) coordinate
                game_x, _, game_z = \
                    struct.unpack("fff", self.reader.read_main(self.PLAYER_POS_ADDRESS, 12))
            # struct.error/binascii.Error when connection terminates before all 12 bytes are read
            except (TimeoutError, struct.error, binascii.Error):
                self.toggle_connection()
                self.toggle_position_work()
                self.error_message_window("TimeoutError", "Connection timed out.")
                return
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

    def error_message_window(self, title, message):
        """Open new window with error message"""
        window = customtkinter.CTkToplevel(self)
        window.geometry("450x100")
        window.title(title)

        label = customtkinter.CTkLabel(window, text = message)
        label.pack(side = "top", pady = 10, padx = 10)

        button = customtkinter.CTkButton(window, text = "OK", command = window.destroy)
        button.pack(side = "bottom", pady = 10, padx = 10, fill = "x")

    def on_closing(self, _ = None):
        """Handle closing of the application"""
        # save settings on termination
        with open("settings.json", "w+", encoding = "utf-8") as settings_file:
            self.settings['IP'] = self.ip_entry.get()
            self.settings['UseCachedTables'] = self.use_cached_tables.get()
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
