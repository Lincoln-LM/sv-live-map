"""CanvasPositionMarker that renders images correctly"""

import tkinter
from tkintermapview.canvas_position_marker import CanvasPositionMarker
from tkintermapview import TkinterMapView
from PIL import Image, ImageTk

class CorrectedMarker(CanvasPositionMarker):
    """CanvasPositionMarker that renders images correctly"""
    def __init__(
        self,
        map_widget: TkinterMapView,
        position: tuple,
        scale_with_zoom = False,
        **kwargs
    ):
        super().__init__(map_widget, position, **kwargs)
        self.scale_with_zoom = scale_with_zoom
        self.last_zoom = self.map_widget.zoom
        # tkinter images get garbage collected apparently?
        self.image_copy = self.image
        self.icon_copy = self.icon

    def calculate_text_y_offset(self):
        # TODO: support other anchors
        self.text_y_offset = 20

    def bind_click(self, obj):
        """Bind click methods of a canvas object"""
        if self.command is not None:
            self.map_widget.canvas.tag_bind(
                obj,
                "<Enter>",
                self.mouse_enter
            )
            self.map_widget.canvas.tag_bind(
                obj,
                "<Leave>",
                self.mouse_leave
            )
            self.map_widget.canvas.tag_bind(
                obj,
                "<Double-Button-1>",
                self.click
        )

    def in_bounds(self):
        """Check if marker is in bounds"""
        canvas_pos_x, canvas_pos_y = self.get_canvas_pos(self.position)
        return (
            -50 < canvas_pos_x < self.map_widget.width + 50 and
            0 < canvas_pos_y < self.map_widget.height + 70
        )

    def draw(self, _ = None):
        if self.deleted:
            return

        # unrender when out of bounds
        if not self.in_bounds():
            self.unrender()
            self.map_widget.manage_z_order()
            return

        if self.last_zoom != self.map_widget.zoom:
            # ensure icons are re-rendered when zoom changes
            self.last_zoom = self.map_widget.zoom
            self.unrender()

        canvas_pos_x, canvas_pos_y = self.get_canvas_pos(self.position)

        # draw standard icon shape
        if self.icon is None:
            self.update_standard_icon(canvas_pos_x, canvas_pos_y)
        # draw icon image for marker
        else:
            self.update_canvas_icon(canvas_pos_x, canvas_pos_y)

        # ensure no text is drawn
        if self.text is None:
            if self.canvas_text is not None:
                self.map_widget.canvas.delete(self.canvas_text)
        # draw set text
        else:
            self.update_canvas_text(canvas_pos_x, canvas_pos_y)

        if self.image is not None and not self.image_hidden and self.image_zoom_visible():
            self.update_canvas_image(canvas_pos_x, canvas_pos_y)
        # unrender image if hidden or not zoom visible
        elif self.canvas_image is not None:
            self.map_widget.canvas.delete(self.canvas_image)
            self.canvas_image = None

        self.map_widget.manage_z_order()

    def image_zoom_visible(self):
        """Check if images are visible based on map zoom"""
        return (
            self.image_zoom_visibility[0]
              <= self.map_widget.zoom
              <= self.image_zoom_visibility[1]
            )

    def update_canvas_image(self, canvas_pos_x, canvas_pos_y):
        """Update canvas image"""
        # draw image
        if self.canvas_image is None:
            img = ImageTk.getimage(self.image)
            if self.scale_with_zoom:
                img = img.resize(
                    (
                        round(self.image.width() * min(1, max(5/8, self.last_zoom / 4))),
                        round(self.image.height() * min(1, max(5/8, self.last_zoom / 4)))
                    ),
                    Image.LANCZOS
                )
            self.image_copy = ImageTk.PhotoImage(img)
            self.canvas_image = self.map_widget.canvas.create_image(
                canvas_pos_x,
                canvas_pos_y,
                anchor = tkinter.S,
                image = self.image_copy,
                tag = "marker"
            )
            self.bind_click(self.canvas_image)
        # move image
        else:
            self.map_widget.canvas.coords(self.canvas_image, canvas_pos_x, canvas_pos_y)

    def update_canvas_text(self, canvas_pos_x, canvas_pos_y):
        """Update canvas text"""
        # draw text
        if self.canvas_text is None:
            self.canvas_text = self.map_widget.canvas.create_text(
                canvas_pos_x,
                canvas_pos_y + self.text_y_offset,
                anchor = tkinter.S,
                text = self.text,
                fill = self.text_color,
                font = self.font,
                tag = ("marker", "marker_text")
            )
            self.bind_click(self.canvas_text)
        # move text
        else:
            self.map_widget.canvas.coords(
                self.canvas_text,
                canvas_pos_x,
                canvas_pos_y + self.text_y_offset
            )
            self.map_widget.canvas.itemconfig(self.canvas_text, text = self.text)

    def update_canvas_icon(self, canvas_pos_x, canvas_pos_y):
        """Update icon built from image"""
        # draw icon
        if self.canvas_icon is None:
            img = ImageTk.getimage(self.icon)
            if self.scale_with_zoom:
                img = img.resize(
                    (
                        round(self.icon.width() * min(1, max(5/8, self.last_zoom / 4))),
                        round(self.icon.height() * min(1, max(5/8, self.last_zoom / 4)))
                    ),
                    Image.LANCZOS
                )
            self.icon_copy = ImageTk.PhotoImage(img)
            self.canvas_icon = self.map_widget.canvas.create_image(
                canvas_pos_x,
                canvas_pos_y,
                anchor = self.icon_anchor,
                image = self.icon_copy,
                tag = "marker"
            )
            self.bind_click(self.canvas_icon)
        # move icon
        else:
            self.map_widget.canvas.coords(self.canvas_icon, canvas_pos_x, canvas_pos_y)

    def update_standard_icon(self, canvas_pos_x, canvas_pos_y):
        """Update standard icon build from shapes"""
        # draw polygon
        if self.polygon is None:
            self.polygon = self.map_widget.canvas.create_polygon(
                canvas_pos_x - 14,
                canvas_pos_y - 23,
                canvas_pos_x,
                canvas_pos_y,
                canvas_pos_x + 14,
                canvas_pos_y - 23,
                fill = self.marker_color_outside,
                width = 2,
                outline = self.marker_color_outside,
                tag = "marker"
            )
            self.bind_click(self.polygon)
        # move polygon
        else:
            self.map_widget.canvas.coords(
                self.polygon,
                canvas_pos_x - 14,
                canvas_pos_y - 23,
                canvas_pos_x,
                canvas_pos_y,
                canvas_pos_x + 14,
                canvas_pos_y - 23
            )
        # draw circle
        if self.big_circle is None:
            self.big_circle = self.map_widget.canvas.create_oval(
                canvas_pos_x - 14,
                canvas_pos_y - 45,
                canvas_pos_x + 14,
                canvas_pos_y - 17,
                fill = self.marker_color_circle,
                width = 6,
                outline = self.marker_color_outside,
                tag = "marker"
            )
            self.bind_click(self.big_circle)
        # move circle
        else:
            self.map_widget.canvas.coords(
                self.big_circle,
                canvas_pos_x - 14,
                canvas_pos_y - 45,
                canvas_pos_x + 14,
                canvas_pos_y - 17
            )

    def unrender(self):
        """Unrender icons"""
        # delete icon image
        if self.icon is not None:
            self.map_widget.canvas.delete(self.canvas_icon)
            self.canvas_icon = None
        # delete icon canvas shapes
        else:
            self.map_widget.canvas.delete(self.polygon, self.big_circle, self.canvas_image)
            self.polygon, self.big_circle, self.canvas_image = None, None, None

        if self.image is not None:
            self.map_widget.canvas.delete(self.canvas_image)
            self.canvas_image = None

        # delete text
        self.map_widget.canvas.delete(self.canvas_text)
        self.canvas_text = None

    def delete(self):
        if self.icon is not None:
            self.map_widget.canvas.delete(self.canvas_icon)
        if self.image is not None:
            self.map_widget.canvas.delete(self.canvas_image)
        return super().delete()
