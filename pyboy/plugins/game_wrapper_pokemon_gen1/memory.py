from enum import Enum

# All info from https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map#ROM_banking

class PokemonMemAddrs(Enum):
    POKEMON_1 = 0xD16B
    POKEMON_2 = 0xD197
    POKEMON_3 = 0xD1C3
    POKEMON_4 = 0xD1EF
    POKEMON_5 = 0xD21B
    POKEMON_6 = 0xD247

class PokemonMemOffs(Enum):
    POKEMON = (0x0, 1)
    CURRENT_HP = (0x1, 2)
    STATUS = (0x3, 1)
    TYPE_1 = (0x4, 1)
    TYPE_2 = (0x5, 1)
    CATCH_RATE = (0x6, 1)
    MOVE_1 = (0x7, 1)
    MOVE_2 = (0x8, 1)
    MOVE_3 = (0x9, 1)
    MOVE_4 = (0xA, 1)
    TRAINER_ID = (0xB, 2)
    EXPERIENCE = (0xD, 3)

class PokemonMemoryWriter:

    def __init__(self, byte_order='big'):
        self.byte_order = byte_order

    