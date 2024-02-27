from .memory_object import MemoryObject
from ..data.memory_addrs.battle import BattleAddress, BATTLE_ADDRESS_LOOKUP

class Battle(MemoryObject):

    _enum = BattleAddress
    _lookup = BATTLE_ADDRESS_LOOKUP

    def __init__(self, fields_to_track=None):
        super().__init__(fields_to_track)