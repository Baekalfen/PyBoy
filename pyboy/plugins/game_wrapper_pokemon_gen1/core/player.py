from ..data.memory_addrs.player import PlayerAddresses
from ..data.constants.pokemon import PokemonIds

class Player:

    def __init__(self,
                 name, 
                 pokemon_in_party,
                 badges,
                 money):
        
        self._name = name
        self._pokemon_in_party = pokemon_in_party
        self._badges = badges
        self._money = money

    @staticmethod
    def load_player(mem_manager):

        name = mem_manager.read_text_from_memory(PlayerAddresses.NAME[0], PlayerAddresses.NAME[1])
        
        num_pokemon_in_party = mem_manager.read_hex_from_memory(PlayerAddresses.NUM_POKEMON_IN_PARTY[0])
        
        pokemon_in_party = [PokemonIds(mem_manager.read_hex_from_memory(PlayerAddresses.NUM_POKEMON_IN_PARTY[0]+i+1))
                             for i in range(num_pokemon_in_party)]
        
        badges = mem_manager.read_bitfield_from_memory(PlayerAddresses.BADGES[0])

        money = mem_manager.read_bcd_from_memory(PlayerAddresses.MONEY[0], PlayerAddresses.MONEY[1])

        return Player(name, pokemon_in_party, badges, money)
    
    @property
    def num_pokemon_in_party(self):
        return len(self._pokemon_in_party)

    @property
    def num_badges(self):
        return sum(self._badges)