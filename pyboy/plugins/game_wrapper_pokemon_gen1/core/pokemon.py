from ..data.memory_addrs.pokemon import PokemonBaseAddress, PokemonMemoryOffset
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
        self._pokemon_id = PokemonId(pokemon_id)
        self._current_hp = current_hp
        self._status = status
        self._type_1 = type_1
        self._type_2 = type_2
        self._catch_rate = catch_rate
        self._moves = [move_1, move_2, move_3, move_4]
        self._trainer_id = trainer_id
        self._experience = experience
        # EV order: HP, Attack, Defense, Speed, Special
        self._evs = [hp_ev, attack_ev, defense_ev, speed_ev, special_ev]
        self._attack_defense_iv = attack_defense_iv
        self._speed_special_iv = speed_special_iv
        self._pp_moves = [pp_move_1, pp_move_2, pp_move_3, pp_move_4]
        self._level = level if in_party else box_level
        # Stat order same as EV order
        self._stats = [max_hp, attack, defense, speed, special]
        self._in_party = in_party

    @property
    def name(self):
        return Pokemon.get_pokemon_name_from_id(self._pokemon_id)
    
    @property
    def pokedex_num(self):
        return Pokemon.get_pokedex_id_from_pokemon_id(self._pokemon_id)
    
    @property
    def move_1(self):
        return self._moves[0]
    
    @property
    def move_2(self):
        return self._moves[1]
    
    @property
    def move_3(self):
        return self._moves[2]
    
    @property
    def move_4(self):
        return self._moves[3]
    
    @property
    def pp_move_1(self):
        return self._pp_moves[0]
    
    @property
    def pp_move_2(self):
        return self._pp_moves[1]
    
    @property
    def pp_move_3(self):
        return self._pp_moves[2]
    
    @property
    def pp_move_4(self):
        return self._pp_moves[3]
    
    @property
    def hp_ev(self):
        return self._evs[0]
    
    @property
    def attack_ev(self):
        return self._evs[1]
    
    @property
    def defense_ev(self):
        return self._evs[2]
    
    @property
    def speed_ev(self):
        return self._evs[3]
    
    @property
    def special_ev(self):
        return self._evs[4]
    
    @property
    def max_hp(self):
        return self._stats[0]
    
    @property
    def attack(self):
        return self._stats[1]
    
    @property
    def defense(self):
        return self._stats[2]
    
    @property
    def speed(self):
        return self._stats[3]
    
    @property
    def special(self):
        return self._stats[4]
    
    @property
    def curr_hp_percent(self):
        return self._current_hp / self.max_hp
    
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
            it = list(PokemonMemoryOffset)
        else:
            # When checking a Pokemon in the box, it does not have the second 
            # level field or any of its stats saved in memory
            it = list(PokemonMemoryOffset)[:-6]

        for offset_enum in PokemonMemoryOffset.values():
            offset_addr = offset_enum.add_addr(pokemon_base_address)
            memory_value = mem_manager.read_memory_address(offset_addr)
            pokemon_values.append(memory_value)

        return Pokemon(*pokemon_values, in_party)
    
    @classmethod
    def load_pokemon_from_party(cls, mem_manager, party_location):
        # party_location goes from 1-6
        pokemon_base_address = list(PokemonBaseAddress)[party_location-1].value
        return cls._load_pokemon_from_address(mem_manager, pokemon_base_address, in_party=True)
    
    def _generate_move_str(self):
        s = f"Moves:\n" 
        
        for i, move_id in enumerate(self._moves):
            s += f"\t{Move.get_name_from_id(move_id)} ({self._pp_moves[i]}/)\n"
        
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