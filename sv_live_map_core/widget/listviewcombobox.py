"""Combobox that allows multiple selections and autocomplete"""

import sys
import tkinter
from tkinter import ttk
from typing import Type, Any
from enum import IntEnum
import customtkinter
from customtkinter import ThemeManager, CTkCanvas, DrawEngine, Settings
from .scrollable_frame import ScrollableFrame


class CTkCompatibleCombobox(ttk.Combobox):
    """CTk compatible ttk Combobox with autocomplete"""
    def __init__(self, master, values: list = None, **kwargs) -> None:
        self.values = values or []
        self.style = ttk.Style(master)
        self.style.theme_use("default")
        self.style.configure("CTkCombobox.TCombobox", borderwidth=0)
        super().__init__(master, style="CTkCombobox.TCombobox", values=values, **kwargs)
        self.tk.eval(f'ttk::combobox::ConfigureListbox {self}')
        self.listbox = tkinter.Listbox()
        self.listbox._w = f'{self}.popdown.f.l'
        self.bind('<KeyRelease>', self.on_key)

    def on_key(self, event: Any = None) -> None:
        """Autocomplete to be run on keypress"""
        if event and event.keysym == "BackSpace":
            self.delete(self.index(tkinter.INSERT), tkinter.END)
        elif not event or event.keysym != "Return":
            if value := self.get():
                for option in self.values:
                    option = str(option)
                    if option.lower().startswith(value.lower()) and option.lower() != value.lower():
                        self.set(value + option[len(value):])
                        self.select_range(len(value), 'end')
                        break

    def configure(self, **kwargs):
        listbox_kwargs = {}
        style_kwargs = {}
        if bg := kwargs.pop('bg', None):
            listbox_kwargs['bg'] = bg
            style_kwargs['fieldbackground'] = bg
        if fg := kwargs.pop('fg', None):
            listbox_kwargs['fg'] = fg
            style_kwargs['foreground'] = fg
            style_kwargs['highlightcolor'] = fg
            style_kwargs['insertcolor'] = fg
        if highlightcolor := kwargs.pop('highlightcolor', None):
            listbox_kwargs['highlightcolor'] = highlightcolor
        if disabledbackground := kwargs.pop('disabledbackground', None):
            style_kwargs['disabledbackground'] = disabledbackground
        if disabledforeground := kwargs.pop('disabledforeground', None):
            style_kwargs['disabledforeground'] = disabledforeground
        self.listbox.configure(**listbox_kwargs)
        self.style.configure("CTkCombobox.TCombobox", **style_kwargs)
        ttk.Combobox.configure(self, kwargs)


class CTkCombobox(customtkinter.CTkBaseClass):
    """ttk Combobox stylized for ctk"""
    def __init__(
        self,
        values: list,
        *args,
        bg_color: str = None,
        fg_color: str = "default_theme",
        button_color="default_theme",
        button_hover_color: str = "default_theme",
        text_color: str = "default_theme",
        text_color_disabled: str = "default_theme",
        placeholder_text_color: str = "default_theme",
        text_font: str = "default_theme",
        corner_radius: str = "default_theme",
        border_width: str = "default_theme",
        border_color: str = "default_theme",
        width: int = 140,
        height: int = 28,
        hover: bool = True,
        state: str = tkinter.NORMAL,
        textvariable: tkinter.Variable = None,
        **kwargs,
    ) -> None:
        # CTkBaseClass
        if "master" in kwargs:
            super().__init__(
                *args,
                bg_color=bg_color,
                width=width,
                height=height,
                master=kwargs.pop("master"),
            )
        else:
            super().__init__(
                *args,
                bg_color=bg_color,
                width=width,
                height=height,
            )

        # grid settings
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # color
        self.fg_color = ThemeManager.theme["color"]["entry"] \
            if fg_color == "default_theme" \
            else fg_color
        self.text_color = ThemeManager.theme["color"]["text"] \
            if text_color == "default_theme" \
            else text_color
        self.text_color_disabled = ThemeManager.theme["color"]["text_button_disabled"] \
            if text_color_disabled == "default_theme" \
            else text_color_disabled
        self.placeholder_text_color = ThemeManager.theme["color"]["entry_placeholder_text"] \
            if placeholder_text_color == "default_theme" \
            else placeholder_text_color
        self.border_color = ThemeManager.theme["color"]["entry_border"] \
            if border_color == "default_theme" \
            else border_color
        self.button_color = ThemeManager.theme["color"]["combobox_border"] \
            if button_color == "default_theme" \
            else button_color
        self.button_hover_color = ThemeManager.theme["color"]["combobox_button_hover"] \
            if button_hover_color == "default_theme" \
            else button_hover_color

        # border
        self.corner_radius = ThemeManager.theme["shape"]["button_corner_radius"] \
            if corner_radius == "default_theme" \
                else corner_radius
        self.border_width = ThemeManager.theme["shape"]["entry_border_width"] \
            if border_width == "default_theme" \
                else border_width

        # font
        self.text_font = (ThemeManager.theme["text"]["font"], ThemeManager.theme["text"]["size"]) \
            if text_font == "default_theme" \
                else text_font

        # textvariable
        self.textvariable = textvariable

        # state, hover, and values
        self.state = state
        self.hover = hover
        self.values = values

        # canvas for entire widget (dropdown button)
        self.canvas = CTkCanvas(
            master = self,
            highlightthickness = 0,
            width = self.apply_widget_scaling(self._current_width),
            height = self.apply_widget_scaling(self._current_height)
        )
        self.canvas.grid(column = 0, row = 0, sticky = "nswe")
        self.draw_engine = DrawEngine(self.canvas)

        # canvas to cut off the default dropdown arrow of the combobox
        self.combobox_canvas = CTkCanvas(
            master = self,
            highlightthickness = 0,
            width = self.apply_widget_scaling(self._current_width),
            height = self.apply_widget_scaling(self._current_height)
        )

        self.combobox = CTkCompatibleCombobox(
            master = self.combobox_canvas,
            values = self.values,
            width = 1,
            font = self.apply_font_scaling(self.text_font),
            state = self.state,
            textvariable = self.textvariable,
            **kwargs
        )

        self.combobox_window = self.canvas.create_window(
            (
                self.apply_widget_scaling(self.corner_radius) \
                    if self.corner_radius >= 6 \
                        else self.apply_widget_scaling(6),
                self.apply_widget_scaling(self.border_width)
            ),
            window = self.combobox_canvas,
            anchor = "nw",
            height = self.apply_widget_scaling(height) - (
                self.apply_widget_scaling(self.corner_radius) \
                    if self.corner_radius >= 6 \
                        else self.apply_widget_scaling(6)),
            width = width - 34
        )
        self.combobox_canvas.create_window(
            (
                0,
                0
            ),
            window = self.combobox,
            anchor = "nw",
            height = self.apply_widget_scaling(height) - (
                self.apply_widget_scaling(self.corner_radius) \
                    if self.corner_radius >= 6 \
                        else self.apply_widget_scaling(6)),
            width = width - 20
        )

        self.canvas.tag_bind("right_parts", "<Enter>", self.on_enter)
        self.canvas.tag_bind("dropdown_arrow", "<Enter>", self.on_enter)
        self.canvas.tag_bind("right_parts", "<Leave>", self.on_leave)
        self.canvas.tag_bind("dropdown_arrow", "<Leave>", self.on_leave)
        self.canvas.tag_bind("right_parts", "<Button-1>", self.clicked)
        self.canvas.tag_bind("dropdown_arrow", "<Button-1>", self.clicked)
        super().bind('<Configure>', self.update_dimensions_event)
        self.draw()

    def draw(self, no_color_updates: bool = False) -> None:
        """Draw the widget"""
        left_section_width = self._current_width - self._current_height
        requires_recoloring = self.draw_engine.draw_rounded_rect_with_border_vertical_split(
            self.apply_widget_scaling(self._current_width),
            self.apply_widget_scaling(self._current_height),
            self.apply_widget_scaling(self.corner_radius),
            self.apply_widget_scaling(self.border_width),
            self.apply_widget_scaling(left_section_width)
        )

        requires_recoloring_2 = self.draw_engine.draw_dropdown_arrow(
            self.apply_widget_scaling(self._current_width - (self._current_height / 2)),
            self.apply_widget_scaling(self._current_height / 2),
            self.apply_widget_scaling(self._current_height / 3)
        )

        if not no_color_updates or requires_recoloring or requires_recoloring_2:
            self.canvas.configure(
                bg = ThemeManager.single_color(
                    self.bg_color,
                    self._appearance_mode
                )
            )

            self.canvas.itemconfig(
                "inner_parts_left",
                outline = ThemeManager.single_color(
                    self.fg_color,
                    self._appearance_mode
                ),
                fill = ThemeManager.single_color(
                    self.fg_color,
                    self._appearance_mode
                )
            )
            self.canvas.itemconfig(
                "border_parts_left",
                outline = ThemeManager.single_color(
                    self.border_color,
                    self._appearance_mode
                ),
                fill = ThemeManager.single_color(
                    self.border_color,
                    self._appearance_mode
                )
            )
            self.canvas.itemconfig(
                "inner_parts_right",
                outline = ThemeManager.single_color(
                    self.border_color,
                    self._appearance_mode
                ),
                fill = ThemeManager.single_color(
                    self.border_color,
                    self._appearance_mode
                )
            )
            self.canvas.itemconfig(
                "border_parts_right",
                outline = ThemeManager.single_color(
                    self.border_color,
                    self._appearance_mode
                ),
                fill = ThemeManager.single_color(
                    self.border_color,
                    self._appearance_mode
                )
            )

            self.combobox.configure(
                bg = ThemeManager.single_color(
                    self.fg_color,
                    self._appearance_mode
                ),
                fg = ThemeManager.single_color(
                    self.text_color,
                    self._appearance_mode
                ),
                disabledforeground = ThemeManager.single_color(
                    self.text_color_disabled,
                    self._appearance_mode
                ),
                disabledbackground = ThemeManager.single_color(
                    self.fg_color,
                    self._appearance_mode
                )
            )

            if self.state == tkinter.DISABLED:
                self.canvas.itemconfig(
                    "dropdown_arrow",
                    fill = ThemeManager.single_color(
                        self.text_color_disabled,
                        self._appearance_mode
                    )
                )
            else:
                self.canvas.itemconfig(
                    "dropdown_arrow",
                    fill = ThemeManager.single_color(
                        self.text_color,
                        self._appearance_mode
                    )
                )

    def on_enter(self, _ = None) -> None:
        """Called when widget is hovered over"""
        if self.hover is True and self.state == tkinter.NORMAL and len(self.values) > 0:
            if sys.platform == "darwin" and Settings.cursor_manipulation_enabled:
                self.canvas.configure(cursor = "pointinghand")
            elif sys.platform.startswith("win") and Settings.cursor_manipulation_enabled:
                self.canvas.configure(cursor = "hand2")

            self.canvas.itemconfig(
                "inner_parts_right",
                outline = ThemeManager.single_color(
                    self.button_hover_color,
                    self._appearance_mode
                ),
                fill = ThemeManager.single_color(
                    self.button_hover_color,
                    self._appearance_mode
                )
            )
            self.canvas.itemconfig(
                "border_parts_right",
                outline = ThemeManager.single_color(
                    self.button_hover_color,
                    self._appearance_mode
                ),
                fill = ThemeManager.single_color(
                    self.button_hover_color,
                    self._appearance_mode
                )
            )

    def on_leave(self, _ = None) -> None:
        """Called when widget is hovered off of"""
        if self.hover and len(self.values) > 0:
            if (
                Settings.cursor_manipulation_enabled
                and
                (
                    sys.platform == "darwin"
                    or sys.platform.startswith("win")
                )
            ):
                self.canvas.configure(cursor = "arrow")

            self.canvas.itemconfig(
                "inner_parts_right",
                outline = ThemeManager.single_color(
                    self.button_color,
                    self._appearance_mode
                ),
                fill = ThemeManager.single_color(
                    self.button_color,
                    self._appearance_mode
                )
            )
            self.canvas.itemconfig(
                "border_parts_right",
                outline = ThemeManager.single_color(
                    self.button_color,
                    self._appearance_mode
                ),
                fill = ThemeManager.single_color(
                    self.button_color,
                    self._appearance_mode
                )
            )

    def clicked(self, _ = None) -> None:
        """Called when the open button is clicked"""
        if self.state is not tkinter.DISABLED and len(self.values) > 0:
            self.combobox.focus_set()
            self.combobox.event_generate('<Down>')

class ListViewCombobox(customtkinter.CTkFrame):
    """Combobox that allows multiple selections and autocomplete"""
    def __init__(
        self,
        master,
        value_enum: Type[IntEnum],
        *args,
        width = 140,
        height = 28,
        **kwargs
    ) -> None:
        super().__init__(
            *args,
            width = width,
            height = height,
            master = master,
            **kwargs
        )
        self.value_enum = value_enum
        self.values = list(sorted(list(self.value_enum), key = str))
        self.value_lookup = {str(x): x for x in self.value_enum}
        self.list_widgets = {}
        self.combobox = CTkCombobox(
            list(map(str, self.values)),
            *args,
            master = self,
            width = width,
            height = height,
            **kwargs
        )
        self.combobox.pack(side = "top")
        self.listview = ScrollableFrame(self, width = width, height = 5 * 22)
        self.listview.pack(side = "bottom", pady = (5, 0))
        self.combobox.combobox.bind("<<ComboboxSelected>>", self.combobox_selected)
        self.combobox.combobox.bind("<Return>", self.combobox_selected)

    def combobox_selected(self, _ = None) -> None:
        """Toggle listview widget based on what is selected"""
        value = self.combobox.combobox.get()
        for option in self.values:
            option = str(option)
            if option.lower().startswith(value.lower()):
                value = option
                break
        try:
            value = self.value_lookup[value]
        except KeyError:
            pass
        else:
            if not self.remove_item(value):
                self.add_item(value)

    def add_item(self, value: int) -> None:
        """Add item to list"""
        enum_value = self.value_enum(value)
        str_value = str(enum_value)
        frame = customtkinter.CTkFrame(
            self.listview.scrollable_frame,
        )
        label = customtkinter.CTkLabel(
            frame,
            text = str_value,
            width = self.listview._current_width - 40,
            height = 20,
        )
        label.pack(side = "left")
        close_button = customtkinter.CTkButton(
            frame,
            text = "×",
            width = 20,
            height = 20,
            command = lambda: self.remove_item(enum_value)
        )
        close_button.pack(side = "right")
        frame.pack(side = "top", pady = 1)
        self.list_widgets[value] = frame

    def remove_item(self, value: int) -> bool:
        """Remove item from list"""
        if widget := self.list_widgets.pop(value, None):
            widget.pack_forget()
            del widget
            return True
        return False

    def clear(self) -> None:
        """Clear list"""
        for value in self.list_widgets.copy():
            self.remove_item(value)

    def get(self) -> list:
        """Get the value of the combobox"""
        return list(self.list_widgets.keys())
