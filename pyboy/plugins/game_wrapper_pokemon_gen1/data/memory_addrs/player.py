from enum import Enum
from .base import MemoryAddress, MemoryAddressType

class PlayerAddress(Enum):
    NAME = MemoryAddress(0xD158, 10, MemoryAddressType.TEXT)
    NUM_POKEMON_IN_PARTY = MemoryAddress(0xD163, 1, MemoryAddressType.HEX)
    BADGES = MemoryAddress(0xD356, 1, MemoryAddressType.HEX)
    MONEY = MemoryAddress(0xD347, 3, MemoryAddressType.BCD)