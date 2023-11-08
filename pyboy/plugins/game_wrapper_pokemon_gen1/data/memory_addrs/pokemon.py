# Pokemon locations in memory
from enum import Enum

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
    ID = (0x0, 1) 
    CURRENT_HP = (0x1, 2)
    BOX_LEVEL = (0x3, 1)
    STATUS = (0x4, 1)
    TYPE_1 = (0x5, 1)
    TYPE_2 = (0x6, 1)
    CATCH_RATE = (0x7, 1)
    MOVE_1 = (0x8, 1)
    MOVE_2 = (0x9, 1)
    MOVE_3 = (0xA, 1)
    MOVE_4 = (0xB, 1)
    TRAINER_ID = (0xC, 2)
    EXPERIENCE = (0xE, 3)
    HP_EV = (0x11, 2)
    ATTACK_EV = (0x13, 2)
    DEFENSE_EV = (0x15, 2)
    SPEED_EV = (0x17, 2)
    SPECIAL_EV = (0x19, 2)
    ATTACK_DEFENSE_IV = (0x1B, 1)
    SPEED_SPECIAL_IV = (0x1C, 1)
    PP_MOVE_1 = (0x1D, 1)
    PP_MOVE_2 = (0x1E, 1)
    PP_MOVE_3 = (0x1F, 1)
    PP_MOVE_4 = (0x20, 1)
    LEVEL = (0x21, 1)
    MAX_HP = (0x22, 2)
    ATTACK = (0x24, 2)
    DEFENSE = (0x26, 2)
    SPEED = (0x28, 2)
    SPECIAL = (0x2A, 2)