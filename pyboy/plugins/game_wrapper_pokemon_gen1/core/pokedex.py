from pyboy.plugins.game_wrapper_pokemon_gen1.utils import bitfield
from pyboy.plugins.game_wrapper_pokemon_gen1.core.pokemon import Pokemon

# TODO: Technically with the project structure these should be in data/memory_addrs,
# but these are literally the only memory addresses we need so they lives here for now.
# Also probably move if we eventually have a flag to check Japanese vs international ROM

POKEDEX_CAUGHT_START_ADDR_INT = 0xD2F7
POKEDEX_CAUGHT_END_ADDR_INT = 0xD309
POKEDEX_SEEN_START_ADDR_INT = 0xD30A
POKEDEX_SEEN_END_ADDR_INT = 0xD31C


class Pokedex:

    def __init__(self,
                 caught_list,
                 seen_list):
         
         self._caught_list = caught_list
         self._seen_list = seen_list

    @staticmethod
    def get_pokedex_range_bits(pyboy, start_addr, end_addr):
         
        bit_list = []

        addr = start_addr

        while addr <= end_addr:
            pokedex_byte = pyboy.get_memory_value(addr)
            byte_bit_list = bitfield(pokedex_byte)
            bit_list.extend(byte_bit_list)
            addr += 1

        return bit_list
              

    @staticmethod
    def load_pokedex(pyboy):
        caught_pokemon = Pokedex.get_pokedex_range_bits(pyboy, POKEDEX_CAUGHT_START_ADDR_INT, POKEDEX_CAUGHT_END_ADDR_INT)
        seen_pokemon = Pokedex.get_pokedex_range_bits(pyboy, POKEDEX_SEEN_START_ADDR_INT, POKEDEX_SEEN_END_ADDR_INT)

        return Pokedex(caught_pokemon, seen_pokemon)
    

    def get_number_pokemon_caught(self):
        return sum(self._caught_list)
    
    def get_number_pokemon_seen(self):
        return sum(self._seen_list)
    
    def have_caught_pokemon(self, pokemon_id):
        return self._caught_list[Pokemon.get_pokedex_id_from_pokemon_id(pokemon_id).value] == 1
    
    def have_seen_pokemon(self, pokemon_id):
        return self._seen_list[Pokemon.get_pokedex_id_from_pokemon_id(pokemon_id).value] == 1