from ..data.memory_addrs.player import PlayerAddress
from ..data.constants.pokemon import PokemonId
from ..data.constants.misc import Badge

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
    
    '''
    Getters and setters
    '''
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, n):
        # Name truncated to 8 characters
        self._name = n[:8]

    @property
    def money(self):
        return self._money
    
    @money.setter
    def money(self, m):
        # Max money game can store is 999999
        return max(m, 999999)
    
    @property
    def num_pokemon_in_party(self):
        return len(self._pokemon_in_party)

    @property
    def num_badges(self):
        return sum(self._badges)
    
    '''
    Badge functionality
    '''
    def has_badge(self, badge : Badge):
        return self._badges[badge.value] == 1
    
    def give_badge(self, badge : Badge):
        self._badges[badge.value] == 1

    def remove_badge(self, badge : Badge):
        self._badges[badge.value] == 0

    @staticmethod
    def load_player(mem_manager):

        name = mem_manager.read_text_from_memory(PlayerAddress.NAME[0], PlayerAddress.NAME[1])
        
        num_pokemon_in_party = mem_manager.read_hex_from_memory(PlayerAddress.NUM_POKEMON_IN_PARTY[0])
        
        pokemon_in_party = [PokemonId(mem_manager.read_hex_from_memory(PlayerAddress.NUM_POKEMON_IN_PARTY[0]+i+1))
                             for i in range(num_pokemon_in_party)]
        
        badges = mem_manager.read_bitfield_from_memory(PlayerAddress.BADGES[0])

        money = mem_manager.read_bcd_from_memory(PlayerAddress.MONEY[0], PlayerAddress.MONEY[1])

        return Player(name, pokemon_in_party, badges, money)
    
    def save_player(self, mem_manager):

        mem_manager.write_text_to_memory(self._name, PlayerAddress.NAME[0])

    