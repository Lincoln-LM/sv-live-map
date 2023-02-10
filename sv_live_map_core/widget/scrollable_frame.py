"""Scrollable customtkinter Frame"""

import sys
import customtkinter


class ScrollableFrame(customtkinter.CTkFrame):
    """Scrollable customtkinter Frame"""

    # pylint: disable=too-many-ancestors
    def __init__(self, master, *args, width=140, height=28, **kwargs):
        super().__init__(master, *args, width=width, height=height, **kwargs)

        self.canvas_inner = customtkinter.CTkCanvas(
            self,
            bg=self.fg_color[self._appearance_mode],
            highlightthickness=0,
            width=width - 20,
            height=height,
        )

        self.scrollbar = customtkinter.CTkScrollbar(
            self,
            orientation="vertical",
            command=self.canvas_inner.yview,
            height=height,
        )
        self.scrollable_frame = customtkinter.CTkFrame(
            self.canvas_inner,
            width=width - 20,
            height=height,
        )

        self.scrollable_frame.bind(
            "<Configure>",
            lambda _: self.canvas_inner.configure(
                scrollregion=self.canvas_inner.bbox("all")
            ),
        )

        self.scrollable_frame.bind("<Enter>", self.on_enter)
        self.scrollable_frame.bind("<Leave>", self.on_leave)

        self.canvas_inner.create_window(
            (0, 0), window=self.scrollable_frame, anchor="center"
        )

        self.canvas_inner.configure(yscrollcommand=self.scrollbar.set)

        self.canvas_inner.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def on_enter(self, _):
        """On enter event"""
        self.scrollable_frame.bind_all("<MouseWheel>", self.on_scroll)
        self.scrollable_frame.bind_all(
            "<Button-4>", lambda _: self.canvas_inner.yview_scroll(-1, "units")
        )
        self.scrollable_frame.bind_all(
            "<Button-5>", lambda _: self.canvas_inner.yview_scroll(1, "units")
        )

    def on_leave(self, _):
        """On leave event"""
        self.scrollable_frame.unbind_all("<MouseWheel>")
        self.scrollable_frame.unbind_all("<Button-4>")
        self.scrollable_frame.unbind_all("<Button-5>")

    def on_scroll(self, event):
        """On scroll event"""
        if sys.platform.startswith("win"):
            self.canvas_inner.yview_scroll(-1 * (round(event.delta / 120)), "units")
        elif sys.platform.startswith("darwin"):
            self.canvas_inner.yview_scroll(-1 * event.delta, "units")
