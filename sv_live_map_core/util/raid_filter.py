"""Filter for TeraRaids"""

from ..save.raid_block import TeraRaid
from ..enums import AbilityIndex, Gender, Nature, Species, StarLevel, Item


class RaidFilter:
    """Filter for TeraRaids"""
    ANY_IV = range(0, 31)
    ANY_ABILITY = list(AbilityIndex)
    ANY_GENDER = list(Gender)
    ANY_NATURE = list(Nature)
    ANY_SPECIES = list(Species)
    ANY_DIFFICULTY = list(StarLevel)
    ANY_REWARD = list(Item)

    def __init__(
        self,
        hp_filter: range = None,
        atk_filter: range = None,
        def_filter: range = None,
        spa_filter: range = None,
        spd_filter: range = None,
        spe_filter: range = None,
        ability_filter: list[AbilityIndex] = None,
        gender_filter: list[Gender] = None,
        nature_filter: list[Nature] = None,
        species_filter: list[Species] = None,
        shiny_filter: bool = False,
        star_filter: list[StarLevel] = None,
        reward_filter: list[Item] = None,
        reward_count_filter: int = None,
    ) -> None:
        self.hp_filter = hp_filter or self.ANY_IV
        self.atk_filter = atk_filter or self.ANY_IV
        self.def_filter = def_filter or self.ANY_IV
        self.spa_filter = spa_filter or self.ANY_IV
        self.spd_filter = spd_filter or self.ANY_IV
        self.spe_filter = spe_filter or self.ANY_IV
        self.ability_filter = ability_filter or self.ANY_ABILITY.copy()
        self.gender_filter = gender_filter or self.ANY_GENDER.copy()
        self.nature_filter = nature_filter or self.ANY_NATURE.copy()
        self.species_filter = species_filter or self.ANY_SPECIES.copy()
        self.shiny_filter = shiny_filter
        self.star_filter = star_filter or self.ANY_DIFFICULTY.copy()
        self.reward_filter = reward_filter or self.ANY_REWARD.copy()
        self.reward_count_filter = reward_count_filter or 0

    @property
    def iv_filters(self) -> list[range]:
        """All IV filters together in one list"""
        return [
            self.hp_filter,
            self.atk_filter,
            self.def_filter,
            self.spa_filter,
            self.spd_filter,
            self.spe_filter
        ]

    def compare(self, raid: TeraRaid) -> bool:
        """Compare raid to filters"""
        for iv_filter, iv_val in zip(self.iv_filters, raid.ivs):
            if iv_val not in iv_filter:
                return False

        if raid.ability_index not in self.ability_filter:
            return False

        if raid.gender not in self.gender_filter:
            return False

        if raid.nature not in self.nature_filter:
            return False

        if raid.species not in self.species_filter:
            return False

        if raid.difficulty not in self.star_filter:
            return False

        if (
            sum(
                reward[1] for reward in raid.rewards if reward[0] in self.reward_filter
            )
            < self.reward_count_filter
        ):
            return False

        return bool(not self.shiny_filter or raid.is_shiny)
