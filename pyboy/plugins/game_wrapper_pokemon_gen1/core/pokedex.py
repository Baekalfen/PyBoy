from pyboy.plugins.game_wrapper_pokemon_gen1.core.pokemon import Pokemon

# TODO: Technically with the project structure these should be in data/memory_addrs,
# but these are literally the only memory addresses we need so they lives here for now.
# Also probably move if we eventually have a flag to check Japanese vs international ROM

POKEDEX_CAUGHT_ADDR_INT = (0xD2F7, 19)
POKEDEX_SEEN_ADDR_INT = (0xD30A, 19)


class Pokedex:

    def __init__(self,
                 caught_pokemon,
                 seen_pokemon):
         
         self._caught_pokemon = caught_pokemon
         self._seen_pokemon = seen_pokemon

    @staticmethod
    def get_pokedex_range_bits(mem_manager, addr, num_bytes):
        return mem_manager.read_bitfield_from_memory(addr, num_bytes, reverse=True)


    @staticmethod
    def load_pokedex(mem_manager):
        caught_pokemon = Pokedex.get_pokedex_range_bits(mem_manager, POKEDEX_CAUGHT_ADDR_INT[0], num_bytes=POKEDEX_CAUGHT_ADDR_INT[1])
        seen_pokemon = Pokedex.get_pokedex_range_bits(mem_manager, POKEDEX_SEEN_ADDR_INT[0], num_bytes=POKEDEX_SEEN_ADDR_INT[1])

        return Pokedex(caught_pokemon, seen_pokemon)
    

    def get_number_pokemon_caught(self):
        return sum(self._caught_pokemon)
    
    def get_number_pokemon_seen(self):
        return sum(self._seen_pokemon)
    
    def have_caught_pokemon(self, pokemon_id):
        return self._caught_pokemon[Pokemon.get_pokedex_id_from_pokemon_id(pokemon_id)-1] == 1
    
    def have_seen_pokemon(self, pokemon_id):
        return self._seen_pokemon[Pokemon.get_pokedex_id_from_pokemon_id(pokemon_id)-1] == 1