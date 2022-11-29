"""Raid Block Data specification
   https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/Saves/Substructures/Gen9/RaidSpawnList9.cs
"""

from dataclasses import dataclass
from bytechomp import Annotated, ByteOrder, Reader
from bytechomp.datatypes import U32, U64
from .rng import Xoroshiro128Plus
from .sv_enums import (
    StoryProgress,
    StarLevel,
    TeraType,
    Species,
    AbilityGeneration,
    Nature,
)
from .raid_enemy_table_array import RaidEnemyTableArray, RaidEnemyInfo

RAID_COUNT = 72

def is_shiny(pid: int, sidtid: int):
    """Check if a given pid is shiny"""
    temp = pid ^ sidtid
    return ((temp & 0xFFFF) ^ (temp >> 16)) < 0x10

@dataclass
class TeraRaid:
    """Single Tera Raid Data"""
    is_enabled: U32
    area_id: U32
    display_type: U32
    den_id: U32
    seed: U32
    _unused_14: U32
    content: U32
    collected_league_points: U32

    def __post_init__(self) -> None:
        self.tera_type: TeraType = None
        self.difficulty: StarLevel = None
        self.raid_enemy_info: RaidEnemyInfo = None
        self.species: Species
        self.is_event: bool = None
        self.encryption_constant: int = None
        self.pid: int = None
        self.sidtid: int = None
        self.is_shiny: bool = None
        self.ivs: tuple[int, 6] = None
        # TODO: check gender ratios and ability ids from personal info
        # to get better values for these (enum)
        self.ability: int = None
        self.gender: int = None
        self.nature: Nature = None
        self.size0: int = None
        self.size1: int = None
        self.size2: int = None

    def generate_pokemon(self, raid_enemy_info: RaidEnemyInfo):
        """Derive pokemon data from seed and slot"""
        self.raid_enemy_info = raid_enemy_info
        self.species = raid_enemy_info.boss_poke_para.dev_id

        rng = Xoroshiro128Plus(self.seed)
        self.encryption_constant = rng.rand(0xFFFFFFFF)
        self.sidtid = rng.rand(0xFFFFFFFF)
        self.pid = rng.rand(0xFFFFFFFF)
        self.is_shiny = is_shiny(self.pid, self.sidtid)

        temp_ivs = [-1 for _ in range(6)]
        for i in range(raid_enemy_info.boss_poke_para.talent_vnum or 0):
            index = rng.rand(6)
            while temp_ivs[index] != -1:
                index = rng.rand(6)
            temp_ivs[index] = 31
        for i in range(6):
            if temp_ivs[i] == -1:
                temp_ivs[i] = rng.rand(32)

        self.ivs = tuple(temp_ivs)
        match raid_enemy_info.boss_poke_para.tokusei:
            case AbilityGeneration.RANDOM_12 | None:
                self.ability = rng.rand(2)
            case AbilityGeneration.RANDOM_12HA:
                self.ability = rng.rand(3)
            case AbilityGeneration.ABILITY_1:
                self.ability = 1
            case AbilityGeneration.ABILITY_2:
                self.ability = 2
            case AbilityGeneration.ABILITY_HA:
                self.ability = 3
        self.gender = rng.rand(100)
        # TODO: Toxtricity?
        self.nature = Nature(rng.rand(25))
        # TODO: label weight/height/scale, deal with forced size ranges
        self.size0 = rng.rand(0x81) + rng.rand(0x80)
        self.size1 = rng.rand(0x81) + rng.rand(0x80)
        self.size2 = rng.rand(0x81) + rng.rand(0x80)

    def initialize_data(
        self,
        raid_enemy_table_arrays: tuple[RaidEnemyTableArray],
        story_progress: StoryProgress
    ):
        """Initialize raid with derived information"""
        # rng object used only for tera type
        rng_tera = Xoroshiro128Plus(self.seed)
        self.tera_type = TeraType(rng_tera.rand(18))

        # rng object used for difficulty and slot
        rng_slot = Xoroshiro128Plus(self.seed)

        self.is_event = self.content == 2

        if self.content == 1:
            self.difficulty = StarLevel.SIX_STAR
        else:
            difficulty_rand = rng_slot.rand(100)
            match story_progress:
                case StoryProgress.DEFAULT:
                    if difficulty_rand <= 80:
                        self.difficulty = StarLevel.ONE_STAR
                    else: # elif (difficulty_rand - 80) <= 20
                        self.difficulty = StarLevel.TWO_STAR
                case StoryProgress.THREE_STAR_UNLOCKED:
                    if difficulty_rand <= 30:
                        self.difficulty = StarLevel.ONE_STAR
                    elif difficulty_rand <= 70: # elif (difficulty_rand - 30) <= 40
                        self.difficulty = StarLevel.TWO_STAR
                    else: # elif (difficulty_rand - 30 - 40) <= 30
                        self.difficulty = StarLevel.THREE_STAR
                case StoryProgress.FOUR_STAR_UNLOCKED:
                    if difficulty_rand <= 20:
                        self.difficulty = StarLevel.ONE_STAR
                    elif difficulty_rand <= 40: # elif (difficulty_rand - 20) <= 20
                        self.difficulty = StarLevel.TWO_STAR
                    elif difficulty_rand <= 70: # elif (difficulty_rand - 20 - 20) <= 30
                        self.difficulty = StarLevel.THREE_STAR
                    else:
                        self.difficulty = StarLevel.FOUR_STAR
                case StoryProgress.FIVE_STAR_UNLOCKED:
                    if difficulty_rand <= 40:
                        self.difficulty = StarLevel.THREE_STAR
                    elif difficulty_rand <= 75: # elif (difficulty_rand - 40) <= 35
                        self.difficulty = StarLevel.FOUR_STAR
                    else: # elif (difficulty_rand - 40 - 35) <= 25
                        self.difficulty = StarLevel.FIVE_STAR
                case StoryProgress.SIX_STAR_UNLOCKED:
                    if difficulty_rand <= 30:
                        self.difficulty = StarLevel.THREE_STAR
                    elif difficulty_rand <= 70: # elif (difficulty_rand - 30) <= 40
                        self.difficulty = StarLevel.FOUR_STAR
                    else: # elif (difficulty_rand - 30 - 40) <= 30
                        self.difficulty = StarLevel.FIVE_STAR

        if self.is_event:
            raid_enemy_table_array = raid_enemy_table_arrays[-1]
            encounter_slot_total = sum(
                (
                    table.raid_enemy_info.rate for table in raid_enemy_table_array.raid_enemy_tables
                    if table.raid_enemy_info.difficulty == self.difficulty
                )
            )
        else:
            raid_enemy_table_array = raid_enemy_table_arrays[self.difficulty]
            encounter_slot_total = sum(
                (table.raid_enemy_info.rate for table in raid_enemy_table_array.raid_enemy_tables)
            )

        encounter_slot_rand = rng_slot.rand(encounter_slot_total)

        for table in raid_enemy_table_array.raid_enemy_tables:
            if encounter_slot_rand <= table.raid_enemy_info.rate:
                self.generate_pokemon(table.raid_enemy_info)
                break
            encounter_slot_rand -= table.raid_enemy_info.rate

    def __str__(self) -> str:
        if not self.is_enabled:
            return "Empty Den"
        return f"{self.difficulty=!r} " \
               f"{self.species=!r} " \
               f"{self.area_id=} " \
               f"{self.den_id=} " \
               f"{self.is_shiny=} " \
               f"{self.ivs=} "

@dataclass
class RaidBlock:
    """Full Raid Block Data"""
    current_seed: U64
    tomorrow_seed: U64
    raids: Annotated[list[TeraRaid], RAID_COUNT]

    def initialize_data(
        self,
        raid_enemy_table_arrays: tuple[RaidEnemyTableArray],
        story_progress: StoryProgress
    ) -> None:
        """Initialize each raid with derived information"""
        for raid in self.raids:
            raid.initialize_data(raid_enemy_table_arrays, story_progress)

def process_raid_block(raid_block: bytes) -> RaidBlock:
    """Process raid block with bytechomp"""
    reader = Reader[RaidBlock](ByteOrder.LITTLE).allocate()
    reader.feed(raid_block)
    assert reader.is_complete(), "Invalid data size"
    return reader.build()
