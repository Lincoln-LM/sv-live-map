"""Spinbox for integers in a range"""

from typing import Callable
import customtkinter


class Spinbox(customtkinter.CTkFrame):
    """Spinbox for integers in a range"""

    def __init__(
        self,
        *args,
        minimum: int = 0,
        maximum: int = 100,
        default_value: int = 0,
        width: int = 140,
        height: int = 32,
        command: Callable = None,
        **kwargs
    ):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.minimum = minimum
        self.maximum = maximum
        self.command = command

        self.entry = customtkinter.CTkEntry(
            self, width=width - height * 2, height=height
        )
        self.entry.grid(row=0, column=1)
        self.sub_button = customtkinter.CTkButton(
            self, width=height, height=height, text="-", command=self.sub_button_command
        )
        self.sub_button.grid(row=0, column=0)
        self.add_button = customtkinter.CTkButton(
            self, width=height, height=height, text="+", command=self.add_button_command
        )
        self.add_button.grid(row=0, column=2)
        self.entry.insert(0, str(default_value))

    def add_button_command(self):
        """Command to be run when add button is clicked"""
        value = min(self.get() + 1, self.maximum)
        self.set(value)
        if self.command is not None:
            self.command(value)

    def sub_button_command(self):
        """Command to be run when sub button is clicked"""
        value = max(self.get() - 1, self.minimum)
        self.set(value)
        if self.command is not None:
            self.command(value)

    def get(self) -> int:
        """Get the value of the spinbox"""
        return int(self.entry.get())

    def set(self, value: int):
        """Set the value of the spinbox"""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
