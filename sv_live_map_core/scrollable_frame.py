"""Scrollable customtkinter Frame"""
import customtkinter

class ScrollableFrame(customtkinter.CTkFrame):
    """Scrollable customtkinter Frame"""
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.canvas_inner = customtkinter.CTkCanvas(
            self,
            bg = self.fg_color[self._appearance_mode],
            highlightthickness = 0
        )

        self.scrollbar = customtkinter.CTkScrollbar(
            self,
            orientation = "vertical",
            command = self.canvas_inner.yview
        )
        self.scrollable_frame = customtkinter.CTkFrame(self.canvas_inner)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda _: self.canvas_inner.configure(
                scrollregion = self.canvas_inner.bbox("all")
            )
        )

        self.canvas_inner.create_window((0, 0), window = self.scrollable_frame, anchor = "center")

        self.canvas_inner.configure(yscrollcommand = self.scrollbar.set)

        self.canvas_inner.pack(side = "left", fill = "both", expand = True)
        self.scrollbar.pack(side = "right", fill = "y")
