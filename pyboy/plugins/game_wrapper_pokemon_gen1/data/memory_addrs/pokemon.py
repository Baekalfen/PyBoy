# Pokemon locations in memory
from enum import Enum, auto
from .base import HexMemoryAddress

class PokemonBaseAddress(Enum):
    POKEMON_1 = 0xD16B
    POKEMON_2 = 0xD197
    POKEMON_3 = 0xD1C3
    POKEMON_4 = 0xD1EF
    POKEMON_5 = 0xD21B
    POKEMON_6 = 0xD247

# Offsets for Pokemon data access
# Structure is (offset, num bytes)
class PokemonAddress(Enum):
    ID = auto()
    CURRENT_HP = auto()
    BOX_LEVEL = auto()
    STATUS = auto()
    TYPE_1 = auto()
    TYPE_2 = auto()
    CATCH_RATE = auto()
    MOVE_1 = auto()
    MOVE_2 = auto()
    MOVE_3 = auto()
    MOVE_4 = auto()
    TRAINER_ID = auto()
    EXPERIENCE = auto()
    HP_EV = auto()
    ATTACK_EV = auto()
    DEFENSE_EV = auto()
    SPEED_EV = auto()
    SPECIAL_EV = auto()
    ATTACK_DEFENSE_IV = auto()
    SPEED_SPECIAL_IV = auto()
    PP_MOVE_1 = auto()
    PP_MOVE_2 = auto()
    PP_MOVE_3 = auto()
    PP_MOVE_4 = auto()
    LEVEL = auto()
    MAX_HP = auto()
    ATTACK = auto()
    DEFENSE = auto()
    SPEED = auto()
    SPECIAL = auto()

POKEMON_ADDRESS_LOOKUP = {
    PokemonAddress.ID: HexMemoryAddress(0x0, 1),
    PokemonAddress.CURRENT_HP: HexMemoryAddress(0x1, 2),
    PokemonAddress.BOX_LEVEL: HexMemoryAddress(0x3, 1),
    PokemonAddress.STATUS: HexMemoryAddress(0x4, 1),
    PokemonAddress.TYPE_1: HexMemoryAddress(0x5, 1),
    PokemonAddress.TYPE_2: HexMemoryAddress(0x6, 1),
    PokemonAddress.CATCH_RATE: HexMemoryAddress(0x7, 1),
    PokemonAddress.MOVE_1: HexMemoryAddress(0x8, 1),
    PokemonAddress.MOVE_2: HexMemoryAddress(0x9, 1),
    PokemonAddress.MOVE_3: HexMemoryAddress(0xA, 1),
    PokemonAddress.MOVE_4: HexMemoryAddress(0xB, 1),
    PokemonAddress.TRAINER_ID: HexMemoryAddress(0xC, 2),
    PokemonAddress.EXPERIENCE: HexMemoryAddress(0xE, 3),
    PokemonAddress.HP_EV: HexMemoryAddress(0x11, 2),
    PokemonAddress.ATTACK_EV: HexMemoryAddress(0x13, 2),
    PokemonAddress.DEFENSE_EV: HexMemoryAddress(0x15, 2),
    PokemonAddress.SPEED_EV: HexMemoryAddress(0x17, 2),
    PokemonAddress.SPECIAL_EV: HexMemoryAddress(0x19, 2),
    PokemonAddress.ATTACK_DEFENSE_IV: HexMemoryAddress(0x1B, 1),
    PokemonAddress.SPEED_SPECIAL_IV: HexMemoryAddress(0x1C, 1),
    PokemonAddress.PP_MOVE_1: HexMemoryAddress(0x1D, 1),
    PokemonAddress.PP_MOVE_2: HexMemoryAddress(0x1E, 1),
    PokemonAddress.PP_MOVE_3: HexMemoryAddress(0x1F, 1),
    PokemonAddress.PP_MOVE_4: HexMemoryAddress(0x20, 1),
    PokemonAddress.LEVEL: HexMemoryAddress(0x21, 1),
    PokemonAddress.MAX_HP: HexMemoryAddress(0x22, 2),
    PokemonAddress.ATTACK: HexMemoryAddress(0x24, 2),
    PokemonAddress.DEFENSE: HexMemoryAddress(0x26, 2),
    PokemonAddress.SPEED: HexMemoryAddress(0x28, 2),
    PokemonAddress.SPECIAL: HexMemoryAddress(0x2A, 2),
}