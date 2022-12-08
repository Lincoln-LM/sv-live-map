"""Live Map GUI"""

import binascii
from functools import partial
import sys
import pickle
import os
import os.path
import threading
from typing import Any, Type
import json
import struct
from PIL import Image, ImageTk
import customtkinter
from sv_live_map_core.raid_reader import RaidReader
from sv_live_map_core.paldea_map_view import PaldeaMapView
from sv_live_map_core.poke_sprite_handler import PokeSpriteHandler
from sv_live_map_core.scrollable_frame import ScrollableFrame
from sv_live_map_core.raid_info_widget import RaidInfoWidget
from sv_live_map_core.sv_enums import StarLevel
from sv_live_map_core.raid_enemy_table_array import RaidEnemyTableArray
from sv_live_map_core.raid_block import RaidBlock, TeraRaid
from sv_live_map_core.corrected_marker import CorrectedMarker
from sv_live_map_core.personal_data_handler import PersonalDataHandler
from sv_live_map_core.automation_window import AutomationWindow

customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")

class Application(customtkinter.CTk):
    """Live Map GUI"""
    # pylint: disable=too-many-instance-attributes
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
        self.automation_window: AutomationWindow = None
        self.render_thread: threading.Thread = None
        self.sprite_handler: PokeSpriteHandler = PokeSpriteHandler(tk_image = True)
        self.settings: dict[str, Any] = {}

        self.load_settings_and_data()

        self.raid_info_widgets: list[RaidInfoWidget] = []
        self.raid_markers: dict[str, CorrectedMarker] = {}
        self.background_workers: dict[str, dict] = {}

        self.set_window_settings()
        self.handle_close_events()

        # initialize widgets
        self.draw_settings_frame()
        self.draw_map_frame()
        self.draw_info_frame()

    def load_settings_and_data(self):
        """Load settings information and den locations"""
        # if settings file exists then access it
        if os.path.exists("settings.json"):
            with open("settings.json", "r", encoding = "utf-8") as settings_file:
                self.settings = json.load(settings_file)

        with open("./resources/den_locations.json", "r", encoding = "utf-8") as location_file:
            self.den_locations: dict[str, list[int, int, int]] = json.load(location_file)

        # ensure personal data is loaded
        PersonalDataHandler()

    def draw_info_frame(self):
        """Draw the rightmost frame"""
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

    def draw_map_frame(self):
        """Draw the middle frame"""
        self.map_frame = customtkinter.CTkFrame(master = self, width = 150)
        self.map_frame.grid(row = 0, column = 2, sticky = "nsew")
        self.grid_columnconfigure(2, minsize = 150)

        self.map_widget = PaldeaMapView(self.map_frame)
        self.map_widget.grid(row = 1, column = 0, sticky = "nw")

    def draw_settings_frame(self):
        """Draw the leftmost frame"""
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
            command = self.toggle_connection
        )
        self.connect_button.grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 5)

        self.position_button = customtkinter.CTkButton(
            master = self.settings_frame,
            text = "Track Player",
            width = 300,
            command = self.toggle_position_work
        )
        self.position_button.grid(row = 3, column = 0, columnspan = 2, padx = 10, pady = 5)

        self.read_raids_button = customtkinter.CTkButton(
            master = self.settings_frame,
            text = "Read All Raids",
            width = 300,
            command = self.read_all_raids
        )
        self.read_raids_button.grid(row = 4, column = 0, columnspan = 2, padx = 10, pady = 5)

        self.raid_progress = customtkinter.CTkProgressBar(
            master = self.settings_frame,
            width = 300
        )
        self.raid_progress.grid(row = 5, column = 0, columnspan = 2, padx = 10, pady = 5)
        self.raid_progress.set(0)

        self.automation_button = customtkinter.CTkButton(
            master = self.settings_frame,
            text = "Automation",
            width = 300,
            command = self.open_automation_window
        )
        self.automation_button.grid(row = 6, column = 0, columnspan = 2, padx = 10, pady = 5)

    def open_automation_window(self):
        """Open Automation Window"""
        if self.automation_window is None:
            self.automation_window = AutomationWindow(settings = self.settings)
        self.automation_window.focus_force()

    def handle_close_events(self):
        """Handle close events"""
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

    def set_window_settings(self):
        """Set window settings"""
        self.title(self.APP_NAME)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(self.WIDTH, self.HEIGHT)
        self.iconphoto(True, ImageTk.PhotoImage(Image.open(self.ICON_PATH)))

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
                pickle.dump(self.reader.raid_enemy_table_arrays[level], file)

    def connect(self) -> bool:
        """Connect to switch and return True if success"""
        try:
            if self.use_cached_tables.get():
                cached_tables = self.read_cached_tables()
                if cached_tables is None:
                    return False
                self.reader = RaidReader(
                    self.ip_entry.get(),
                    read_safety = False,
                    raid_enemy_table_arrays = cached_tables
                )
                if len(self.reader.raid_enemy_table_arrays[0].raid_enemy_tables) == 0:
                    return self.connection_error(
                        "Cached raid data is invalid. Ensure the game is loaded in when reading."
                    )

            else:
                self.reader = RaidReader(self.ip_entry.get(), read_safety = True)
                # disable after the tables are read
                self.reader.read_safety = False
                if len(self.reader.raid_enemy_table_arrays[0].raid_enemy_tables) == 0:
                    return self.connection_error(
                        "Raid data is invalid. Ensure the game is loaded in."
                    )

                self.dump_cached_tables()
            return True
        except (TimeoutError, struct.error, binascii.Error) as error:
            self.reader = None
            self.error_message_window("TimeoutError", "Connection timed out.")
            print(error)
            return False

    def connection_error(self, error_message):
        """Set reader to None and open error window"""
        self.reader = None
        self.error_message_window("Invalid", error_message)
        return False

    def toggle_connection(self):
        """Toggle connection to switch"""
        if self.reader:
            self.reader.close()
            self.reader = None
            self.connect_button.configure(text = "Connect")
        elif self.connect():
            self.connect_button.configure(text = "Disconnect")

    def read_all_raids(self, render: bool = True) -> RaidBlock:
        """Read and display all raid information"""
        if self.reader:
            # struct.error/binascii.Error when connection terminates before all bytes are read
            try:
                # try reading up to 5 times before erroring
                for i in range(5):
                    try:
                        raid_block_data = self.reader.read_raid_block_data()
                        break
                    except binascii.Error as error:
                        self.reader.read_safety = True
                        print(f"Failed to read {i}")
                        if i == 4:
                            raise error
                self.reader.read_safety = False
                if render:
                    self.render_thread = self.render_raids(raid_block_data)
                return raid_block_data
            except (TimeoutError, struct.error, binascii.Error) as error:
                if 'position' in self.background_workers \
                      and self.background_workers['position']['active']:
                    self.toggle_position_work()
                self.connection_timeout(error)
        else:
            self.error_message_window("Invalid", "Not connected to switch.")

    def render_raids(self, raid_block_data) -> threading.Thread:
        """Display raid information"""
        for info_widget in self.raid_info_widgets:
            info_widget.grid_forget()
        for marker in self.raid_markers.values():
            marker.delete()
        self.raid_info_widgets.clear()
        self.raid_markers.clear()
        work = partial(self.render_raids_work, raid_block_data)
        work_thread = threading.Thread(target = work)
        work_thread.start()
        return work_thread

    def render_raids_work(self, raid_block_data: RaidBlock):
        """Threading work to render raids"""
        self.connect_button.configure(require_redraw = True, state = "disabled")
        self.position_button.configure(require_redraw = True, state = "disabled")
        self.read_raids_button.configure(require_redraw = True, state = "disabled")
        count = 0

        # popup display of marker info for on_click events
        def popup_display_builder(raid: TeraRaid, _ = None):
            self.widget_message_window(
                f"Shiny {raid.species.name.title()} ★"
                  if raid.is_shiny else raid.species.name.title(),
                RaidInfoWidget,
                poke_sprite_handler = self.sprite_handler,
                raid_data = raid,
                fg_color = customtkinter.ThemeManager.theme["color"]["frame_low"],
            )

        # swap the marker to its alternative position
        def swap_position(raid: TeraRaid):
            # swap whether or not the underscore is present
            if raid.id_str.endswith("_"):
                other_id_str = raid.id_str[:-1]
            else:
                other_id_str = f"{raid.id_str}_"
            # position has not been changed
            if self.raid_markers[raid.id_str].position \
              == self.map_widget.game_coordinates_to_deg(*self.den_locations[raid.id_str]):
                # swap the positions of the two markers
                self.raid_markers[raid.id_str].set_position(
                    *self.map_widget.game_coordinates_to_deg(*self.den_locations[other_id_str])
                )
                if other_id_str in self.raid_markers:
                    self.raid_markers[other_id_str].set_position(
                        *self.map_widget.game_coordinates_to_deg(*self.den_locations[raid.id_str])
                    )
            # position has been changed
            else:
                # set the two markers back to normal
                self.raid_markers[raid.id_str].set_position(
                    *self.map_widget.game_coordinates_to_deg(*self.den_locations[raid.id_str])
                )
                if other_id_str in self.raid_markers:
                    self.raid_markers[other_id_str].set_position(
                        *self.map_widget.game_coordinates_to_deg(*self.den_locations[other_id_str])
                    )

        # focus the map to the marker
        def focus_marker(raid: TeraRaid):
            self.map_widget.set_zoom(self.map_widget.max_zoom)
            self.map_widget.set_position(*self.raid_markers[raid.id_str].position)

        for raid in raid_block_data.raids:
            if raid.is_enabled:
                has_alternate_location = f"{raid.id_str}_" in self.den_locations
                if raid.id_str in self.raid_markers:
                    print(f"WARNING duplicate raid id {raid.id_str} is treated as {raid.id_str}_")
                    raid.id_str = f"{raid.id_str}_"

                info_widget = RaidInfoWidget(
                    master = self.info_frame.scrollable_frame,
                    poke_sprite_handler = self.sprite_handler,
                    raid_data = raid,
                    has_alternate_location = has_alternate_location,
                    focus_command = partial(focus_marker, raid),
                    swap_command = partial(swap_position, raid),
                    is_popup = False,
                    fg_color = customtkinter.ThemeManager.theme["color"]["frame_low"],
                )
                popup_display = partial(popup_display_builder, raid)
                self.raid_info_widgets.append(info_widget)
                count += 1
                if raid.id_str in self.den_locations:
                    pos_x, pos_y = self.map_widget.game_coordinates_to_deg(
                        *self.den_locations[raid.id_str]
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

                    self.raid_markers[raid.id_str] = self.map_widget.set_marker(
                        pos_x,
                        pos_y,
                        icon = tera_sprite,
                        image = poke_sprite,
                        command = popup_display
                    )
                else:
                    print(f"WARNING den {raid.id_str} location not present")
                self.raid_progress.set(count/69)
                info_widget.grid(row = count + 1, column = 0)
        self.connect_button.configure(require_redraw = True, state = "normal")
        self.position_button.configure(require_redraw = True, state = "normal")
        self.read_raids_button.configure(require_redraw = True, state = "normal")
        self.render_thread = None
        sys.exit()

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
        elif self.reader:
            self.position_button.configure(text = "Stop Tracking Player")
            self.background_workers['position']['active'] = True
            self.after(1000, self.position_work)
        else:
            self.error_message_window("Invalid", "Not connected to switch.")

    def position_work(self):
        """Work to be done to update the player's position"""
        if not self.reader:
            return
        try:
            # omit Y (height) coordinate
            game_x, _, game_z = \
                    struct.unpack("fff", self.reader.read_main(self.PLAYER_POS_ADDRESS, 12))
        except (TimeoutError, struct.error, binascii.Error) as error:
            self.connection_timeout(error)
        pos_x, pos_y = self.map_widget.game_coordinates_to_deg(game_x, _, game_z)
        if 'marker' not in self.background_workers['position']:
            self.background_workers['position']['marker'] = \
                    self.map_widget.set_marker(pos_x, pos_y, "PLAYER")
        else:
            self.background_workers['position']['marker'].set_position(pos_x, pos_y)

        self.background_workers['position']['worker'] = self.after(1000, self.position_work)

    def connection_timeout(self, error):
        """Toggle connection + buttons and display timeout error"""
        self.toggle_connection()
        self.connect_button.configure(require_redraw = True, state = "normal")
        self.position_button.configure(require_redraw = True, state = "normal")
        self.read_raids_button.configure(require_redraw = True, state = "normal")
        self.toggle_position_work()
        self.error_message_window("TimeoutError", "Connection timed out.")
        raise error

    def error_message_window(self, title: str, message: str):
        """Open new window with error message"""
        # TODO: scrollable textbox with full console error information
        window = customtkinter.CTkToplevel(self)
        window.geometry("450x100")
        window.title(title)

        label = customtkinter.CTkLabel(window, text = message)
        label.pack(side = "top", pady = 10, padx = 10)

        button = customtkinter.CTkButton(window, text = "OK", command = window.destroy)
        button.pack(side = "bottom", pady = 10, padx = 10, fill = "x")

        # TODO: this or focus()?
        window.focus_force()

    def widget_message_window(
        self,
        title: str,
        widget_type: Type[customtkinter.CTkBaseClass],
        **kwargs
    ):
        """Open new window with widget"""
        window = customtkinter.CTkToplevel(self)
        window.title(title)

        widget = widget_type(master = window, **kwargs)
        widget.pack(side = "top", pady = 10, padx = 10)

        button = customtkinter.CTkButton(window, text = "OK", command = window.destroy)
        button.pack(side = "bottom", pady = 10, padx = 10, fill = "x")

        # TODO: this or focus()?
        window.focus_force()

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
