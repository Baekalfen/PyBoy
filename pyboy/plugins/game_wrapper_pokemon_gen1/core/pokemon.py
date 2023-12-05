from ..data.memory_addrs.pokemon import PokemonBaseAddress, PokemonAddress, POKEMON_ADDRESS_LOOKUP
from ..data.constants.pokemon import PokemonId, _POKEMON_NAMES, _POKEMON_POKEDEX_INDEX
from .move import Move
from .memory_object import MemoryObject

class Pokemon(MemoryObject):

    _enum = PokemonAddress
    _lookup = POKEMON_ADDRESS_LOOKUP

    def __init__(self, fields_to_track):
        super().__init__(fields_to_track)

    @property
    def name(self):
        return Pokemon.get_pokemon_name_from_id(self.get_value(PokemonAddress.ID))
    
    @property
    def pokedex_num(self):
        return Pokemon.get_pokedex_id_from_pokemon_id(self.get_value(PokemonAddress.ID))
    
    # @property
    # def move_1(self):
    #     return self._moves[0]
    
    # @property
    # def move_2(self):
    #     return self._moves[1]
    
    # @property
    # def move_3(self):
    #     return self._moves[2]
    
    # @property
    # def move_4(self):
    #     return self._moves[3]
    
    # @property
    # def pp_move_1(self):
    #     return self._pp_moves[0]
    
    # @property
    # def pp_move_2(self):
    #     return self._pp_moves[1]
    
    # @property
    # def pp_move_3(self):
    #     return self._pp_moves[2]
    
    # @property
    # def pp_move_4(self):
    #     return self._pp_moves[3]
    
    # @property
    # def hp_ev(self):
    #     return self._evs[0]
    
    # @property
    # def attack_ev(self):
    #     return self._evs[1]
    
    # @property
    # def defense_ev(self):
    #     return self._evs[2]
    
    # @property
    # def speed_ev(self):
    #     return self._evs[3]
    
    # @property
    # def special_ev(self):
    #     return self._evs[4]
    
    # @property
    # def max_hp(self):
    #     return self._stats[0]
    
    # @property
    # def attack(self):
    #     return self._stats[1]
    
    # @property
    # def defense(self):
    #     return self._stats[2]
    
    # @property
    # def speed(self):
    #     return self._stats[3]
    
    # @property
    # def special(self):
    #     return self._stats[4]
    
    # @property
    # def curr_hp_percent(self):
    #     return self._current_hp / self.max_hp
    
    @staticmethod
    def get_pokemon_name_from_id(pokemon_id):
        return _POKEMON_NAMES.get(PokemonId(pokemon_id))

    @staticmethod
    def get_pokedex_id_from_pokemon_id(pokemon_id):
        return _POKEMON_POKEDEX_INDEX.get(PokemonId(pokemon_id))
    
    @staticmethod
    def load_pokemon_from_party(mem_manager, party_id):
        pokemon = PartyPokemon(party_id=party_id)
        pokemon.load_from_memory(mem_manager)
        return pokemon 
    
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
    
class PartyPokemon(Pokemon):

    def __init__(self, party_id, fields_to_track=None):
        super().__init__(fields_to_track)
        self._party_id = party_id

    def _load_field_from_memory(self, mem_manager, field_enum):
        memory_addr = self._lookup[field_enum]
        memory_addr = memory_addr.add_offset([e.value for e in PokemonBaseAddress][self._party_id-1])
        self.data[field_enum] = mem_manager.read_memory_address(self._lookup[field_enum])