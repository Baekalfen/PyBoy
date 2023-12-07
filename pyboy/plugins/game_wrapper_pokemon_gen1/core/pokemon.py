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

    @property
    def current_hp(self):
        return self.get_value(PokemonAddress.CURRENT_HP)
    
    @property
    def move_1(self):
        return self.get_value(PokemonAddress.MOVE_1)
    
    @property
    def move_2(self):
        return self.get_value(PokemonAddress.MOVE_2)
    
    @property
    def move_3(self):
        return self.get_value(PokemonAddress.MOVE_3)
    
    @property
    def move_4(self):
        return self.get_value(PokemonAddress.MOVE_4)
    
    @property
    def experience(self):
        return self.get_value(PokemonAddress.EXPERIENCE)
    
    @property
    def pp_move_1(self):
        return self.get_value(PokemonAddress.PP_MOVE_1)
    
    @property
    def pp_move_2(self):
        return self.get_value(PokemonAddress.PP_MOVE_2)
    
    @property
    def pp_move_3(self):
        return self.get_value(PokemonAddress.PP_MOVE_3)
    
    @property
    def pp_move_4(self):
        return self.get_value(PokemonAddress.PP_MOVE_4)
    
    @property
    def hp_ev(self):
        return self.get_value(PokemonAddress.HP_EV)
    
    @property
    def attack_ev(self):
        return self.get_value(PokemonAddress.ATTACK_EV)
    
    @property
    def defense_ev(self):
        return self.get_value(PokemonAddress.DEFENSE_EV)
    
    @property
    def speed_ev(self):
        return self.get_value(PokemonAddress.SPEED_EV)
    
    @property
    def special_ev(self):
        return self.get_value(PokemonAddress.SPECIAL_EV)
    
    @property
    def max_hp(self):
        return self.get_value(PokemonAddress.MAX_HP)
    
    @property
    def attack(self):
        return self.get_value(PokemonAddress.ATTACK)
    
    @property
    def defense(self):
        return self.get_value(PokemonAddress.DEFENSE)
    
    @property
    def speed(self):
        return self.get_value(PokemonAddress.SPEED)
    
    @property
    def special(self):
        return self.get_value(PokemonAddress.SPECIAL)
    
    @property
    def curr_hp_percent(self):
        return self.current_hp / self.max_hp
    
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
        s += f"\t{Move.get_name_from_id(self.move_1)} ({self.pp_move_1}/)\n"
        s += f"\t{Move.get_name_from_id(self.move_2)} ({self.pp_move_2}/)\n"
        s += f"\t{Move.get_name_from_id(self.move_3)} ({self.pp_move_3}/)\n"
        s += f"\t{Move.get_name_from_id(self.move_4)} ({self.pp_move_4}/)\n"
        
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
        self._data[field_enum] = mem_manager.read_memory_address(memory_addr)