"""Live Map GUI"""

import customtkinter
from sv_live_map_core.nxreader import NXReader
from sv_live_map_core.paldea_map_view import PaldeaMapView

customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")

class Application(customtkinter.CTk):
    """Live Map GUI"""
    APP_NAME = "SV Live Map"
    WIDTH = 800
    HEIGHT = 512

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initialize for later
        self.reader: NXReader = None

        # window settings
        self.title(self.APP_NAME)
        self.geometry(str(self.WIDTH) + "x" + str(self.HEIGHT))
        self.minsize(self.WIDTH, self.HEIGHT)

        # handle closing the application
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.settings_frame = customtkinter.CTkFrame(
            master = self,
            width = 150,
            corner_radius = 0,
            fg_color = None,
        )

        self.settings_frame.grid(
            row = 0,
            column = 1,
            rowspan = 1,
            pady = 0,
            padx = 0,
            sticky = "nsew"
        )

        self.map_frame = customtkinter.CTkFrame(
            master = self,
            width = 150,
            corner_radius = 0,
            fg_color = None,
        )

        self.map_frame.grid(
            row = 0,
            column = 2,
            rowspan = 1,
            pady = 0,
            padx = 0,
            sticky = "nsew"
        )

        self.map_widget = PaldeaMapView(self.map_frame)
        self.map_widget.grid(
            row = 1,
            rowspan = 1,
            column = 0,
            columnspan = 1,
            sticky = "nw",
            padx = (0, 0),
            pady = (0, 0)
        )

    def on_closing(self, _ = None):
        """Handle closing of the application"""
        if self.reader:
            self.reader.close()
        self.destroy()

def main():
    """Main function of the appliation"""
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
