"""Window for displaying raid rewards"""

import customtkinter
from ..util.item_sprite_handler import ItemSpriteHandler
from ..save.raid_block import TeraRaid
from ..enums import Item, RaidRewardItemSubjectType, SandwichLevel
from ..widget.image_widget import ImageWidget


class RewardWindow(customtkinter.CTkToplevel):
    """Window for displaying raid rewards"""
    ITEM_SPRITE_HANDLER: ItemSpriteHandler = None

    def __init__(
        self,
        *args,
        raid_data: TeraRaid = None,
        fg_color = "default_theme",
        **kwargs
    ):
        super().__init__(
            *args,
            fg_color = fg_color,
            **kwargs
        )
        assert raid_data is not None
        self.raid_data = raid_data

        self.item_sprite_handler = RewardWindow.ITEM_SPRITE_HANDLER or ItemSpriteHandler(True)
        RewardWindow.ITEM_SPRITE_HANDLER = self.item_sprite_handler
        self.title(
            f"Shiny {self.raid_data.species} ★ Rewards"
            if self.raid_data.is_shiny
            else f"{self.raid_data.species} Rewards"
        )
        for row, reward in enumerate(self.raid_data.rewards):
            self.draw_reward(reward, row)

    def draw_reward(
        self,
        reward: tuple[Item, int, RaidRewardItemSubjectType, SandwichLevel],
        row: int
    ):
        """Draw representation of reward"""
        item_id, count, subject_type, sandwich_level = reward
        item_image = ImageWidget(
            master = self,
            image = self.item_sprite_handler.grab_sprite(item_id),
            fg_color = self.fg_color
        )
        item_image.grid(row = row, column = 0, padx = 10)
        item_text = customtkinter.CTkLabel(master = self, text = f"{item_id} x {count}")
        item_text.grid(row = row, column = 1, padx = 10)
        item_subject_text = customtkinter.CTkLabel(master = self, text = str(subject_type))
        item_subject_text.grid(row = row, column = 2, padx = 10)
        item_sandwich_level_text = customtkinter.CTkLabel(master = self, text = str(sandwich_level))
        item_sandwich_level_text.grid(row = row, column = 3, padx = 10)
