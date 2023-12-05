from enum import Enum, auto
from .base import MemoryAddress, MemoryAddressType

class BattleAddress(Enum):
    ENEMY_MOVE_ID = auto()
    ENEMY_MOVE_EFFECT = auto()
    ENEMY_MOVE_POWER = auto()
    ENEMY_MOVE_TYPE = auto()
    ENEMY_MOVE_ACCURACY = auto()
    ENEMY_MOVE_MAX_PP = auto()
    PLAYER_MOVE_ID = auto()
    PLAYER_MOVE_EFFECT = auto()
    PLAYER_MOVE_POWER = auto()
    PLAYER_MOVE_TYPE = auto()
    PLAYER_MOVE_ACCURACY = auto()
    PLAYER_MOVE_MAX_PP = auto()
    ENEMY_POKEMON_ID = auto()
    PLAYER_POKEMON_ID = auto()
    ENEMY_NAME = auto()
    # This seems to be a repat?
    # ENEMY_POKEMON_ID = 16
    ENEMY_HP = auto()
    ENEMY_LEVEL = auto()
    ENEMY_STATUS = auto()
    ENEMY_TYPE_1 = auto()
    ENEMY_TYPE_2 = auto()
    # ENEMY_CATCH_RATE_UNUSED only checked by move Transform
    ENEMY_CATCH_RATE_UNUSED = auto()
    ENEMY_MOVE_1 = auto()
    ENEMY_MOVE_2 = auto()
    ENEMY_MOVE_3 = auto()
    ENEMY_MOVE_4 = auto()
    ENEMY_ATT_DEF_DVS = auto()
    ENEMY_SPEED_SPEC_DVS = auto()
    # Another repeat? 
    # ENEMY_LEVEL = (0xCFEC)
    ENEMY_MAX_HP = auto()
    ENEMY_ATTACK = auto()
    ENEMY_DEFENSE = auto()
    ENEMY_SPEED = auto()
    ENEMY_SPECIAL = auto()
    ENEMY_MOVE_PP_1 = auto()
    ENEMY_MOVE_PP_2 = auto()
    ENEMY_MOVE_PP_3 = auto()
    EMENY_MOVE_PP_4 = auto()
    ENEMY_BASE_STATS = auto()
    ENEMY_CATCH_RATE = auto()
    ENEMY_BASE_EXP = auto()
    TYPE_OF_BATTLE = auto()

BATTLE_ADDRESS_LOOKUP = {
    BattleAddress.ENEMY_MOVE_ID: MemoryAddress(0xCFCC, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_MOVE_EFFECT: MemoryAddress(0xCFCD, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_MOVE_POWER: MemoryAddress(0xCFCE, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_MOVE_TYPE: MemoryAddress(0xCFCF, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_MOVE_ACCURACY: MemoryAddress(0xCFD0, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_MOVE_MAX_PP: MemoryAddress(0xCFD1, 1, MemoryAddressType.HEX),
    BattleAddress.PLAYER_MOVE_ID: MemoryAddress(0xCFD2, 1, MemoryAddressType.HEX),
    BattleAddress.PLAYER_MOVE_EFFECT: MemoryAddress(0xCFD3, 1, MemoryAddressType.HEX),
    BattleAddress.PLAYER_MOVE_POWER: MemoryAddress(0xCFD4, 1, MemoryAddressType.HEX),
    BattleAddress.PLAYER_MOVE_TYPE: MemoryAddress(0xCFD5, 1, MemoryAddressType.HEX),
    BattleAddress.PLAYER_MOVE_ACCURACY: MemoryAddress(0xCFD6, 1, MemoryAddressType.HEX),
    BattleAddress.PLAYER_MOVE_MAX_PP: MemoryAddress(0xCFD7, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_POKEMON_ID: MemoryAddress(0xCFD8, 1, MemoryAddressType.HEX),
    BattleAddress.PLAYER_POKEMON_ID: MemoryAddress(0xCFD9, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_NAME: MemoryAddress(0xCFDA, 10, MemoryAddressType.TEXT),
    # This seems to be a repat?
    # ENEMY_POKEMON_ID = (0xCFE5, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_HP: MemoryAddress(0xCFE6, 2, MemoryAddressType.HEX),
    BattleAddress.ENEMY_LEVEL: MemoryAddress(0xCFE8, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_STATUS: MemoryAddress(0xCFE9, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_TYPE_1: MemoryAddress(0xCFEA, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_TYPE_2: MemoryAddress(0xCFEB, 1, MemoryAddressType.HEX),
    # ENEMY_CATCH_RATE_UNUSED only checked by move Transform
    BattleAddress.ENEMY_CATCH_RATE_UNUSED: MemoryAddress(0xCFEC, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_MOVE_1: MemoryAddress(0xCFED, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_MOVE_2: MemoryAddress(0xCFEE, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_MOVE_3: MemoryAddress(0xCFEF, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_MOVE_4: MemoryAddress(0xCFF0, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_ATT_DEF_DVS: MemoryAddress(0xCFF1, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_SPEED_SPEC_DVS: MemoryAddress(0xCFF2, 1, MemoryAddressType.HEX),
    # Another repeat? 
    # ENEMY_LEVEL = MemoryAddress(0xCFEC, 1)
    BattleAddress.ENEMY_MAX_HP: MemoryAddress(0xCFF4, 2, MemoryAddressType.HEX),
    BattleAddress.ENEMY_ATTACK: MemoryAddress(0xCFF6, 2, MemoryAddressType.HEX),
    BattleAddress.ENEMY_DEFENSE: MemoryAddress(0xCFF8, 2, MemoryAddressType.HEX),
    BattleAddress.ENEMY_SPEED: MemoryAddress(0xCFFA, 2, MemoryAddressType.HEX),
    BattleAddress.ENEMY_SPECIAL: MemoryAddress(0xCFFC, 2, MemoryAddressType.HEX),
    BattleAddress.ENEMY_MOVE_PP_1: MemoryAddress(0xCFFF, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_MOVE_PP_2: MemoryAddress(0xCFFF, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_MOVE_PP_3: MemoryAddress(0xD000, 1, MemoryAddressType.HEX),
    BattleAddress.EMENY_MOVE_PP_4: MemoryAddress(0xD001, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_BASE_STATS: MemoryAddress(0xD002, 5, MemoryAddressType.HEX),
    BattleAddress.ENEMY_CATCH_RATE: MemoryAddress(0xD007, 1, MemoryAddressType.HEX),
    BattleAddress.ENEMY_BASE_EXP: MemoryAddress(0xD008, 1, MemoryAddressType.HEX),
    BattleAddress.TYPE_OF_BATTLE: MemoryAddress(0xD057, 1, MemoryAddressType.HEX),
}