from enum import Enum
from .base import MemoryAddress, MemoryAddressType

class GameStateAddress(Enum):
    BATTLE_TYPE = (0xD057, 1, MemoryAddressType.HEX)