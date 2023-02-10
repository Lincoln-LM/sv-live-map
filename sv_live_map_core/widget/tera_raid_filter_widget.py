"""Tera raid filter widget"""

import glob
import json
import os
import customtkinter
from PIL import ImageTk, Image
from .iv_filter_widget import IVFilterWidget
from .checked_combobox import CheckedCombobox
from .listviewcombobox import ListViewCombobox
from .spinbox import Spinbox
from ..window.text_input_dialouge_window import TextInputDialogueWindow
from ..window.bool_input_dialouge_window import BoolInputDialogueWindow
from ..util.path_handler import get_path
from ..util.raid_filter import RaidFilter
from ..enums import Nature, AbilityIndex, Gender, StarLevel, TeraType, Species, Item

# this may need to be abstracted if different kinds of filters are to be supported in the future


class TeraRaidFilterWidget(customtkinter.CTkFrame):
    """Tera raid filter widget"""
    EDIT_IMAGE: ImageTk.PhotoImage = None
    NEW_IMAGE: ImageTk.PhotoImage = None
    DELETE_IMAGE: ImageTk.PhotoImage = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_images()
        self.draw_filter_frame()
        self.select_filter(self.filter_combobox.values[0])

    def cache_images(self):
        """Cache GUI images"""
        if TeraRaidFilterWidget.EDIT_IMAGE is None:
            TeraRaidFilterWidget.EDIT_IMAGE = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/icons8/pencil.png")
                )
            )
        if TeraRaidFilterWidget.NEW_IMAGE is None:
            TeraRaidFilterWidget.NEW_IMAGE = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/icons8/plus.png")
                )
            )
        if TeraRaidFilterWidget.DELETE_IMAGE is None:
            TeraRaidFilterWidget.DELETE_IMAGE = ImageTk.PhotoImage(
                Image.open(
                    get_path("./resources/icons8/trash.png")
                )
            )

    def draw_filter_frame(self):
        """Draw frame with filter information"""
        self.filter_combobox_label = customtkinter.CTkLabel(
            self, text="Current Filter:"
        )
        self.filter_combobox_label.grid(row=0, column=0)
        self.filter_combobox = customtkinter.CTkComboBox(
            self,
            values=self.get_filters(),
            width=500,
            command=self.select_filter
        )
        self.filter_combobox.grid(row=0, column=1, columnspan=4)
        self.filter_combobox.entry.configure(state='disabled')

        self.new_filter_button = customtkinter.CTkButton(
            self,
            text="",
            image=self.NEW_IMAGE,
            fg_color=customtkinter.ThemeManager.theme["color"]["frame_low"],
            width=self.NEW_IMAGE.width(),
            height=self.NEW_IMAGE.height(),
            command=self.new_filter
        )
        self.new_filter_button.grid(row=0, column=5)
        self.edit_filter_button = customtkinter.CTkButton(
            self,
            text="",
            image=self.EDIT_IMAGE,
            fg_color=customtkinter.ThemeManager.theme["color"]["frame_low"],
            width=self.EDIT_IMAGE.width(),
            height=self.EDIT_IMAGE.height(),
            command=self.edit_filter
        )
        self.edit_filter_button.grid(row=0, column=6)
        self.delete_filter_button = customtkinter.CTkButton(
            self,
            text="",
            image=self.DELETE_IMAGE,
            fg_color=customtkinter.ThemeManager.theme["color"]["frame_low"],
            width=self.DELETE_IMAGE.width(),
            height=self.DELETE_IMAGE.height(),
            command=self.delete_filter
        )
        self.delete_filter_button.grid(row=0, column=7)

        self.hp_filter = IVFilterWidget(self, title="HP")
        self.hp_filter.grid(row=1, column=5, padx=10, pady=(10, 0), columnspan=3)

        self.atk_filter = IVFilterWidget(self, title="ATK")
        self.atk_filter.grid(row=2, column=5, padx=10, columnspan=3)

        self.def_filter = IVFilterWidget(self, title="DEF")
        self.def_filter.grid(row=3, column=5, padx=10, columnspan=3)

        self.spa_filter = IVFilterWidget(self, title="SPA")
        self.spa_filter.grid(row=4, column=5, padx=10, columnspan=3)

        self.spd_filter = IVFilterWidget(self, title="SPD")
        self.spd_filter.grid(row=5, column=5, padx=10, columnspan=3)

        self.spe_filter = IVFilterWidget(self, title="SPE")
        self.spe_filter.grid(row=6, column=5, padx=10, columnspan=3)

        self.nature_label = customtkinter.CTkLabel(
            self,
            text="Nature:"
        )
        self.nature_label.grid(row=7, column=0, pady=(10, 0))

        self.nature_filter = CheckedCombobox(
            self,
            values=list(Nature)
        )
        self.nature_filter.grid(row=7, column=1, padx=10, pady=(10, 0))

        self.ability_label = customtkinter.CTkLabel(
            self,
            text="Ability:"
        )
        self.ability_label.grid(row=8, column=0)

        self.ability_filter = CheckedCombobox(
            self,
            values=list(AbilityIndex)
        )
        self.ability_filter.grid(row=8, column=1, padx=10)

        self.gender_label = customtkinter.CTkLabel(
            self,
            text="Gender:"
        )
        self.gender_label.grid(row=9, column=0)

        self.gender_filter = CheckedCombobox(
            self,
            values=list(Gender)
        )
        self.gender_filter.grid(row=9, column=1, padx=10)

        self.difficulty_label = customtkinter.CTkLabel(
            self,
            text="Difficulty:"
        )
        self.difficulty_label.grid(row=10, column=0)

        self.difficulty_filter = CheckedCombobox(
            self,
            values=list(StarLevel)
        )
        self.difficulty_filter.grid(row=10, column=1, padx=10)

        self.tera_type_label = customtkinter.CTkLabel(
            self,
            text="Tera Type:"
        )
        self.tera_type_label.grid(row=11, column=0)

        self.tera_type_filter = CheckedCombobox(
            self,
            values=list(TeraType)
        )
        self.tera_type_filter.grid(row=11, column=1, padx=10)

        self.shiny_filter = customtkinter.CTkCheckBox(self, text="Shiny Only")
        self.shiny_filter.grid(row=12, column=0, columnspan=2, pady=10)

        self.species_label = customtkinter.CTkLabel(
            self,
            text="Species:"
        )
        self.species_label.grid(row=1, column=0)

        self.species_filter = ListViewCombobox(
            self,
            value_enum=Species
        )
        self.species_filter.grid(
            row=1,
            column=1,
            rowspan=5,
            padx=10,
            pady=(10, 0),
            sticky="n"
        )

        self.reward_label = customtkinter.CTkLabel(
            self,
            text="Reward Items:"
        )
        self.reward_label.grid(row=1, column=3)

        self.reward_filter = ListViewCombobox(
            self,
            value_enum=Item,
            width=200
        )
        self.reward_filter.grid(
            row=1,
            column=4,
            rowspan=10,
            padx=10,
            pady=(10, 0),
            sticky="n"
        )

        self.reward_count_filter_label = customtkinter.CTkLabel(
            self,
            text="Min Reward Count:"
        )
        self.reward_count_filter_label.grid(row=7, column=3, pady=(10, 0))

        self.reward_count_filter = Spinbox(self, width=200, height=28)
        self.reward_count_filter.grid(row=7, column=4, padx=10, sticky="n", pady=(10, 0))

        self.filter_active = customtkinter.CTkCheckBox(self, text="Filter Active")
        self.filter_active.grid(row=12, column=3, columnspan=2, pady=10)

    def select_filter(self, name: str):
        """To be run when a filter is selected"""
        if name and name != self.filter_combobox.get():
            self.save_filter()
        self.filter_combobox.entry.configure(state='normal')
        self.filter_combobox.set(name)
        self.filter_combobox.entry.configure(state='disabled')

        if name:
            file_path = get_path(f"./resources/filter_settings/{name}")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as filter_file:
                    filter_json = json.load(filter_file)
                    self.load_filter(filter_json)

    def new_filter(self):
        """Create a new filter"""
        TextInputDialogueWindow(
            title="Filter Creation",
            text="Enter New Filter Name:",
            command=self.new_filter_action
        )

    def new_filter_action(self, name: str):
        """Create new filter file"""
        if name is None:
            return
        with open(
            get_path(f"./resources/filter_settings/{name}.json"),
            "w+",
            encoding="utf-8"
        ) as new_filter:
            new_filter.write("{}")
        self.filter_combobox.configure(values=self.get_filters())
        self.select_filter(f"{name}.json")

    def edit_filter(self):
        """Edit the name of a filter"""
        TextInputDialogueWindow(
            title="Filter Edit",
            text="Enter New Filter Name:",
            command=self.edit_filter_action
        )

    def edit_filter_action(self, name: str):
        """Rename filter file"""
        if name is None:
            return
        os.rename(
            get_path(f"./resources/filter_settings/{self.filter_combobox.get()}"),
            get_path(f"./resources/filter_settings/{name}.json")
        )
        self.filter_combobox.configure(values=self.get_filters())
        self.select_filter(f"{name}.json")

    def delete_filter(self):
        """Delete a filter"""
        BoolInputDialogueWindow(
            title="Delete Filter",
            text=f"Delete the filter {self.filter_combobox.get()}?",
            command=self.delete_filter_action
        )

    def delete_filter_action(self, confirm: bool):
        """Delete filter file"""
        if confirm:
            os.remove(get_path(f"./resources/filter_settings/{self.filter_combobox.get()}"))
            self.select_filter("")
            self.filter_combobox.configure(values=self.get_filters())
            # TODO: default case when no filters
            self.select_filter(self.filter_combobox.values[0])

    def save_filter(self):
        """Save current filter to file"""
        if name := self.filter_combobox.get():
            with open(
                get_path(f"./resources/filter_settings/{name}"),
                "w+",
                encoding="utf-8"
            ) as filter_json_file:
                json.dump(self.build_filter_json(), filter_json_file, indent=2)

    def build_filter_json(self):
        """Build filter json"""
        return {
            "IVFilter": [
                self.hp_filter.get_tuple(),
                self.atk_filter.get_tuple(),
                self.def_filter.get_tuple(),
                self.spa_filter.get_tuple(),
                self.spd_filter.get_tuple(),
                self.spe_filter.get_tuple()
            ],
            "NatureFilter": self.nature_filter.get(),
            "AbilityFilter": self.ability_filter.get(),
            "GenderFilter": self.gender_filter.get(),
            "SpeciesFilter": self.species_filter.get(),
            "DifficultyFilter": self.difficulty_filter.get(),
            "TeraTypeFilter": self.tera_type_filter.get(),
            "ShinyFilter": self.shiny_filter.get(),
            "RewardFilter": self.reward_filter.get(),
            "RewardCountFilter": self.reward_count_filter.get(),
            "IsEnabled": self.filter_active.get(),
        }

    def build_filter(self) -> RaidFilter:
        """Build RaidFilter"""
        return RaidFilter(
            hp_filter=self.hp_filter.get(),
            atk_filter=self.atk_filter.get(),
            def_filter=self.def_filter.get(),
            spa_filter=self.spa_filter.get(),
            spd_filter=self.spd_filter.get(),
            spe_filter=self.spe_filter.get(),
            ability_filter=self.ability_filter.get(),
            gender_filter=self.gender_filter.get(),
            nature_filter=self.nature_filter.get(),
            species_filter=self.species_filter.get(),
            shiny_filter=self.shiny_filter.get(),
            star_filter=self.difficulty_filter.get(),
            tera_type_filter=self.tera_type_filter.get(),
            reward_filter=self.reward_filter.get(),
            reward_count_filter=self.reward_count_filter.get(),
            is_enabled=bool(self.filter_active.get())
        )

    def load_filter(self, filter_json):
        """Load filter json into gui"""
        self.load_iv_filter(filter_json)
        self.load_combobox(self.nature_filter, filter_json, "NatureFilter")
        self.load_combobox(self.ability_filter, filter_json, "AbilityFilter")
        self.load_combobox(self.gender_filter, filter_json, "GenderFilter")
        self.load_combobox(self.species_filter, filter_json, "SpeciesFilter")
        self.load_combobox(self.difficulty_filter, filter_json, "DifficultyFilter")
        self.load_combobox(self.tera_type_filter, filter_json, "TeraTypeFilter")
        self.load_combobox(self.reward_filter, filter_json, "RewardFilter")
        self.reward_count_filter.set(filter_json.get("RewardCountFilter", 0))
        if filter_json.get("ShinyFilter", False):
            self.shiny_filter.select()
        else:
            self.shiny_filter.deselect()
        if filter_json.get("IsEnabled", False):
            self.filter_active.select()
        else:
            self.filter_active.deselect()

    def load_iv_filter(self, filter_json: dict):
        """Load iv filter from filter_json"""
        iv_filters = filter_json.get(
            "IVFilter",
            [
                (0, 31),
                (0, 31),
                (0, 31),
                (0, 31),
                (0, 31),
                (0, 31),
            ]
        )
        self.hp_filter.set_tuple(
            iv_filters[0]
        )
        self.atk_filter.set_tuple(
            iv_filters[1]
        )
        self.def_filter.set_tuple(
            iv_filters[2]
        )
        self.spa_filter.set_tuple(
            iv_filters[3]
        )
        self.spd_filter.set_tuple(
            iv_filters[4]
        )
        self.spe_filter.set_tuple(
            iv_filters[5]
        )

    @staticmethod
    def load_combobox(combobox: CheckedCombobox | ListViewCombobox, filter_json: dict, key: str):
        """Load combobox from filter_json"""
        filter_data = filter_json.get(key, [])
        if isinstance(combobox, CheckedCombobox):
            for variable, value in zip(
                combobox.dropdown_menu.variables,
                combobox.dropdown_menu.values
            ):
                variable.set(value in filter_data)
            combobox.dropdown_callback()
        else:
            combobox.clear()
            for value in filter_data:
                combobox.add_item(value)

    def get_filters(self):
        """Get a list of all filters in the filters directory"""
        return [
            file.split("/")[-1].split("\\")[-1]
            for file in glob.glob(get_path("./resources/filter_settings/*.json"))
        ]

    def get_filter_objects(self) -> list[RaidFilter]:
        """Get a list of all filtesr as RaidFilters"""
        filters = []
        for filename in glob.glob(get_path("./resources/filter_settings/*.json")):
            with open(filename, "r", encoding="utf-8") as file:
                filters.append(
                    RaidFilter.from_json(json.load(file))
                )
        return filters
