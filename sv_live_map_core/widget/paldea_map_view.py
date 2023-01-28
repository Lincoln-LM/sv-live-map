"""Modified TkinterMapView for use with the paldea map"""

from typing import Self
import tkinter
import contextlib
import requests
from tkintermapview import TkinterMapView, osm_to_decimal
from tkintermapview.canvas_button import CanvasButton
import customtkinter
from PIL import Image, ImageTk
from .corrected_marker import CorrectedMarker


class PaldeaMapView(TkinterMapView):
    # pylint: disable=too-many-ancestors
    """Modified TkinterMapView for use with the paldea map"""
    def __init__(
        self,
        *args,
        width: int = 512,
        height: int = 512,
        corner_radius: int = 0,
        bg_color: str = None,
        database_path: str = None,
        use_database_only: bool = False,
        max_zoom: int = 5,
        on_popout = None,
        **kwargs
    ):
        super().__init__(
            *args,
            width=width,
            height=height,
            corner_radius=corner_radius,
            bg_color=bg_color,
            database_path=database_path,
            use_database_only=use_database_only,
            max_zoom=max_zoom,
            **kwargs
        )

        self.set_zoom(self.min_zoom)
        self.pop_out_button = CanvasButton(
            self,
            # reference already defined button's width to avoid needing to check OS
            (self.width - (20 + self.button_zoom_in.width), 20),
            text = "⇱",
            command = self.toggle_pop_out
        )
        self.is_popped_out = False
        self.old_grid_info = None
        self.old_pack_info = None
        self.old_place_info = None
        self.original_map: Self = None
        self.on_popout = on_popout

    def clone(self):
        """Clone map to a new toplevel"""
        # create new window to pop out to
        new_master = customtkinter.CTkToplevel()
        new_master.title("Paldea Map")
        # copy all relevant attributes
        clone = PaldeaMapView(new_master, **{key: self.cget(key) for key in self.configure()})
        new_master.protocol("WM_DELETE_WINDOW", clone.toggle_pop_out)
        clone.is_popped_out = self.is_popped_out
        clone.pop_out_button.text = "⇲" if clone.is_popped_out else "⇱"
        clone.on_popout = self.on_popout
        # redraw button
        clone.canvas.delete(self.pop_out_button.canvas_rect)
        clone.canvas.delete(self.pop_out_button.canvas_text)
        clone.pop_out_button.draw()
        # pack to fill the whole window
        clone.pack()
        # store geometry of map before pop out
        self.old_grid_info = None
        self.old_pack_info = None
        self.old_place_info = None
        with contextlib.suppress(tkinter.TclError):
            self.old_grid_info = self.grid_info()
        with contextlib.suppress(tkinter.TclError):
            self.old_pack_info = self.pack_info()
        with contextlib.suppress(tkinter.TclError):
            self.old_place_info = self.place_info()
        # un-render
        self.grid_forget()
        self.pack_forget()
        self.place_forget()
        clone.original_map = self
        # call on_popout method for adjusting master
        clone.on_popout(True, clone)

    def toggle_pop_out(self):
        """Toggle whether or not the map widget is popped out"""
        self.pop_out_button.text = "⇱" if self.is_popped_out else "⇲"
        self.is_popped_out = not self.is_popped_out
        # redraw button
        self.canvas.delete(self.pop_out_button.canvas_rect)
        self.canvas.delete(self.pop_out_button.canvas_text)
        self.pop_out_button.draw()
        if self.is_popped_out:
            self.clone()
        elif self.original_map:
            self.grid_forget()
            self.pack_forget()
            self.place_forget()
            self.master.destroy()
            if self.original_map.old_grid_info is not None:
                self.original_map.grid(self.original_map.old_grid_info)
            if self.original_map.old_pack_info is not None:
                self.original_map.pack(self.original_map.old_pack_info)
            if self.original_map.old_place_info is not None:
                self.original_map.place(self.original_map.old_place_info)
            self.original_map.toggle_pop_out()
            # call on_popout method for adjusting master
            self.original_map.on_popout(False, self.original_map)

    def pre_cache(self):
        # disable precaching
        pass

    def check_map_border_crossing(self):
        diff_x, diff_y = 0, 0
        if self.upper_left_tile_pos[0] < 0:
            diff_x += 0 - self.upper_left_tile_pos[0]

        if self.upper_left_tile_pos[1] < 0:
            diff_y += 0 - self.upper_left_tile_pos[1]
        if self.lower_right_tile_pos[0] > 2 ** round(self.zoom):
            diff_x -= self.lower_right_tile_pos[0] - (2 ** round(self.zoom))
        if self.lower_right_tile_pos[1] > 2 ** round(self.zoom):
            diff_y -= self.lower_right_tile_pos[1] - (2 ** round(self.zoom))

        self.upper_left_tile_pos = \
            self.upper_left_tile_pos[0] + diff_x, self.upper_left_tile_pos[1] + diff_y
        self.lower_right_tile_pos = \
            self.lower_right_tile_pos[0] + diff_x, self.lower_right_tile_pos[1] + diff_y

    def update_dimensions(self, event):
        if self.width != event.width or self.height != event.height:
            self.width = event.width
            self.height = event.height

    def get_tile_image_from_cache(self, zoom: int, x: int, y: int):
        if f"z{zoom}x{x}y{y}" in self.tile_image_cache:
            return self.tile_image_cache[f"z{zoom}x{x}y{y}"]
        return False

    def request_image(self, zoom: int, x: int, y: int, db_cursor = None):
        if not self.tile_in_bounds(zoom, x, y):
            return self.empty_tile_image

        try:
            req = requests.get(
                # files are stored with zoom inverted
                "https://github.com/Lincoln-LM/paldea-map-assets/raw/main/map/" \
                f"{5 - zoom}_{x}_{y}.png",
                stream = True,
                timeout = 5.0
            )
            img = ImageTk.PhotoImage(Image.open(req.raw))
            self.tile_image_cache[f'z{zoom}x{x}y{y}'] = img
            return img
        except requests.ConnectionError:
            return self.empty_tile_image

    def tile_in_bounds(self, zoom: int, x_pos: int, y_pos: int):
        """Check if a tile is in bounds"""
        return (
            0 < zoom <= self.max_zoom # ensure zoom is a valid value
            and 2 ** zoom > max(x_pos, y_pos) # ensure x and y are within zoom scale
            and min(x_pos, y_pos) >= 0 # ensure x and y are non negative
        )

    def set_marker(self, deg_x: float, deg_y: float, text: str = None, **kwargs) -> CorrectedMarker:
        marker = CorrectedMarker(self, (deg_x, deg_y), text=text, **kwargs)
        marker.draw()
        self.canvas_marker_list.append(marker)
        return marker

    def game_coordinates_to_deg(self, game_x: float, _: float, game_z: float):
        """Convert game coordinates to degrees for map"""
        # TODO: more accurate conversion
        return osm_to_decimal(
            (game_x + 2.072021484) / 5000,
            (game_z + 5505.240018) / 5000,
            0
        )
