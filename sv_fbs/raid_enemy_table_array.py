"""Array of RaidEnemyInfoTable"""

from .sv_enums import (
    StarLevel,
    Game,
    Move,
    Species,
    Gender,
    NatureGeneration,
    Item,
    TeraTypeGeneration,
    AbilityGeneration,
    Ball,
    IVGeneration,
    ShinyGeneration,
    SizeGeneration,
    MovesetType
)
from .flatbuffer_object import (
    U8,
    U16,
    U64,
    I8,
    I16,
    I32,
    FlatBufferObject,
)

class RaidEnemyTableArray(FlatBufferObject):
    """Array of RaidEnemyInfoTable (root object)"""
    def __init__(self, buf: bytearray):
        FlatBufferObject.__init__(self, buf)
        self.raid_enemy_tables: list[RaidEnemyTable] = self.read_init_object_array(RaidEnemyTable)

class RaidEnemyTable(FlatBufferObject):
    """Table containing only RaidEnemyInfo"""
    def __init__(self, buf: bytearray, offset: int):
        FlatBufferObject.__init__(self, buf, offset)
        self.raid_enemy_info: RaidEnemyInfo = self.read_init_object(RaidEnemyInfo)

class RaidEnemyInfo(FlatBufferObject):
    """Spawn info of raid pokemon"""
    def __init__(self, buf: bytearray, offset: int):
        FlatBufferObject.__init__(self, buf, offset)
        self.rom_ver: Game = self.read_init_int_enum(I16, Game)
        self.no: int = self.read_init_int(I32)
        self.delivery_group_id: int = self.read_init_int(I8)
        self.difficulty: StarLevel = self.read_init_int_enum(I32, StarLevel)
        self.rate: int = self.read_init_int(I8)
        self.drop_table_fix: int = self.read_init_int(U64)
        self.drop_table_random: int = self.read_init_int(U64)
        self.capture_rate: int = self.read_init_int(I8)
        self.capture_lv: int = self.read_init_int(I8)
        self.boss_poke_para: PokeDataBattle = self.read_init_object(PokeDataBattle)
        self.boss_poke_size: RaidBossSizeData = self.read_init_object(RaidBossSizeData)
        self.boss_desc: RaidBossData = self.read_init_object(RaidBossData)
        self.raid_time_data: RaidTimeData = self.read_init_object(RaidTimeData)

class PokeDataBattle(FlatBufferObject):
    """Data that describes attributes of the pokemon itself"""
    def __init__(self, buf: bytearray, offset: int):
        FlatBufferObject.__init__(self, buf, offset)
        self.dev_id: Species = self.read_init_int_enum(U16, Species)
        self.form_id: int = self.read_init_int(I16)
        self.sex: Gender = self.read_init_int_enum(I32, Gender)
        self.item: Item = self.read_init_int_enum(I32, Item)
        self.level: int = self.read_init_int(I32)
        self.ball_id: Ball = self.read_init_int_enum(I32, Ball)
        self.waza_type: MovesetType = self.read_init_int_enum(I32, MovesetType)
        self.waza_1: WazaSet = self.read_init_object(WazaSet)
        self.waza_2: WazaSet = self.read_init_object(WazaSet)
        self.waza_3: WazaSet = self.read_init_object(WazaSet)
        self.waza_4: WazaSet = self.read_init_object(WazaSet)
        self.gem_type: TeraTypeGeneration = self.read_init_int_enum(I32, TeraTypeGeneration)
        self.seikaku: NatureGeneration = self.read_init_int_enum(I32, NatureGeneration)
        self.tokusei: AbilityGeneration = self.read_init_int_enum(I32, AbilityGeneration)
        self.talent_type: IVGeneration = self.read_init_int_enum(I32, IVGeneration)
        self.talent_value: ParamSet = self.read_init_object(ParamSet)
        self.talent_vnum: int = self.read_init_int(I8)
        self.effort_value: ParamSet = self.read_init_object(ParamSet)
        self.rare_type: ShinyGeneration = self.read_init_int_enum(I32, ShinyGeneration)
        self.scale_type: SizeGeneration = self.read_init_int_enum(I32, SizeGeneration)
        self.scale_value: int = self.read_init_int(I16)

class WazaSet(FlatBufferObject):
    """Data that describes a learnt move"""
    def __init__(self, buf: bytearray, offset: int):
        FlatBufferObject.__init__(self, buf, offset)
        self.waza_id: Move = self.read_init_int_enum(U16, Move)
        self.point_up: int = self.read_init_int(I8)

class ParamSet(FlatBufferObject):
    """Data that describes pokemon stats (IVs or EVs)"""
    def __init__(self, buf: bytearray, offset: int):
        FlatBufferObject.__init__(self, buf, offset)
        self.hp: int = self.read_init_int(I32)
        self.atk: int = self.read_init_int(I32)
        self.def_: int = self.read_init_int(I32)
        self.spa: int = self.read_init_int(I32)
        self.spd: int = self.read_init_int(I32)
        self.spe: int = self.read_init_int(I32)

class RaidBossSizeData(FlatBufferObject):
    """Data that describes the size of raid bosses"""
    def __init__(self, buf: bytearray, offset: int):
        FlatBufferObject.__init__(self, buf, offset)
        self.height_type: SizeGeneration = self.read_init_int_enum(I32, SizeGeneration)
        self.heignt_value: int = self.read_init_int(I16)
        self.weight_type: SizeGeneration = self.read_init_int_enum(I32, SizeGeneration)
        self.waight_value: int = self.read_init_int(I16)
        self.scale_type: SizeGeneration = self.read_init_int_enum(I32, SizeGeneration)
        self.scale_value: int = self.read_init_int(I16)

class RaidBossData(FlatBufferObject):
    """Data that describes raid boss behavior"""
    def __init__(self, buf: bytearray, offset: int):
        FlatBufferObject.__init__(self, buf, offset)
        self.hp_coef: int = self.read_init_int(I16)
        self.power_charge_triger_hp: int = self.read_init_int(I8)
        self.power_charge_triger_time: int = self.read_init_int(I8)
        self.power_charge_limit_time: int = self.read_init_int(I16)
        self.power_charge_cancel_damage: int = self.read_init_int(I8)
        self.power_charge_penalty_time: int = self.read_init_int(I16)
        self.power_charge_penalty_action: int = self.read_init_int(U16)
        self.power_charge_damage_rate: int = self.read_init_int(I8)
        self.power_charge_gem_damage_rate: int = self.read_init_int(I8)
        self.power_charge_change_gem_damage_rate: int = self.read_init_int(I8)
        self.extra_action_1: RaidBossExtraData = self.read_init_object(RaidBossExtraData)
        self.extra_action_2: RaidBossExtraData = self.read_init_object(RaidBossExtraData)
        self.extra_action_3: RaidBossExtraData = self.read_init_object(RaidBossExtraData)
        self.extra_action_4: RaidBossExtraData = self.read_init_object(RaidBossExtraData)
        self.extra_action_5: RaidBossExtraData = self.read_init_object(RaidBossExtraData)
        self.extra_action_6: RaidBossExtraData = self.read_init_object(RaidBossExtraData)
        self.double_action_triger_hp: int = self.read_init_int(I8)
        self.double_action_triger_time: int = self.read_init_int(I8)
        self.double_action_rate: int = self.read_init_int(I8)

class RaidBossExtraData(FlatBufferObject):
    """Data describing special actions a raid boss can do during a raid"""
    def __init__(self, buf: bytearray, offset: int):
        FlatBufferObject.__init__(self, buf, offset)
        self.timming: int = self.read_init_int(I16)
        self.action: int = self.read_init_int(I16)
        self.value: int = self.read_init_int(I16)
        self.waza_no: Move = self.read_init_int_enum(U16, Move)

class RaidTimeData(FlatBufferObject):
    """Data that describes the timer during raid battle"""
    def __init__(self, buf: bytearray, offset: int):
        FlatBufferObject.__init__(self, buf, offset)
        self.is_active: bool = self.read_init_int(U8)
        self.game_limit: int = self.read_init_int(I32)
        self.client_limit: int = self.read_init_int(I32)
        self.command_limit: int = self.read_init_int(I32)
        self.poke_revive_time: int = self.read_init_int(I32)
        self.ai_interval_time: int = self.read_init_int(I32)
        self.ai_interval_rand: int = self.read_init_int(I32)
