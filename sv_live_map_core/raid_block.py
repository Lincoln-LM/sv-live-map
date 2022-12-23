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
    GenderGeneration,
    ShinyGeneration,
    Nature,
    Game,
    Ability,
    Gender,
    AbilityIndex,
)
from .raid_enemy_table_array import RaidEnemyTableArray, RaidEnemyTable, RaidEnemyInfo
from .personal_data_handler import PersonalDataHandler
from .my_status_9 import MyStatus9

RAID_COUNT = 72
TOXTRICITY_AMPED_NATURES = (
    Nature.ADAMANT,
    Nature.NAUGHTY,
    Nature.BRAVE,
    Nature.IMPISH,
    Nature.LAX,
    Nature.RASH,
    Nature.SASSY,
    Nature.HASTY,
    Nature.JOLLY,
    Nature.NAIVE,
    Nature.HARDY,
    Nature.DOCILE,
    Nature.QUIRKY,
)
TOXTRICITY_LOWKEY_NATURES = (
    Nature.LONELY,
    Nature.BOLD,
    Nature.RELAXED,
    Nature.TIMID,
    Nature.SERIOUS,
    Nature.MODEST,
    Nature.MILD,
    Nature.QUIET,
    Nature.BASHFUL,
    Nature.CALM,
    Nature.GENTLE,
    Nature.CAREFUL,
)

def shiny_xor(pid: int, sidtid: int) -> int:
    """Get shiny XOR"""
    temp = pid ^ sidtid
    return (temp & 0xFFFF) ^ (temp >> 16)

def is_shiny(pid: int, sidtid: int) -> bool:
    """Check if a given pid is shiny"""
    return shiny_xor(pid, sidtid) < 0x10

def force_shininess(
    lock_type: ShinyGeneration,
    fake_pid: int,
    fake_sidtid: int,
    sidtid: int
) -> int:
    """Force a pid to be shiny/non shiny if applicable"""
    # if pokemon is supposed to be shiny for the trainer
    if (
        # naturally rolled shiny
        (lock_type in (None, ShinyGeneration.RANDOM_SHININESS) and is_shiny(fake_pid, fake_sidtid))
        # or forced to be shiny
        or lock_type == ShinyGeneration.FORCED_SHINY
    ):
        return (
            # if fake pid happens to be shiny for trainer
            fake_pid
            if is_shiny(fake_pid, sidtid)
            # otherwise force shiny
            else (
                (
                    (
                        (sidtid & 0xFFFF)
                        ^ (sidtid >> 16)
                        ^ (fake_pid & 0xFFFF)
                        ^ bool(shiny_xor(fake_pid, fake_sidtid))
                    )
                    << 16
                )
                | (fake_pid & 0xFFFF)
            )
        )
    # pokemon is not supposed to be shiny for trainer, correct it if it is
    return fake_pid ^ 0x10000000 if is_shiny(fake_pid, sidtid) else fake_pid


def calc_difficulty(story_progress: StoryProgress, difficulty_rand: int) -> StarLevel:
    """Calculate raid difficulty from story progress and difficulty rand"""
    match story_progress:
        case StoryProgress.DEFAULT:
            return (
                StarLevel.ONE_STAR
                if difficulty_rand <= 80
                else StarLevel.TWO_STAR # elif (difficulty_rand - 80) <= 20
            )
        case StoryProgress.THREE_STAR_UNLOCKED:
            return (
                StarLevel.ONE_STAR
                if difficulty_rand <= 30
                else (
                    StarLevel.TWO_STAR # elif (difficulty_rand - 30) <= 40
                    if difficulty_rand <= 70
                    else
                    StarLevel.THREE_STAR # elif (difficulty_rand - 30 - 40) <= 30
                )
            )
        case StoryProgress.FOUR_STAR_UNLOCKED:
            return (
                StarLevel.ONE_STAR
                if difficulty_rand <= 20
                else (
                    StarLevel.TWO_STAR # elif (difficulty_rand - 20) <= 20
                    if difficulty_rand <= 40
                    else (
                        StarLevel.THREE_STAR # elif (difficulty_rand - 20 - 20) <= 30
                        if difficulty_rand <= 70
                        else
                        StarLevel.FOUR_STAR
                    )
                )
            )
        case StoryProgress.FIVE_STAR_UNLOCKED:
            return (
                StarLevel.THREE_STAR
                if difficulty_rand <= 40
                else (
                    StarLevel.FOUR_STAR # elif (difficulty_rand - 40) <= 35
                    if difficulty_rand <= 75
                    else
                    StarLevel.FIVE_STAR # elif (difficulty_rand - 40 - 35) <= 25
                )
            )
        case StoryProgress.SIX_STAR_UNLOCKED:
            return (
                StarLevel.THREE_STAR
                if difficulty_rand <= 30
                else (
                    StarLevel.FOUR_STAR # elif (difficulty_rand - 30) <= 40
                    if difficulty_rand <= 70
                    else
                    StarLevel.FIVE_STAR # elif (difficulty_rand - 30 - 40) <= 30
                )
            )
    return None

@dataclass
class TeraRaid:
    """Single Tera Raid Data"""
    # pylint: disable=too-many-instance-attributes
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

        self.ability: Ability = None
        self.ability_index: AbilityIndex = None
        self.gender: Gender = None

        self.nature: Nature = None
        self.height: int = None
        self.weight: int = None
        self.scale: int = None

        # for map display
        self.id_str: str = f"{self.area_id}-{self.den_id}"

        # tid/sid used for pid generation
        self.my_status: MyStatus9 = None

        self.hide_sensitive_info: bool = False # Default to false. Override later if needed

    def generate_pokemon(self, raid_enemy_info: RaidEnemyInfo):
        """Derive pokemon data from seed and slot"""
        self.raid_enemy_info = raid_enemy_info

        # events who force their own difficulty
        if self.raid_enemy_info.difficulty is not None:
            self.difficulty = self.raid_enemy_info.difficulty

        # slot directly determines species + form
        self.species = raid_enemy_info.boss_poke_para.dev_id
        self.form = raid_enemy_info.boss_poke_para.form_id

        # own rng
        self.tera_type = self.rand_tera_type()

        # main rng
        rng = Xoroshiro128Plus(self.seed)
        self.encryption_constant = rng.rand()
        self.sidtid = rng.rand()
        self.pid = self.rand_pid(rng)
        self.is_shiny = is_shiny(self.pid, self.my_status.full_id)
        self.ivs = self.rand_ivs(rng)
        self.ability_index, self.ability = self.rand_ability(rng)
        self.gender = self.rand_gender(rng)
        self.nature = self.rand_nature(rng)
        self.height = self.rand_size(rng)
        self.weight = self.rand_size(rng)
        self.scale = self.rand_size(rng)

    def rand_pid(self, rng: Xoroshiro128Plus) -> int:
        """Generate shiny-corrected pid"""
        return force_shininess(
            self.raid_enemy_info.boss_poke_para.rare_type,
            rng.rand(),
            self.sidtid,
            self.my_status.full_id
        )

    def rand_tera_type(self) -> TeraType:
        """Generate tera type"""
        match self.raid_enemy_info.boss_poke_para.gem_type:
            case None | TeraTypeGeneration.NONE | TeraTypeGeneration.RANDOM:
                # rng object used only for tera type
                rng_tera = Xoroshiro128Plus(self.seed)
                return TeraType(rng_tera.rand(18))
            case _:
                return TeraType.from_generation(self.raid_enemy_info.boss_poke_para.gem_type)

    def rand_ivs(self, rng: Xoroshiro128Plus) -> tuple:
        """Generate ivs"""
        match self.raid_enemy_info.boss_poke_para.talent_type:
            case IVGeneration.RANDOM_IVS:
                return tuple(rng.rand(32) for _ in range(6))
            case IVGeneration.SET_GUARANTEED_IVS:
                temp_ivs = [-1 for _ in range(6)]
                for _ in range(self.raid_enemy_info.boss_poke_para.talent_vnum or 0):
                    index = rng.rand(6)
                    while temp_ivs[index] != -1:
                        index = rng.rand(6)
                    temp_ivs[index] = 31
                for i in range(6):
                    if temp_ivs[i] == -1:
                        temp_ivs[i] = rng.rand(32)
                return tuple(temp_ivs)
            case IVGeneration.SET_IVS:
                return (
                    self.raid_enemy_info.boss_poke_para.talent_value.hp,
                    self.raid_enemy_info.boss_poke_para.talent_value.atk,
                    self.raid_enemy_info.boss_poke_para.talent_value.def_,
                    self.raid_enemy_info.boss_poke_para.talent_value.spa,
                    self.raid_enemy_info.boss_poke_para.talent_value.spd,
                    self.raid_enemy_info.boss_poke_para.talent_value.spe
                )

    def rand_ability(self, rng: Xoroshiro128Plus) -> tuple[AbilityIndex, Ability]:
        """Generate ability"""
        raid_fixed_ability = self.raid_enemy_info.boss_poke_para.tokusei
        match raid_fixed_ability:
            case AbilityGeneration.RANDOM_12 | None:
                index = AbilityIndex(rng.rand(2))
            case AbilityGeneration.RANDOM_12HA:
                index = AbilityIndex(rng.rand(3))
            case _:
                index = raid_fixed_ability.to_ability_index()
        return (
            index,
            PersonalDataHandler.get_ability(
                self.species,
                self.form,
                index
            )
        )

    def rand_gender(self, rng: Xoroshiro128Plus) -> Gender:
        """Generate gender"""
        raid_fixed_gender = self.raid_enemy_info.boss_poke_para.sex
        match raid_fixed_gender:
            case None | GenderGeneration.RANDOM_GENDER:
                species_fixed_gender = PersonalDataHandler.fixed_gender(self.species, self.form)
                match species_fixed_gender:
                    case GenderGeneration.RANDOM_GENDER:
                        return PersonalDataHandler.get_gender(
                            self.species,
                            self.form,
                            rng.rand(100)
                        )
                    case _:
                        return Gender.from_generation(species_fixed_gender)
            case _:
                return Gender.from_generation(raid_fixed_gender)

    def rand_nature(self, rng: Xoroshiro128Plus) -> Nature:
        """Generate nature"""
        raid_fixed_nature = self.raid_enemy_info.boss_poke_para.seikaku
        match raid_fixed_nature:
            case None | NatureGeneration.NONE:
                if self.species == Species.TOXTRICITY:
                    match self.form:
                        case 0: # amped
                            return TOXTRICITY_AMPED_NATURES[rng.rand(13)]
                        case 1: # lowkey
                            return TOXTRICITY_LOWKEY_NATURES[rng.rand(12)]
                return Nature(rng.rand(25))
            case _:
                return Nature.from_generation(raid_fixed_nature)

    def rand_size(self, rng: Xoroshiro128Plus) -> int:
        """Generate size scalar"""
        # TODO: deal with forced size ranges
        return rng.rand(0x81) + rng.rand(0x80)

    def initialize_data(
        self,
        raid_enemy_table_arrays: tuple[RaidEnemyTableArray],
        story_progress: StoryProgress,
        game: Game,
        my_status: MyStatus9,
        delivery_group_id: int
    ):
        """Initialize raid with derived information"""
        # based on position in full raid list
        self.delivery_group_id = delivery_group_id
        self.is_event = self.content >= 2

        # tid/sid used for pid generation
        self.my_status = my_status

        # rng object used for difficulty and slot
        rng_slot = Xoroshiro128Plus(self.seed)

        self.difficulty = self.rand_difficulty(story_progress, rng_slot)

        possible_encounter_slots, encounter_slot_total = \
            self.build_encounter_table(raid_enemy_table_arrays, story_progress, game)

        self.generate_from_slots(rng_slot, possible_encounter_slots, encounter_slot_total)

    def rand_difficulty(
        self,
        story_progress: StoryProgress,
        rng_slot: Xoroshiro128Plus
    ) -> StarLevel:
        """Set difficulty based on raid and progress"""
        if self.content == 1:
            # difficulty_rand does not happen
            return StarLevel.SIX_STAR
        difficulty_rand = rng_slot.rand(100)
        if self.is_event:
            # difficulty_rand unused but still happens
            return StarLevel.EVENT
        return calc_difficulty(story_progress, difficulty_rand)

    def generate_from_slots(
        self,
        rng_slot: Xoroshiro128Plus,
        possible_encounter_slots: list[RaidEnemyTable],
        encounter_slot_total: int
    ):
        """Generate pokemon based on possible slots"""
        encounter_slot_rand = rng_slot.rand(encounter_slot_total)
        for table in possible_encounter_slots:
            if encounter_slot_rand < table.raid_enemy_info.rate:
                self.generate_pokemon(table.raid_enemy_info)
                break
            encounter_slot_rand -= table.raid_enemy_info.rate

    def build_encounter_table(
        self,
        raid_enemy_table_arrays: list[RaidEnemyTableArray],
        story_progress: StoryProgress,
        game: Game
    ) -> tuple[list[RaidEnemyTable], int]:
        """Build possible encounter table array"""
        raid_enemy_table_array = raid_enemy_table_arrays[self.difficulty]

        possible_encounter_tables = []
        encounter_slot_total = 0

        for table in raid_enemy_table_array.raid_enemy_tables:
            if self.valid_table(story_progress, game, table):
                possible_encounter_tables.append(table)
                encounter_slot_total += table.raid_enemy_info.rate

        return possible_encounter_tables, encounter_slot_total

    def valid_table_event(
        self,
        story_progress: StoryProgress,
        game: Game,
        table: RaidEnemyTable
    ) -> bool:
        """Check if a RaidEnemyTable is possible to be selected for events"""
        return (
            table.raid_enemy_info.delivery_group_id == self.delivery_group_id and
            (
                table.raid_enemy_info.difficulty is None
                or table.raid_enemy_info.difficulty.is_unlocked(story_progress)
            ) and
            table.raid_enemy_info.rom_ver in (None, game, Game.BOTH)
        )

    def valid_table(
        self,
        story_progress: StoryProgress,
        game: Game,
        table: RaidEnemyTable
    ) -> bool:
        """Check if a RaidEnemyTable is possible to be selected"""
        if self.is_event:
            return self.valid_table_event(story_progress, game, table)
        return table.raid_enemy_info.rom_ver in (None, game, Game.BOTH)

    def __str__(self) -> str:
        if not self.is_enabled:
            return "Empty Den"

        form_str = f"-{self.form}" if self.form else ""
        shiny_str = "Shiny " if self.is_shiny else ""
        event_str = "Event " if self.is_event else ""
        star_str = "★" * (self.difficulty + 1)
        display = f"{self.species}{form_str}\n" \
                    f"{shiny_str}{event_str}{star_str}\n" \
                    f"IVs: {'/'.join(map(str, self.ivs))}\n" \
                    f"Nature: {self.nature}\n" \
                    f"Ability: {self.ability}\n" \
                    f"Gender: {self.gender}\n" \
                    f"Tera Type: {self.tera_type}\n" \
                    f"Location: {self.id_str}\n"
        if not self.hide_sensitive_info:
            display += f"Seed: {self.seed:08X} EC: {self.encryption_constant:08X}\n" \
                        f"PID: {self.pid:08X} SIDTID: {self.sidtid:08X}\n"
        return display

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
        my_status: MyStatus9,
        delivery_raid_priority: tuple[int]
    ) -> None:
        """Initialize each raid with derived information"""
        for i, raid in enumerate(self.raids):
            # check the event delivery group
            den_delivery_group_id = None
            for delivery_group_id, delivery_group_size in enumerate(delivery_raid_priority):
                if i < delivery_group_size:
                    if not self.validate_event_slots(
                        raid_enemy_table_arrays,
                        story_progress,
                        game,
                        delivery_group_id
                    ):
                        continue
                    den_delivery_group_id = delivery_group_id
                    break
                i -= delivery_group_size
            raid.initialize_data(
                raid_enemy_table_arrays,
                story_progress,
                game,
                my_status,
                den_delivery_group_id
            )

    def validate_event_slots(
        self,
        raid_enemy_table_arrays: tuple[RaidEnemyTableArray],
        story_progress: StoryProgress,
        game: Game,
        delivery_group_id: int
    ):
        """Check if a delivery group id has spawnable pokemon"""
        dummy_raid = TeraRaid(
            is_enabled = 1,
            area_id = 0,
            display_type = 0,
            den_id = 0,
            seed = 0,
            _unused_14 = 0,
            content = 0,
            collected_league_points = 0,
        )
        dummy_raid.delivery_group_id = delivery_group_id
        dummy_raid.is_event = True
        dummy_raid.difficulty = StarLevel.EVENT
        total = dummy_raid.build_encounter_table(raid_enemy_table_arrays, story_progress, game)[1]
        return total != 0

def process_raid_block(raid_block: bytes) -> RaidBlock:
    """Process raid block with bytechomp"""
    reader = Reader[RaidBlock](ByteOrder.LITTLE).allocate()
    reader.feed(raid_block)
    assert reader.is_complete(), "Invalid data size"
    return reader.build()
