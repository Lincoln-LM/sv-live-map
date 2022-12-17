"""Modified TkinterMapView for use with the paldea map"""

import requests
from tkintermapview import TkinterMapView, osm_to_decimal
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
