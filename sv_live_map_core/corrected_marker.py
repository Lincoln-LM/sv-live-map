"""CanvasPositionMarker that renders images correctly"""

import tkinter
from tkintermapview.canvas_position_marker import CanvasPositionMarker

class CorrectedMarker(CanvasPositionMarker):
    """CanvasPositionMarker that renders images correctly"""
    def draw(self, event=None):
        # TODO: lint tkintermapview's code lol
        canvas_pos_x, canvas_pos_y = self.get_canvas_pos(self.position)

        if not self.deleted:
            if 0 - 50 < canvas_pos_x < self.map_widget.width + 50 and 0 < canvas_pos_y < self.map_widget.height + 70:
                # draw icon image for marker
                if self.icon is not None:
                    if self.canvas_icon is None:
                        self.canvas_icon = self.map_widget.canvas.create_image(canvas_pos_x, canvas_pos_y,
                                                                               anchor=self.icon_anchor,
                                                                               image=self.icon,
                                                                               tag="marker")
                        if self.command is not None:
                            self.map_widget.canvas.tag_bind(self.canvas_icon, "<Enter>", self.mouse_enter)
                            self.map_widget.canvas.tag_bind(self.canvas_icon, "<Leave>", self.mouse_leave)
                            self.map_widget.canvas.tag_bind(self.canvas_icon, "<Double-Button-1>", self.click)
                    else:
                        self.map_widget.canvas.coords(self.canvas_icon, canvas_pos_x, canvas_pos_y)

                # draw standard icon shape
                else:
                    if self.polygon is None:
                        self.polygon = self.map_widget.canvas.create_polygon(canvas_pos_x - 14, canvas_pos_y - 23,
                                                                             canvas_pos_x, canvas_pos_y,
                                                                             canvas_pos_x + 14, canvas_pos_y - 23,
                                                                             fill=self.marker_color_outside, width=2,
                                                                             outline=self.marker_color_outside, tag="marker")
                        if self.command is not None:
                            self.map_widget.canvas.tag_bind(self.polygon, "<Enter>", self.mouse_enter)
                            self.map_widget.canvas.tag_bind(self.polygon, "<Leave>", self.mouse_leave)
                            self.map_widget.canvas.tag_bind(self.polygon, "<Double-Button-1>", self.click)
                    else:
                        self.map_widget.canvas.coords(self.polygon,
                                                      canvas_pos_x - 14, canvas_pos_y - 23,
                                                      canvas_pos_x, canvas_pos_y,
                                                      canvas_pos_x + 14, canvas_pos_y - 23)
                    if self.big_circle is None:
                        self.big_circle = self.map_widget.canvas.create_oval(canvas_pos_x - 14, canvas_pos_y - 45,
                                                                             canvas_pos_x + 14, canvas_pos_y - 17,
                                                                             fill=self.marker_color_circle, width=6,
                                                                             outline=self.marker_color_outside, tag="marker")
                        if self.command is not None:
                            self.map_widget.canvas.tag_bind(self.big_circle, "<Enter>", self.mouse_enter)
                            self.map_widget.canvas.tag_bind(self.big_circle, "<Leave>", self.mouse_leave)
                            self.map_widget.canvas.tag_bind(self.big_circle, "<Double-Button-1>", self.click)
                    else:
                        self.map_widget.canvas.coords(self.big_circle,
                                                      canvas_pos_x - 14, canvas_pos_y - 45,
                                                      canvas_pos_x + 14, canvas_pos_y - 17)

                if self.text is not None:
                    if self.canvas_text is None:
                        self.canvas_text = self.map_widget.canvas.create_text(canvas_pos_x, canvas_pos_y + self.text_y_offset,
                                                                              anchor=tkinter.S,
                                                                              text=self.text,
                                                                              fill=self.text_color,
                                                                              font=self.font,
                                                                              tag=("marker", "marker_text"))
                        if self.command is not None:
                            self.map_widget.canvas.tag_bind(self.canvas_text, "<Enter>", self.mouse_enter)
                            self.map_widget.canvas.tag_bind(self.canvas_text, "<Leave>", self.mouse_leave)
                            self.map_widget.canvas.tag_bind(self.canvas_text, "<Double-Button-1>", self.click)
                    else:
                        self.map_widget.canvas.coords(self.canvas_text, canvas_pos_x, canvas_pos_y + self.text_y_offset)
                        self.map_widget.canvas.itemconfig(self.canvas_text, text=self.text)
                else:
                    if self.canvas_text is not None:
                        self.map_widget.canvas.delete(self.canvas_text)

                if self.image is not None and self.image_zoom_visibility[0] <= self.map_widget.zoom <= self.image_zoom_visibility[1]\
                        and not self.image_hidden:

                    if self.canvas_image is None:
                        self.canvas_image = self.map_widget.canvas.create_image(canvas_pos_x, canvas_pos_y,
                                                                                anchor=tkinter.S,
                                                                                image=self.image,
                                                                                tag="marker")
                        if self.command is not None:
                            self.map_widget.canvas.tag_bind(self.canvas_image, "<Enter>", self.mouse_enter)
                            self.map_widget.canvas.tag_bind(self.canvas_image, "<Leave>", self.mouse_leave)
                            self.map_widget.canvas.tag_bind(self.canvas_image, "<Double-Button-1>", self.click)
                    else:
                        self.map_widget.canvas.coords(self.canvas_image, canvas_pos_x, canvas_pos_y)
                else:
                    if self.canvas_image is not None:
                        self.map_widget.canvas.delete(self.canvas_image)
                        self.canvas_image = None
            else:
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

            self.map_widget.manage_z_order()
