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
    TeraTypeGeneration,
    AbilityGeneration,
    NatureGeneration,
    IVGeneration,
    Nature,
    Game,
)
from .raid_enemy_table_array import RaidEnemyTableArray, RaidEnemyInfo

RAID_COUNT = 72

def is_shiny(pid: int, sidtid: int):
    """Check if a given pid is shiny"""
    temp = pid ^ sidtid
    return ((temp & 0xFFFF) ^ (temp >> 16)) < 0x10

def calc_difficulty(story_progress: StoryProgress, difficulty_rand: int) -> StarLevel:
    """Calculate raid difficulty from story progress and difficulty rand"""
    match story_progress:
        case StoryProgress.DEFAULT:
            if difficulty_rand <= 80:
                return StarLevel.ONE_STAR
            # elif (difficulty_rand - 80) <= 20
            return StarLevel.TWO_STAR
        case StoryProgress.THREE_STAR_UNLOCKED:
            if difficulty_rand <= 30:
                return StarLevel.ONE_STAR
            if difficulty_rand <= 70: # elif (difficulty_rand - 30) <= 40
                return StarLevel.TWO_STAR
            # elif (difficulty_rand - 30 - 40) <= 30
            return StarLevel.THREE_STAR
        case StoryProgress.FOUR_STAR_UNLOCKED:
            if difficulty_rand <= 20:
                return StarLevel.ONE_STAR
            if difficulty_rand <= 40: # elif (difficulty_rand - 20) <= 20
                return StarLevel.TWO_STAR
            if difficulty_rand <= 70: # elif (difficulty_rand - 20 - 20) <= 30
                return StarLevel.THREE_STAR
            # elif (difficulty_rand - 20 - 20 - 30) <= 30
            return StarLevel.FOUR_STAR
        case StoryProgress.FIVE_STAR_UNLOCKED:
            if difficulty_rand <= 40:
                return StarLevel.THREE_STAR
            if difficulty_rand <= 75: # elif (difficulty_rand - 40) <= 35
                return StarLevel.FOUR_STAR
            # elif (difficulty_rand - 40 - 35) <= 25
            return StarLevel.FIVE_STAR
        case StoryProgress.SIX_STAR_UNLOCKED:
            if difficulty_rand <= 30:
                return StarLevel.THREE_STAR
            if difficulty_rand <= 70: # elif (difficulty_rand - 30) <= 40
                return StarLevel.FOUR_STAR
            # elif (difficulty_rand - 30 - 40) <= 30
            return StarLevel.FIVE_STAR
    return None

@dataclass
class TeraRaid:
    """Single Tera Raid Data"""
    # information directly present in raid block
    is_enabled: U32
    area_id: U32
    display_type: U32
    den_id: U32
    seed: U32
    _unused_14: U32
    content: U32
    collected_league_points: U32

    def __post_init__(self) -> None:
        # information that needs to be derived
        self.delivery_group_id: int = None
        self.tera_type: TeraType = None
        self.difficulty: StarLevel = None
        self.raid_enemy_info: RaidEnemyInfo = None
        self.species: Species = None
        self.form: int = None
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
        # TODO: support default event settings if ever used
        self.raid_enemy_info = raid_enemy_info
        if self.raid_enemy_info.difficulty:
            self.difficulty = self.raid_enemy_info.difficulty
        if self.raid_enemy_info.boss_poke_para.gem_type \
          and self.raid_enemy_info.boss_poke_para.gem_type >= TeraTypeGeneration.NORMAL:
            self.tera_type = TeraType.from_generation(self.raid_enemy_info.boss_poke_para.gem_type)
        self.species = raid_enemy_info.boss_poke_para.dev_id
        self.form = raid_enemy_info.boss_poke_para.form_id

        rng = Xoroshiro128Plus(self.seed)
        self.encryption_constant = rng.rand(0xFFFFFFFF)
        self.sidtid = rng.rand(0xFFFFFFFF)
        self.pid = rng.rand(0xFFFFFFFF)
        self.is_shiny = is_shiny(self.pid, self.sidtid)

        match raid_enemy_info.boss_poke_para.talent_type:
            case IVGeneration.RANDOM_IVS:
                self.ivs = tuple(rng.rand(32) for _ in range(6))
            case IVGeneration.SET_GUARANTEED_IVS:
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
            case IVGeneration.SET_IVS:
                self.ivs = (
                    raid_enemy_info.boss_poke_para.talent_value.hp,
                    raid_enemy_info.boss_poke_para.talent_value.atk,
                    raid_enemy_info.boss_poke_para.talent_value.def_,
                    raid_enemy_info.boss_poke_para.talent_value.spa,
                    raid_enemy_info.boss_poke_para.talent_value.spd,
                    raid_enemy_info.boss_poke_para.talent_value.spe
                )

        match raid_enemy_info.boss_poke_para.tokusei:
            case AbilityGeneration.RANDOM_12 | None:
                self.ability = rng.rand(2) + 1
            case AbilityGeneration.RANDOM_12HA:
                self.ability = rng.rand(3) + 1
            case AbilityGeneration.ABILITY_1:
                self.ability = 1
            case AbilityGeneration.ABILITY_2:
                self.ability = 2
            case AbilityGeneration.ABILITY_HA:
                self.ability = 3
        self.gender = rng.rand(100)
        if raid_enemy_info.boss_poke_para.seikaku:
            self.nature = Nature.from_generation(raid_enemy_info.boss_poke_para.seikaku)
        else:
            # TODO: Toxtricity?
            self.nature = Nature(rng.rand(25))
        # TODO: label weight/height/scale, deal with forced size ranges
        self.size0 = rng.rand(0x81) + rng.rand(0x80)
        self.size1 = rng.rand(0x81) + rng.rand(0x80)
        self.size2 = rng.rand(0x81) + rng.rand(0x80)

    def initialize_data(
        self,
        raid_enemy_table_arrays: tuple[RaidEnemyTableArray],
        story_progress: StoryProgress,
        game: Game,
        delivery_group_id: int
    ):
        """Initialize raid with derived information"""
        self.delivery_group_id = delivery_group_id

        # rng object used only for tera type
        rng_tera = Xoroshiro128Plus(self.seed)
        self.tera_type = TeraType(rng_tera.rand(18))

        # rng object used for difficulty and slot
        rng_slot = Xoroshiro128Plus(self.seed)

        self.is_event = self.content >= 2

        # TODO: do 7 stars still do the rand(100)? (will this ever matter?)
        if self.content == 1:
            self.difficulty = StarLevel.SIX_STAR
        elif self.content == 3:
            self.difficulty = StarLevel.SEVEN_STAR
        else:
            difficulty_rand = rng_slot.rand(100)
            self.difficulty = calc_difficulty(story_progress, difficulty_rand)

        if self.is_event:
            raid_enemy_table_array = raid_enemy_table_arrays[-1]
            encounter_slot_total = sum(
                (
                    table.raid_enemy_info.rate for table in raid_enemy_table_array.raid_enemy_tables
                    if table.raid_enemy_info.delivery_group_id == self.delivery_group_id and
                        (
                            table.raid_enemy_info.difficulty is None
                            or table.raid_enemy_info.difficulty.is_unlocked(story_progress)
                        ) and
                        table.raid_enemy_info.rom_ver in (None, game, Game.BOTH)
                )
            )
        else:
            raid_enemy_table_array = raid_enemy_table_arrays[self.difficulty]
            encounter_slot_total = sum(
                (
                    table.raid_enemy_info.rate for table in raid_enemy_table_array.raid_enemy_tables
                    if table.raid_enemy_info.rom_ver in (None, game, Game.BOTH)
                )
            )

        encounter_slot_rand = rng_slot.rand(encounter_slot_total)
        for table in raid_enemy_table_array.raid_enemy_tables:
            if (table.raid_enemy_info.delivery_group_id in (None, self.delivery_group_id) and
              (
                table.raid_enemy_info.difficulty is None
                or table.raid_enemy_info.difficulty.is_unlocked(story_progress)
              ) and
              table.raid_enemy_info.rom_ver in (None, game, Game.BOTH)):
                if encounter_slot_rand < table.raid_enemy_info.rate:
                    self.generate_pokemon(table.raid_enemy_info)
                    break
                encounter_slot_rand -= table.raid_enemy_info.rate

    def __str__(self) -> str:
        if not self.is_enabled:
            return "Empty Den"
        return f"{self.difficulty=!r} " \
               f"{self.species=!r}{f'-{self.form}' if self.form else ''} " \
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
        story_progress: StoryProgress,
        game: Game,
        delivery_raid_priority: tuple[int]
    ) -> None:
        """Initialize each raid with derived information"""
        for i, raid in enumerate(self.raids):
            # check the event delivery group
            den_delivery_group_id = None
            for delivery_group_id, delivery_group_size in enumerate(delivery_raid_priority):
                if i < delivery_group_size:
                    den_delivery_group_id = delivery_group_id
                    break
                i -= delivery_group_size
            raid.initialize_data(
                raid_enemy_table_arrays,
                story_progress,
                game,
                den_delivery_group_id
            )

def process_raid_block(raid_block: bytes) -> RaidBlock:
    """Process raid block with bytechomp"""
    reader = Reader[RaidBlock](ByteOrder.LITTLE).allocate()
    reader.feed(raid_block)
    assert reader.is_complete(), "Invalid data size"
    return reader.build()
