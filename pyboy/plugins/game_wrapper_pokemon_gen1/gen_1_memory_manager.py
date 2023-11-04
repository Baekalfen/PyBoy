from enum import Enum

# All info from https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map#ROM_banking

SRAM = (0xA000, 0xBFFF)
WRAM = (0xC000, 0xDFFF) # Unsure of where this range ACTUALLY ends
HRAM = (0xFF80, 0xFFFE)

# Pokemon locations in memory
POKEMON_1_BASE = 0xD16B
POKEMON_2_BASE = 0xD197
POKEMON_3_BASE = 0xD1C3
POKEMON_4_BASE = 0xD1EF
POKEMON_5_BASE = 0xD21B
POKEMON_6_BASE = 0xD247

# Offsets for Pokemon data access
# Structure is (offset, num bytes)
POKEMON_OFFSET = (0x0, 1) 
POKEMON_CURRENT_HP_OFFSET = (0x1, 2)
POKEMON_STATUS_OFFSET = (0x3, 1)
POKEMON_TYPE_1_OFFSET = (0x4, 1)
POKEMON_TYPE_2_OFFSET = (0x5, 1)
POKEMON_CATCH_RATE_OFFSET = (0x6, 1)
POKEMON_MOVE_1_OFFSET = (0x7, 1)
POKEMON_MOVE_2_OFFSET = (0x8, 1)
POKEMON_MOVE_3_OFFSET = (0x9, 1)
POKEMON_MOVE_4_OFFSET = (0xA, 1)
POKEMON_TRAINER_ID_OFFSET = (0xB, 2)
POKEMON_EXPERIENCE_OFFSET = (0xD, 3)

POKEMON_LEVEL_OFFSET = (0x21, 1)

class Gen1MemoryManager:

    def __init__(self, pyboy, byte_order='big'):
        self.pyboy = pyboy
        self.byte_order = byte_order

    def get_pokemon_1_info(self):
        return self.pyboy.get_memory_value(POKEMON_1_BASE + LEVEL[0])
