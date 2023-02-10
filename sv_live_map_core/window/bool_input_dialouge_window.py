"""Window for receiving a boolean input from the user"""

from typing import Callable
import customtkinter


class BoolInputDialogueWindow(customtkinter.CTkToplevel):
    """Window for receiving a boolean input from the user"""

    def __init__(
        self,
        *args,
        title: str = "Boolean Input Window",
        text: str = "Boolean Input:",
        command: Callable[[bool | None], None] = None,
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
        self.input_checkbox = customtkinter.CTkCheckBox(self, text=text)
        self.input_checkbox.pack(side="top", padx=10, pady=5)
        self.input_confirm = customtkinter.CTkButton(
            self, text="Confirm", command=self.on_closing
        )
        self.input_confirm.pack(side="bottom", padx=10, pady=(0, 10))

    def handle_close_events(self):
        """Handle close events"""
        self.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(empty=True))

    def on_closing(self, _=None, empty: bool = False):
        """Handle closing of the window"""
        if self.command is not None:
            self.command(None if empty else self.input_checkbox.get())
        self.destroy()
