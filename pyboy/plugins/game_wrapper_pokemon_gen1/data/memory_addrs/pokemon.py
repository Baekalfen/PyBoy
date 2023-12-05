# Pokemon locations in memory
from enum import Enum
from .base import MemoryAddress, MemoryAddressType

class PokemonBaseAddress(Enum):
    POKEMON_1 = 0xD16B
    POKEMON_2 = 0xD197
    POKEMON_3 = 0xD1C3
    POKEMON_4 = 0xD1EF
    POKEMON_5 = 0xD21B
    POKEMON_6 = 0xD247

# Offsets for Pokemon data access
# Structure is (offset, num bytes)
class PokemonMemoryOffset(Enum):
    ID = MemoryAddress(0x0, 1, MemoryAddressType.HEX)
    CURRENT_HP = MemoryAddress(0x1, 2, MemoryAddressType.HEX)
    BOX_LEVEL = MemoryAddress(0x3, 1, MemoryAddressType.HEX)
    STATUS = MemoryAddress(0x4, 1, MemoryAddressType.HEX)
    TYPE_1 = MemoryAddress(0x5, 1, MemoryAddressType.HEX)
    TYPE_2 = MemoryAddress(0x6, 1, MemoryAddressType.HEX)
    CATCH_RATE = MemoryAddress(0x7, 1, MemoryAddressType.HEX)
    MOVE_1 = MemoryAddress(0x8, 1, MemoryAddressType.HEX)
    MOVE_2 = MemoryAddress(0x9, 1, MemoryAddressType.HEX)
    MOVE_3 = MemoryAddress(0xA, 1, MemoryAddressType.HEX)
    MOVE_4 = MemoryAddress(0xB, 1, MemoryAddressType.HEX)
    TRAINER_ID = MemoryAddress(0xC, 2, MemoryAddressType.HEX)
    EXPERIENCE = MemoryAddress(0xE, 3, MemoryAddressType.HEX)
    HP_EV = MemoryAddress(0x11, 2, MemoryAddressType.HEX)
    ATTACK_EV = MemoryAddress(0x13, 2, MemoryAddressType.HEX)
    DEFENSE_EV = MemoryAddress(0x15, 2, MemoryAddressType.HEX)
    SPEED_EV = MemoryAddress(0x17, 2, MemoryAddressType.HEX)
    SPECIAL_EV = MemoryAddress(0x19, 2, MemoryAddressType.HEX)
    ATTACK_DEFENSE_IV = MemoryAddress(0x1B, 1, MemoryAddressType.HEX)
    SPEED_SPECIAL_IV = MemoryAddress(0x1C, 1, MemoryAddressType.HEX)
    PP_MOVE_1 = MemoryAddress(0x1D, 1, MemoryAddressType.HEX)
    PP_MOVE_2 = MemoryAddress(0x1E, 1, MemoryAddressType.HEX)
    PP_MOVE_3 = MemoryAddress(0x1F, 1, MemoryAddressType.HEX)
    PP_MOVE_4 = MemoryAddress(0x20, 1, MemoryAddressType.HEX)
    LEVEL = MemoryAddress(0x21, 1, MemoryAddressType.HEX)
    MAX_HP = MemoryAddress(0x22, 2, MemoryAddressType.HEX)
    ATTACK = MemoryAddress(0x24, 2, MemoryAddressType.HEX)
    DEFENSE = MemoryAddress(0x26, 2, MemoryAddressType.HEX)
    SPEED = MemoryAddress(0x28, 2, MemoryAddressType.HEX)
    SPECIAL = MemoryAddress(0x2A, 2, MemoryAddressType.HEX)