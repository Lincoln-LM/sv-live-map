"""customtkinter widget for displaying an image"""

import customtkinter
from PIL import ImageTk

class ImageWidget(customtkinter.CTkFrame):
    # pylint: disable=too-many-ancestors
    """customtkinter widget for displaying an image"""
    def __init__(
        self,
        *args,
        master = None,
        image: ImageTk.PhotoImage = None,
        **kwargs
    ):
        assert image is not None
        super().__init__(
            *args,
            master = master,
            width = image.width(),
            height = image.height(),
            corner_radius = 0,
            **kwargs
        )
        self.canvas.create_image(0, 0, anchor = "nw", image = image)
