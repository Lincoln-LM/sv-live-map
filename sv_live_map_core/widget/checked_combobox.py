"""Checked Combobox"""

import sys
import tkinter
from typing import Callable, Any
import customtkinter
from customtkinter.widgets.dropdown_menu import DropdownMenu


class CheckedDropdownMenu(DropdownMenu):
    """Checked DropdownMenu"""
    def __init__(
        self,
        *args,
        min_character_width: int = 18,
        fg_color: str = "default_theme",
        hover_color: str = "default_theme",
        text_color: str = "default_theme",
        text_font: str = "default_theme",
        command: Callable = None,
        values: list = None,
        **kwargs
    ):
        self.variables = [tkinter.BooleanVar() for _ in values]
        super().__init__(
            *args,
            min_character_width=min_character_width,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            text_font=text_font,
            command=command,
            values=values,
            **kwargs
        )

    def add_menu_commands(self):
        if sys.platform.startswith("linux"):
            for variable, value in zip(self.variables, self.values):
                self.add_checkbutton(
                    label=f"  {str(value).ljust(self.min_character_width)}  ",
                    command=lambda v=value: self.button_callback(v),
                    compound="left",
                    variable=variable
                )
        else:
            for variable, value in zip(self.variables, self.values):
                self.add_checkbutton(
                    label=str(value).ljust(self.min_character_width),
                    command=lambda v=value: self.button_callback(v),
                    compound="left",
                    variable=variable
                )


class CheckedCombobox(customtkinter.CTkComboBox):
    """Checked Combobox"""
    def __init__(
        self,
        *args,
        bg_color: str = None,
        fg_color: str = "default_theme",
        border_color: str = "default_theme",
        button_color: str = "default_theme",
        button_hover_color: str = "default_theme",
        dropdown_color: str = "default_theme",
        dropdown_hover_color: str = "default_theme",
        dropdown_text_color: str = "default_theme",
        variable: tkinter.Variable = None,
        values: list = None,
        command: Callable = None,
        width: int = 140,
        height: int = 28,
        corner_radius: str = "default_theme",
        border_width: str = "default_theme",
        text_font: str = "default_theme",
        dropdown_text_font: str = "default_theme",
        text_color: str = "default_theme",
        text_color_disabled: str = "default_theme",
        hover: bool = True,
        state: str = tkinter.NORMAL,
        **kwargs
    ):
        super().__init__(
            *args,
            bg_color=bg_color,
            fg_color=fg_color,
            border_color=border_color,
            button_color=button_color,
            button_hover_color=button_hover_color,
            dropdown_color=dropdown_color,
            dropdown_hover_color=dropdown_hover_color,
            dropdown_text_color=dropdown_text_color,
            variable=variable,
            # TODO: hacky
            values=[],
            command=command,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=border_width,
            text_font=text_font,
            dropdown_text_font=dropdown_text_font,
            text_color=text_color,
            text_color_disabled=text_color_disabled,
            hover=hover,
            state=state,
            **kwargs
        )
        self.values = values
        self.dropdown_menu = CheckedDropdownMenu(
            master=self,
            values=self.values,
            command=self.dropdown_callback,
            fg_color=dropdown_color,
            hover_color=dropdown_hover_color,
            text_color=dropdown_text_color,
            text_font=dropdown_text_font
        )
        self.dropdown_callback()

    def dropdown_callback(self, _: Any = None):
        set_values = [
            value for variable, value
            in zip(self.dropdown_menu.variables, self.dropdown_menu.values)
            if variable.get()
        ]
        text = "|".join(str(value) for value in set_values) if set_values else "Any"
        if self.state == "readonly":
            self.entry.configure(state="normal")
            self.entry.delete(0, tkinter.END)
            self.entry.insert(0, text)
            self.entry.configure(state="readonly")
        else:
            self.entry.delete(0, tkinter.END)
            self.entry.insert(0, text)

        if self.command is not None:
            self.command(set_values)

    def get(self) -> list:
        """Get set values"""
        if set_values := [
            value for variable, value
            in zip(self.dropdown_menu.variables, self.dropdown_menu.values)
            if variable.get()
        ]:
            return set_values

        str_repr = self.entry.get()
        if str_repr == "Any":
            return []
        # TODO: pass enum to class constructor, hacky
        lookup_table = {value.name: value for value in type(self.values[0])}
        return [
            lookup_table[value.replace(" ", "_").upper()]
            for value
            in str_repr.split("|")
        ]
