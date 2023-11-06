from enum import Enum

# All info from https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map#ROM_banking

SRAM = (0xA000, 0xBFFF)
WRAM = (0xC000, 0xDFFF) # Unsure of where this range ACTUALLY ends
HRAM = (0xFF80, 0xFFFE)

# Pokemon locations in memory
class PokemonBaseAddrs(Enum):
    POKEMON_1 = 0xD16B
    POKEMON_2 = 0xD197
    POKEMON_3 = 0xD1C3
    POKEMON_4 = 0xD1EF
    POKEMON_5 = 0xD21B
    POKEMON_6 = 0xD247

# Offsets for Pokemon data access
# Structure is (offset, num bytes)
class PokemonOffsets(Enum):
    ID = (0x0, 1) 
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

class Pokemon:

    def __init__(self,
                 pokemon_id,
                 current_hp,
                 status,
                 type_1,
                 type_2,
                 catch_rate,
                 move_1,
                 move_2,
                 move_3,
                 move_4,
                 trainer_id,
                 experience,
                 hp_ev,
                 attack_ev,
                 defense_ev,
                 speed_ev,
                 special_ev,
                 attack_defense_iv,
                 speed_special_iv,
                 pp_move_1,
                 pp_move_2,
                 pp_move_3,
                 pp_move_4,
                 level,
                 max_hp,
                 attack,
                 defense,
                 speed,
                 special):
        self.pokemon_id = pokemon_id
        self.current_hp = current_hp
        self.status = status
        self.type_1 = type_1
        self.type_2 = type_2
        self.catch_rate = catch_rate
        self.move_1 = move_1
        self.move_2 = move_2
        self.move_3 = move_3
        self.move_4 = move_4
        self.trainer_id = trainer_id
        self.experience = experience
        self.hp_ev = hp_ev
        self.attack_ev = attack_ev
        self.defense_ev = defense_ev
        self.speed_ev = speed_ev
        self.special_ev = special_ev
        self.attack_defense_iv = attack_defense_iv
        self.speed_special_iv = speed_special_iv
        self.pp_move_1 = pp_move_1
        self.pp_move_2 = pp_move_2
        self.pp_move_3 = pp_move_3
        self.pp_move_4 = pp_move_4
        self.level = level
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.special = special

    def pretty_stringify(self):
        s = '''
                
            '''
        
class Gen1MemoryManager:

    def __init__(self, pyboy, byte_order='big'):
        self.pyboy = pyboy
        self.byte_order = byte_order

    def _load_pokemon_from_address(self, pokemon_base_address):

        pokemon_values = []

        for offset_enum in PokemonOffsets:
            offset, num_bytes = offset_enum.value[0], offset_enum.value[1]
            memory_value = self.pyboy.get_memory_value(pokemon_base_address+offset, num_bytes)
            pokemon_values.append(memory_value)

        return Pokemon(*pokemon_values)
    
    def load_pokemon_from_party(self, party_location):
        # party_location goes from 1 to 6
        pokemon_base_address = list(PokemonBaseAddrs)[party_location-1].value
        return self._load_pokemon_from_address(pokemon_base_address)