"""Automation window"""

from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter

if TYPE_CHECKING:
    from .application import Application

HidKeyboardKey: dict[str, int] = {
    "A": 4,
    "B": 5,
    "C": 6,
    "D": 7,
    "E": 8,
    "F": 9,
    "G": 10,
    "H": 11,
    "I": 30, # Replaces to 1
    "J": 13,
    "K": 14,
    "L": 15,
    "M": 16,
    "N": 17,
    "O": 39, # O replaces to 0
    "P": 19,
    "Q": 20,
    "R": 21,
    "S": 22,
    "T": 23,
    "U": 24,
    "V": 25,
    "W": 26,
    "X": 27,
    "Y": 28,
    "Z": 22, # Z replaces to S
    "1": 30,
    "2": 31,
    "3": 32,
    "4": 33,
    "5": 34,
    "6": 35,
    "7": 36,
    "8": 37,
    "9": 38,
    "0": 39,
}

class FastCodeWindow(customtkinter.CTkToplevel):
    """Fast Code Entry window"""
    def __init__(
        self,
        *args,
        settings: dict = None,
        master: Application = None,
        fg_color="default_theme",
        **kwargs
    ):
        self.settings: dict = settings or {}
        super().__init__(*args, master = master, fg_color=fg_color, **kwargs)
        self.master: Application

        self.title("Fast Code Entry")
        self.past_clipboard = ''
        self.clipboard_after = None
        self.handle_close_events()
        self.draw_code_frame()
        self.draw_start_button_frame()

    def send_fce(self):
        """Send text from box to code entry screen."""
        code = self.code_entry.get().upper()
        keys = [HidKeyboardKey.get(key) for key in code if key in HidKeyboardKey]
        for key in keys:
            self.master.reader.key(key)
        self.master.reader.click("PLUS")

    def send_fce_clipboard(self):
        """Read clipboard and set code text as contents. Then send_fce."""
        self.code_entry.delete(0, len(self.code_entry.get()))
        self.code_entry.insert(0, self.master.clipboard_get())
        self.send_fce()

    def watch_fce_clipboard(self):
        """Monitor clipboard and set code text as contents. Then send_fce."""
        clipboard_code = self.master.clipboard_get()
        if not (clipboard_code == self.past_clipboard or clipboard_code == "") and len([character for character in clipboard_code.upper() if character in HidKeyboardKey])==6:
            self.past_clipboard = clipboard_code
            self.master.clipboard_clear()
            self.code_entry.delete(0, len(self.code_entry.get()))
            self.code_entry.insert(0, self.past_clipboard)
            self.send_fce()
        else:
            self.past_clipboard = clipboard_code
            self.clipboard_after = self.master.after(1, self.watch_fce_clipboard)

    def toggle_watch_clipboard(self):
        if self.clipboard_after is not None:
            self.after_cancel(self.clipboard_after)
            self.clipboard_after = None
            self.watch_clipboard.configure(text = "Watch for Raid Code (Clipboard)")
        else:
            self.past_clipboard = self.master.clipboard_get()
            self.watch_clipboard.configure(text = "Watching for Raid Code (Clipboard)... Click to stop.")
            self.watch_clipboard.update()
            self.watch_fce_clipboard()

    def draw_start_button_frame(self):
        """Draw start button frame"""
        self.start_button_frame = customtkinter.CTkFrame(master = self, width = 850)
        self.start_button_frame.grid(row = 1, column = 0, columnspan = 4, sticky = "nwse")
        self.send_code = customtkinter.CTkButton(
            master = self.start_button_frame,
            text = "Send Code",
            width = 850,
            height = 200,
            command = self.send_fce
        )
        self.send_code.grid(
            row = 0,
            column = 0,
            columnspan = 4,
            sticky = "nwse",
            padx = 5,
            pady = 5
        )
        self.send_clipboard = customtkinter.CTkButton(
            master = self.start_button_frame,
            text = "Send Code (Clipboard)",
            width = 850,
            height = 200,
            command = self.send_fce_clipboard
        )
        self.send_clipboard.grid(
            row = 1,
            column = 0,
            columnspan = 4,
            sticky = "nwse",
            padx = 5,
            pady = 5
        )
        self.watch_clipboard = customtkinter.CTkButton(
            master = self.start_button_frame,
            text = "Watch for Raid Code (Clipboard)",
            width = 850,
            height = 50,
            command = self.toggle_watch_clipboard
        )
        self.watch_clipboard.grid(
            row = 2,
            column = 0,
            columnspan = 4,
            sticky = "nwse",
            padx = 5,
            pady = 5
        )

    def handle_close_events(self):
        """Handle close events"""
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)

    def on_closing(self):
        """Handle closing of the window"""
        # TODO: make this less hacky
        self.master.fast_code_window = None

        self.destroy()

    def draw_code_frame(self):
        """Draw frame with code entry box"""
        self.code_frame = customtkinter.CTkFrame(master = self, width = 850)
        self.code_frame.grid(row = 0, column = 1, columnspan = 2, sticky = "nsew")
        self.grid_columnconfigure(1, minsize = 850)

        # code entry
        self.code_entry_label = customtkinter.CTkLabel(
            master = self.code_frame,
            text = "Raid Code:\nBoxes and buttons are large\nso they can be easily clicked."
        )
        self.code_entry_label.grid(row = 1, column = 0, padx = 10, pady = 10)

        self.code_entry = customtkinter.CTkEntry(
            master = self.code_frame,
            width = 550,
            height = 300
        )
        self.code_entry.grid(row = 1, column = 1, padx = 10, pady = 10)
