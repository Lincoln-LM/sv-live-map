from sv_live_map_core.raid_block import TeraRaid
from sv_live_map_core.sv_enums import (
    StarLevel,
    Species,
    GenderGeneration,
    TeraTypeGeneration,
    NatureGeneration,
    AbilityGeneration,
    IVGeneration,
    ShinyGeneration,
    TeraType,
    Ability,
    AbilityIndex,
    Gender,
    Nature
)
from sv_live_map_core.personal_data_handler import PersonalDataHandler

class MockParamSet:
    def __init__(
        self,
        hp: int,
        atk: int,
        def_: int,
        spa: int,
        spd: int,
        spe: int
    ):
        self.hp = hp
        self.atk = atk
        self.def_ = def_
        self.spa = spa
        self.spd = spd
        self.spe = spe

class MockPokeDataBattle:
    def __init__(
        self,
        dev_id: Species,
        form_id: int,
        sex: GenderGeneration,
        gem_type: TeraTypeGeneration,
        seikaku: NatureGeneration,
        tokusei: AbilityGeneration,
        talent_type: IVGeneration,
        talent_value: MockParamSet,
        talent_vnum: int,
        rare_type: ShinyGeneration,
    ) -> None:
        self.dev_id = dev_id
        self.form_id = form_id
        self.sex = sex
        self.gem_type = gem_type
        self.seikaku = seikaku
        self.tokusei = tokusei
        self.talent_type = talent_type
        self.talent_value = talent_value
        self.talent_vnum = talent_vnum
        self.rare_type = rare_type

class MockRaidEnemyInfo:
    def __init__(
        self,
        dev_id: Species,
        form_id: int,
        sex: GenderGeneration = GenderGeneration.RANDOM_GENDER,
        gem_type: TeraTypeGeneration = TeraTypeGeneration.RANDOM,
        seikaku: NatureGeneration = NatureGeneration.NONE,
        tokusei: AbilityGeneration = AbilityGeneration.RANDOM_12,
        talent_type: IVGeneration = IVGeneration.SET_GUARANTEED_IVS,
        talent_value: MockParamSet = MockParamSet(0, 0, 0, 0, 0, 0),
        talent_vnum: int = 0,
        rare_type: ShinyGeneration = ShinyGeneration.RANDOM_SHININESS,
        difficulty: StarLevel = None,
    ) -> None:
        self.difficulty = difficulty
        self.boss_poke_para = MockPokeDataBattle(
            dev_id = dev_id,
            form_id = form_id,
            sex = sex,
            gem_type = gem_type,
            seikaku = seikaku,
            tokusei = tokusei,
            talent_type = talent_type,
            talent_value = talent_value,
            talent_vnum = talent_vnum,
            rare_type = rare_type
        )

def test_generation():
    PersonalDataHandler()
    seed = 0x11223344
    mock_info = MockRaidEnemyInfo(
        dev_id = Species.PIKACHU,
        form_id = 0
    )
    dummy_raid = TeraRaid(
        is_enabled = 1,
        area_id = 0,
        display_type = 0,
        den_id = 0,
        seed = seed,
        _unused_14 = 0,
        content = 0,
        collected_league_points = 0,
    )
    dummy_raid.generate_pokemon(mock_info)
    assert dummy_raid.tera_type == TeraType.ROCK
    assert dummy_raid.encryption_constant == 0x33bf9d9f
    assert dummy_raid.pid == 0x982d1248
    assert dummy_raid.sidtid == 0x82f687c5
    assert dummy_raid.is_shiny == False
    assert dummy_raid.ivs == (1, 0, 20, 14, 3, 11)
    assert dummy_raid.ability == Ability.STATIC
    assert dummy_raid.ability_index == AbilityIndex.ABILITY_2
    assert dummy_raid.gender == Gender.FEMALE
    assert dummy_raid.nature == Nature.LONELY
    assert dummy_raid.height == 124
    assert dummy_raid.weight == 205
    assert dummy_raid.scale == 94
