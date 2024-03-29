"""Enum for pokemon abilities"""
# pylint: disable=too-many-lines

from enum import IntEnum


class Ability(IntEnum):
    """Enum for pokemon abilities"""

    NONE = 0
    STENCH = 1
    DRIZZLE = 2
    SPEED_BOOST = 3
    BATTLE_ARMOR = 4
    STURDY = 5
    DAMP = 6
    LIMBER = 7
    SAND_VEIL = 8
    STATIC = 9
    VOLT_ABSORB = 10
    WATER_ABSORB = 11
    OBLIVIOUS = 12
    CLOUD_NINE = 13
    COMPOUND_EYES = 14
    INSOMNIA = 15
    COLOR_CHANGE = 16
    IMMUNITY = 17
    FLASH_FIRE = 18
    SHIELD_DUST = 19
    OWN_TEMPO = 20
    SUCTION_CUPS = 21
    INTIMIDATE = 22
    SHADOW_TAG = 23
    ROUGH_SKIN = 24
    WONDER_GUARD = 25
    LEVITATE = 26
    EFFECT_SPORE = 27
    SYNCHRONIZE = 28
    CLEAR_BODY = 29
    NATURAL_CURE = 30
    LIGHTNING_ROD = 31
    SERENE_GRACE = 32
    SWIFT_SWIM = 33
    CHLOROPHYLL = 34
    ILLUMINATE = 35
    TRACE = 36
    HUGE_POWER = 37
    POISON_POINT = 38
    INNER_FOCUS = 39
    MAGMA_ARMOR = 40
    WATER_VEIL = 41
    MAGNET_PULL = 42
    SOUNDPROOF = 43
    RAIN_DISH = 44
    SAND_STREAM = 45
    PRESSURE = 46
    THICK_FAT = 47
    EARLY_BIRD = 48
    FLAME_BODY = 49
    RUN_AWAY = 50
    KEEN_EYE = 51
    HYPER_CUTTER = 52
    PICKUP = 53
    TRUANT = 54
    HUSTLE = 55
    CUTE_CHARM = 56
    PLUS = 57
    MINUS = 58
    FORECAST = 59
    STICKY_HOLD = 60
    SHED_SKIN = 61
    GUTS = 62
    MARVEL_SCALE = 63
    LIQUID_OOZE = 64
    OVERGROW = 65
    BLAZE = 66
    TORRENT = 67
    SWARM = 68
    ROCK_HEAD = 69
    DROUGHT = 70
    ARENA_TRAP = 71
    VITAL_SPIRIT = 72
    WHITE_SMOKE = 73
    PURE_POWER = 74
    SHELL_ARMOR = 75
    AIR_LOCK = 76
    TANGLED_FEET = 77
    MOTOR_DRIVE = 78
    RIVALRY = 79
    STEADFAST = 80
    SNOW_CLOAK = 81
    GLUTTONY = 82
    ANGER_POINT = 83
    UNBURDEN = 84
    HEATPROOF = 85
    SIMPLE = 86
    DRY_SKIN = 87
    DOWNLOAD = 88
    IRON_FIST = 89
    POISON_HEAL = 90
    ADAPTABILITY = 91
    SKILL_LINK = 92
    HYDRATION = 93
    SOLAR_POWER = 94
    QUICK_FEET = 95
    NORMALIZE = 96
    SNIPER = 97
    MAGIC_GUARD = 98
    NO_GUARD = 99
    STALL = 100
    TECHNICIAN = 101
    LEAF_GUARD = 102
    KLUTZ = 103
    MOLD_BREAKER = 104
    SUPER_LUCK = 105
    AFTERMATH = 106
    ANTICIPATION = 107
    FOREWARN = 108
    UNAWARE = 109
    TINTED_LENS = 110
    FILTER = 111
    SLOW_START = 112
    SCRAPPY = 113
    STORM_DRAIN = 114
    ICE_BODY = 115
    SOLID_ROCK = 116
    SNOW_WARNING = 117
    HONEY_GATHER = 118
    FRISK = 119
    RECKLESS = 120
    MULTITYPE = 121
    FLOWER_GIFT = 122
    BAD_DREAMS = 123
    PICKPOCKET = 124
    SHEER_FORCE = 125
    CONTRARY = 126
    UNNERVE = 127
    DEFIANT = 128
    DEFEATIST = 129
    CURSED_BODY = 130
    HEALER = 131
    FRIEND_GUARD = 132
    WEAK_ARMOR = 133
    HEAVY_METAL = 134
    LIGHT_METAL = 135
    MULTISCALE = 136
    TOXIC_BOOST = 137
    FLARE_BOOST = 138
    HARVEST = 139
    TELEPATHY = 140
    MOODY = 141
    OVERCOAT = 142
    POISON_TOUCH = 143
    REGENERATOR = 144
    BIG_PECKS = 145
    SAND_RUSH = 146
    WONDER_SKIN = 147
    ANALYTIC = 148
    ILLUSION = 149
    IMPOSTER = 150
    INFILTRATOR = 151
    MUMMY = 152
    MOXIE = 153
    JUSTIFIED = 154
    RATTLED = 155
    MAGIC_BOUNCE = 156
    SAP_SIPPER = 157
    PRANKSTER = 158
    SAND_FORCE = 159
    IRON_BARBS = 160
    ZEN_MODE = 161
    VICTORY_STAR = 162
    TURBOBLAZE = 163
    TERAVOLT = 164
    AROMA_VEIL = 165
    FLOWER_VEIL = 166
    CHEEK_POUCH = 167
    PROTEAN = 168
    FUR_COAT = 169
    MAGICIAN = 170
    BULLETPROOF = 171
    COMPETITIVE = 172
    STRONG_JAW = 173
    REFRIGERATE = 174
    SWEET_VEIL = 175
    STANCE_CHANGE = 176
    GALE_WINGS = 177
    MEGA_LAUNCHER = 178
    GRASS_PELT = 179
    SYMBIOSIS = 180
    TOUGH_CLAWS = 181
    PIXILATE = 182
    GOOEY = 183
    AERILATE = 184
    PARENTAL_BOND = 185
    DARK_AURA = 186
    FAIRY_AURA = 187
    AURA_BREAK = 188
    PRIMORDIAL_SEA = 189
    DESOLATE_LAND = 190
    DELTA_STREAM = 191
    STAMINA = 192
    WIMP_OUT = 193
    EMERGENCY_EXIT = 194
    WATER_COMPACTION = 195
    MERCILESS = 196
    SHIELDS_DOWN = 197
    STAKEOUT = 198
    WATER_BUBBLE = 199
    STEELWORKER = 200
    BERSERK = 201
    SLUSH_RUSH = 202
    LONG_REACH = 203
    LIQUID_VOICE = 204
    TRIAGE = 205
    GALVANIZE = 206
    SURGE_SURFER = 207
    SCHOOLING = 208
    DISGUISE = 209
    BATTLE_BOND = 210
    POWER_CONSTRUCT = 211
    CORROSION = 212
    COMATOSE = 213
    QUEENLY_MAJESTY = 214
    INNARDS_OUT = 215
    DANCER = 216
    BATTERY = 217
    FLUFFY = 218
    DAZZLING = 219
    SOUL_HEART = 220
    TANGLING_HAIR = 221
    RECEIVER = 222
    POWEROF_ALCHEMY = 223
    BEAST_BOOST = 224
    R_K_S_SYSTEM = 225
    ELECTRIC_SURGE = 226
    PSYCHIC_SURGE = 227
    MISTY_SURGE = 228
    GRASSY_SURGE = 229
    FULL_METAL_BODY = 230
    SHADOW_SHIELD = 231
    PRISM_ARMOR = 232
    NEUROFORCE = 233
    INTREPID_SWORD = 234
    DAUNTLESS_SHIELD = 235
    LIBERO = 236
    BALL_FETCH = 237
    COTTON_DOWN = 238
    PROPELLER_TAIL = 239
    MIRROR_ARMOR = 240
    GULP_MISSILE = 241
    STALWART = 242
    STEAM_ENGINE = 243
    PUNK_ROCK = 244
    SAND_SPIT = 245
    ICE_SCALES = 246
    RIPEN = 247
    ICE_FACE = 248
    POWER_SPOT = 249
    MIMICRY = 250
    SCREEN_CLEANER = 251
    STEELY_SPIRIT = 252
    PERISH_BODY = 253
    WANDERING_SPIRIT = 254
    GORILLA_TACTICS = 255
    NEUTRALIZING_GAS = 256
    PASTEL_VEIL = 257
    HUNGER_SWITCH = 258
    QUICK_DRAW = 259
    UNSEEN_FIST = 260
    CURIOUS_MEDICINE = 261
    TRANSISTOR = 262
    DRAGONS_MAW = 263
    CHILLING_NEIGH = 264
    GRIM_NEIGH = 265
    AS_ONE_I = 266
    AS_ONE_G = 267
    LINGERING_AROMA = 268
    SEED_SOWER = 269
    THERMAL_EXCHANGE = 270
    ANGER_SHELL = 271
    PURIFYING_SALT = 272
    WELL_BAKED_BODY = 273
    WIND_RIDER = 274
    GUARD_DOG = 275
    ROCKY_PAYLOAD = 276
    WIND_POWER = 277
    ZEROTO_HERO = 278
    COMMANDER = 279
    ELECTROMORPHOSIS = 280
    PROTOSYNTHESIS = 281
    QUARK_DRIVE = 282
    GOODAS_GOLD = 283
    VESSELOF_RUIN = 284
    SWORDOF_RUIN = 285
    TABLETSOF_RUIN = 286
    BEADSOF_RUIN = 287
    ORICHALCUM_PULSE = 288
    HADRON_ENGINE = 289
    OPPORTUNIST = 290
    CUD_CHEW = 291
    SHARPNESS = 292
    SUPREME_OVERLORD = 293
    COSTAR = 294
    TOXIC_DEBRIS = 295
    ARMOR_TAIL = 296
    EARTH_EATER = 297
    MYCELIUM_MIGHT = 298

    def __str__(self) -> str:
        return self.name.replace("_", " ").title()


class AbilityIndex(IntEnum):
    """Enum for pokemon ability index"""

    ABILITY_1 = 0
    ABILITY_2 = 1
    ABILITY_HA = 2

    def __str__(self) -> str:
        return self.name.replace("_", " ").title().replace("Ha", "HA")


class AbilityGeneration(IntEnum):
    """Enum for pokemon ability generation"""

    RANDOM_12 = 0
    RANDOM_12HA = 1
    ABILITY_1 = 2
    ABILITY_2 = 3
    ABILITY_HA = 4

    def to_ability_index(self) -> AbilityIndex:
        """Convert to ability index"""
        return AbilityIndex(self.value - AbilityGeneration.ABILITY_1)

    def __str__(self) -> str:
        return self.name.replace("_", " ").title().replace("Ha", "HA")
