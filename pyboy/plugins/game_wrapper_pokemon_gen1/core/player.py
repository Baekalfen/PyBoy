from ..data.memory_addrs.player import PlayerAddress, PLAYER_ADDRESS_LOOKUP
from ..data.constants.pokemon import PokemonId
from ..data.constants.misc import Badge
from .memory_object import MemoryObject

class Player(MemoryObject):

    _enum = PlayerAddress
    _lookup = PLAYER_ADDRESS_LOOKUP

    def __init__(self, fields_to_track):
        super().__init__(fields_to_track)
    
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
        self._money = min(m, 999999)
    
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
        self._badges[badge.value] = 1

    def remove_badge(self, badge : Badge):
        self._badges[badge.value] = 0

    @staticmethod
    def load_player(mem_manager, fields_to_track=None):
        player = Player(mem_manager, fields_to_track)
        player.load_from_memory(mem_manager)
        return player
    
    # def save_player(self, mem_manager):

    #     mem_manager.write_memory_address(self._name, PlayerAddress.NAME)
    #     mem_manager.write_memory_address(self.num_pokemon_in_party, PlayerAddress.NUM_POKEMON_IN_PARTY)
    #     # TODO: Figure out the loading and unloading of Pokemon in party, as that should be in tandem with
    #     # Pokemon class so that data does not get out of sync
    #     mem_manager.write_memory_address(self._badges, PlayerAddress.BADGES)
    #     mem_manager.write_memory_address(self._money, PlayerAddress.MONEY)


    