"""IV filter widget"""

import customtkinter

class IVFilterWidget(customtkinter.CTkFrame):
    """IV filter widget"""
    def __init__(
        self,
        *args,
        title: str = "IV",
        width: int = 100,
        height: int = 32,
        **kwargs
    ):
        super().__init__(*args, width = width, height = height, **kwargs)

        self.title_label = customtkinter.CTkLabel(self, width = 35, text = f"{title}:")
        self.title_label.pack(side = "left")

        self.min_entry = customtkinter.CTkEntry(self, width = 28, justify = "center")
        self.min_entry.pack(side = "left")
        self.min_entry.insert(0, "0")

        self.sep_label = customtkinter.CTkLabel(self, width = 28, text = "~")
        self.sep_label.pack(side = "left")

        self.max_entry = customtkinter.CTkEntry(self, width = 28, justify = "center")
        self.max_entry.pack(side = "left")
        self.max_entry.insert(0, "31")

    def get(self) -> range:
        """Get range of IV filter"""
        return range(int(self.min_entry.get()), int(self.max_entry.get()) + 1)
