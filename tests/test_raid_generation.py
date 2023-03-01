"""Test TeraRaid generation"""
# pylint: disable=import-error
from .context import (
    TeraRaid,
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
    Nature,
)


class MockMyStatus9:
    """Mock version of MyStatus9"""

    def __init__(self, tid: int, sid: int):
        self.tid = tid
        self.sid = sid
        self.full_id = (sid << 16) | tid


class MockParamSet:
    """Mock version of ParamSet"""

    def __init__(
        self, hp: int, atk: int, def_: int, spa: int, spd: int, spe: int
    ) -> None:
        self.hp = hp
        self.atk = atk
        self.def_ = def_
        self.spa = spa
        self.spd = spd
        self.spe = spe


class MockPokeDataBattle:
    """Mock version of PokeDataBattle"""

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
    """Mock version of RaidEnemyInfo"""

    def __init__(
        self,
        boss_poke_para: MockPokeDataBattle,
        difficulty: StarLevel = None,
    ) -> None:
        self.difficulty = difficulty
        self.boss_poke_para = boss_poke_para


def test_basic_generation():
    """Basic test of tera raid generation"""
    seed = 0x11223344
    mock_boss_poke_para = MockPokeDataBattle(dev_id=Species.PIKACHU, form_id=0)
    mock_info = MockRaidEnemyInfo(boss_poke_para=mock_boss_poke_para)
    dummy_raid = TeraRaid(
        is_enabled=1,
        area_id=0,
        display_type=0,
        den_id=0,
        seed=seed,
        _unused_14=0,
        content=0,
        collected_league_points=0,
    )
    dummy_raid.my_status = MockMyStatus9(tid=0, sid=0)
    dummy_raid.generate_pokemon(mock_info)

    assert dummy_raid.tera_type == TeraType.ROCK
    assert dummy_raid.encryption_constant == 0x33BF9D9F
    assert dummy_raid.pid == 0x982D1248
    assert dummy_raid.sidtid == 0x82F687C5
    assert not dummy_raid.is_shiny
    assert dummy_raid.ivs == (1, 0, 20, 14, 3, 11)
    assert dummy_raid.ability == Ability.STATIC
    assert dummy_raid.ability_index == AbilityIndex.ABILITY_2
    assert dummy_raid.gender == Gender.FEMALE
    assert dummy_raid.nature == Nature.LONELY
    assert dummy_raid.height == 124
    assert dummy_raid.weight == 205
    assert dummy_raid.scale == 94


def test_guaranteed_iv_generation():
    """Test tera raid generation with guaranteed ivs"""
    seed = 0x88776655
    mock_boss_poke_para = MockPokeDataBattle(
        dev_id=Species.MAUSHOLD,
        form_id=0,
        talent_vnum=3,
    )
    mock_info = MockRaidEnemyInfo(boss_poke_para=mock_boss_poke_para)
    dummy_raid = TeraRaid(
        is_enabled=1,
        area_id=0,
        display_type=0,
        den_id=0,
        seed=seed,
        _unused_14=0,
        content=0,
        collected_league_points=0,
    )
    dummy_raid.my_status = MockMyStatus9(tid=0, sid=0)
    dummy_raid.generate_pokemon(mock_info)

    assert dummy_raid.tera_type == TeraType.DARK
    assert dummy_raid.encryption_constant == 0xAB14D0B0
    assert dummy_raid.pid == 0x4F18230B
    assert dummy_raid.sidtid == 0x483A3AC3
    assert not dummy_raid.is_shiny
    assert dummy_raid.ivs == (26, 31, 31, 7, 15, 31)
    assert dummy_raid.ability == Ability.CHEEK_POUCH
    assert dummy_raid.ability_index == AbilityIndex.ABILITY_2
    assert dummy_raid.gender == Gender.GENDERLESS
    assert dummy_raid.nature == Nature.RELAXED
    assert dummy_raid.height == 47
    assert dummy_raid.weight == 113
    assert dummy_raid.scale == 57


def test_toxtricity_0_generation():
    """Test tera raid generation of Toxtricity-0"""
    seed = 0xDEADBEEF
    mock_boss_poke_para = MockPokeDataBattle(
        dev_id=Species.TOXTRICITY,
        form_id=0,
        talent_vnum=3,
    )
    mock_info = MockRaidEnemyInfo(boss_poke_para=mock_boss_poke_para)
    dummy_raid = TeraRaid(
        is_enabled=1,
        area_id=0,
        display_type=0,
        den_id=0,
        seed=seed,
        _unused_14=0,
        content=0,
        collected_league_points=0,
    )
    dummy_raid.my_status = MockMyStatus9(tid=0, sid=0)
    dummy_raid.generate_pokemon(mock_info)

    assert dummy_raid.tera_type == TeraType.WATER
    assert dummy_raid.encryption_constant == 0x14B294A
    assert dummy_raid.pid == 0x8059C15D
    assert dummy_raid.sidtid == 0x1BDB0373
    assert not dummy_raid.is_shiny
    assert dummy_raid.ivs == (31, 7, 31, 31, 28, 22)
    assert dummy_raid.ability == Ability.PLUS
    assert dummy_raid.ability_index == AbilityIndex.ABILITY_2
    assert dummy_raid.gender == Gender.FEMALE
    assert dummy_raid.nature == Nature.BRAVE
    assert dummy_raid.height == 140
    assert dummy_raid.weight == 128
    assert dummy_raid.scale == 155


def test_toxtricity_1_generation():
    """Test tera raid generation of Toxtricity-1"""
    seed = 0xDEADBEEF
    mock_boss_poke_para = MockPokeDataBattle(
        dev_id=Species.TOXTRICITY,
        form_id=1,
        talent_vnum=3,
    )
    mock_info = MockRaidEnemyInfo(boss_poke_para=mock_boss_poke_para)
    dummy_raid = TeraRaid(
        is_enabled=1,
        area_id=0,
        display_type=0,
        den_id=0,
        seed=seed,
        _unused_14=0,
        content=0,
        collected_league_points=0,
    )
    dummy_raid.my_status = MockMyStatus9(tid=0, sid=0)
    dummy_raid.generate_pokemon(mock_info)

    assert dummy_raid.tera_type == TeraType.WATER
    assert dummy_raid.encryption_constant == 0x14B294A
    assert dummy_raid.pid == 0x8059C15D
    assert dummy_raid.sidtid == 0x1BDB0373
    assert not dummy_raid.is_shiny
    assert dummy_raid.ivs == (31, 7, 31, 31, 28, 22)
    assert dummy_raid.ability == Ability.MINUS
    assert dummy_raid.ability_index == AbilityIndex.ABILITY_2
    assert dummy_raid.gender == Gender.FEMALE
    assert dummy_raid.nature == Nature.RELAXED
    assert dummy_raid.height == 140
    assert dummy_raid.weight == 128
    assert dummy_raid.scale == 155


def test_forced_generation():
    """Test tera raid generation with forced info"""
    seed = 0x66774455
    mock_boss_poke_para = MockPokeDataBattle(
        dev_id=Species.CHARIZARD,
        form_id=0,
        talent_type=IVGeneration.SET_IVS,
        talent_value=MockParamSet(31, 31, 31, 31, 31, 31),
        sex=GenderGeneration.MALE,
        seikaku=NatureGeneration.MODEST,
        tokusei=AbilityGeneration.ABILITY_HA,
        rare_type=ShinyGeneration.SHINY_LOCKED,
        gem_type=TeraTypeGeneration.DRAGON,
    )
    mock_info = MockRaidEnemyInfo(boss_poke_para=mock_boss_poke_para)
    dummy_raid = TeraRaid(
        is_enabled=1,
        area_id=0,
        display_type=0,
        den_id=0,
        seed=seed,
        _unused_14=0,
        content=0,
        collected_league_points=0,
    )
    dummy_raid.my_status = MockMyStatus9(tid=17328, sid=4753)
    dummy_raid.generate_pokemon(mock_info)

    assert dummy_raid.tera_type == TeraType.DRAGON
    assert dummy_raid.encryption_constant == 0x8914AEB0
    assert dummy_raid.pid == 0x53B01291
    assert dummy_raid.sidtid == 0x943A5CB6
    assert not dummy_raid.is_shiny
    assert dummy_raid.ivs == (31, 31, 31, 31, 31, 31)
    assert dummy_raid.ability == Ability.SOLAR_POWER
    assert dummy_raid.ability_index == AbilityIndex.ABILITY_HA
    assert dummy_raid.gender == Gender.MALE
    assert dummy_raid.nature == Nature.MODEST
    assert dummy_raid.height == 145
    assert dummy_raid.weight == 157
    assert dummy_raid.scale == 63
