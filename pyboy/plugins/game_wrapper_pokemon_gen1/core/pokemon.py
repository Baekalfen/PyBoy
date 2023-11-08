from ..data.memory_addrs.pokemon import PokemonBaseAddrs, PokemonMemoryOffsets
from ..data.constants.pokemon import PokemonId, _POKEMON_NAMES, _POKEMON_POKEDEX_INDEX
from .move import Move

class Pokemon:

    def __init__(self,
                 pokemon_id,
                 current_hp,
                 box_level,
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
                 max_hp=0,
                 attack=0,
                 defense=0,
                 speed=0,
                 special=0,
                 in_party=False):
        self.pokemon_id = PokemonId(pokemon_id)
        self.current_hp = current_hp
        self.status = status
        self.type_1 = type_1
        self.type_2 = type_2
        self.catch_rate = catch_rate
        self.moves = [move_1, move_2, move_3, move_4]
        self.trainer_id = trainer_id
        self.experience = experience
        # EV order: HP, Attack, Defense, Speed, Special
        self.evs = [hp_ev, attack_ev, defense_ev, speed_ev, special_ev]
        self.attack_defense_iv = attack_defense_iv
        self.speed_special_iv = speed_special_iv
        self.pp_moves = [pp_move_1, pp_move_2, pp_move_3, pp_move_4]
        self.level = level if in_party else box_level
        # Stat order same as EV order
        self.stats = [max_hp, attack, defense, speed, special]
        self.in_party = in_party

    @property
    def name(self):
        return Pokemon.get_pokemon_name_from_id(self.pokemon_id)
    
    @property
    def pokedex_num(self):
        return Pokemon.get_pokedex_id_from_pokemon_id(self.pokemon_id)
    
    @property
    def move_1(self):
        return self.moves[0]
    
    @property
    def move_2(self):
        return self.moves[1]
    
    @property
    def move_3(self):
        return self.moves[2]
    
    @property
    def move_4(self):
        return self.moves[3]
    
    @property
    def pp_move_1(self):
        return self.pp_moves[0]
    
    @property
    def pp_move_2(self):
        return self.pp_moves[1]
    
    @property
    def pp_move_3(self):
        return self.pp_moves[2]
    
    @property
    def pp_move_4(self):
        return self.pp_moves[3]
    
    @property
    def hp_ev(self):
        return self.evs[0]
    
    @property
    def attack_ev(self):
        return self.evs[1]
    
    @property
    def defense_ev(self):
        return self.evs[2]
    
    @property
    def speed_ev(self):
        return self.evs[3]
    
    @property
    def special_ev(self):
        return self.evs[4]
    
    @property
    def max_hp(self):
        return self.stats[0]
    
    @property
    def attack(self):
        return self.stats[1]
    
    @property
    def defense(self):
        return self.stats[2]
    
    @property
    def speed(self):
        return self.stats[3]
    
    @property
    def special(self):
        return self.stats[4]
    
    @staticmethod
    def get_pokemon_name_from_id(pokemon_id):
        return _POKEMON_NAMES.get(PokemonId(pokemon_id))

    @staticmethod
    def get_pokedex_id_from_pokemon_id(pokemon_id):
        return _POKEMON_POKEDEX_INDEX.get(PokemonId(pokemon_id))

    
    @staticmethod
    def _load_pokemon_from_address(mem_manager, pokemon_base_address, in_party):

        pokemon_values = []

        if in_party:
            it = list(PokemonMemoryOffsets)
        else:
            # When checking a Pokemon in the box, it does not have the second 
            # level field or any of its stats saved in memory
            it = list(PokemonMemoryOffsets)[:-6]

        for offset_enum in PokemonMemoryOffsets:
            offset, num_bytes = offset_enum.value[0], offset_enum.value[1]
            memory_value = mem_manager.read_hex_from_memory(pokemon_base_address+offset, num_bytes)
            pokemon_values.append(memory_value)

        return Pokemon(*pokemon_values, in_party)
    
    @classmethod
    def load_pokemon_from_party(cls, mem_manager, party_location):
        # party_location goes from 1-6
        pokemon_base_address = list(PokemonBaseAddrs)[party_location-1].value
        return cls._load_pokemon_from_address(mem_manager, pokemon_base_address, in_party=True)
    
    def _generate_move_str(self):
        s = f"Moves:\n" 
        
        for i, move_id in enumerate(self.moves):
            s += f"\t{Move.get_name_from_id(move_id)} ({self.pp_moves[i]}/)\n"
        
        return s
    
    def _generate_stats_str(self):

        s = f"Stats:\n" + \
            f"\tHP: {self.max_hp}\n" + \
            f"\tAttack: {self.attack}\n" + \
            f"\tDefense: {self.defense}\n" + \
            f"\tSpeed: {self.speed}\n" + \
            f"\tSpecial: {self.special}\n" 
        return s

    def pretty_stringify(self):
        s = f"{self.name}\n" + self._generate_stats_str() + self._generate_move_str() 
        return s