"""Window for receiving a text input from the user"""

from typing import Callable
import customtkinter


class TextInputDialogueWindow(customtkinter.CTkToplevel):
    """Window for receiving a text input from the user"""

    def __init__(
        self,
        *args,
        title: str = "Text Input Window",
        text: str = "Text Input:",
        command: Callable[[str | None], None] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.title(title)
        self.draw_input_dialogue(text)
        self.command = command
        self.handle_close_events()
        self.grab_set()

    def draw_input_dialogue(self, text: str):
        """Draw input dialouge widgets"""
        self.input_label = customtkinter.CTkLabel(self, text=text)
        self.input_label.pack(side="top", padx=10, pady=(5, 0))
        self.input_entry = customtkinter.CTkEntry(self)
        self.input_entry.pack(side="top", padx=10, pady=(0, 5))
        self.input_confirm = customtkinter.CTkButton(
            self, text="Confirm", command=self.on_closing
        )
        self.input_confirm.pack(side="bottom", padx=10, pady=(0, 10))

    def handle_close_events(self):
        """Handle close events"""
        self.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(empty=True))
        self.input_entry.bind("<Return>", self.on_closing)

    def on_closing(self, _=None, empty: bool = False):
        """Handle closing of the window"""
        if self.command is not None:
            self.command(None if empty else (self.input_entry.get() or None))
        self.destroy()
