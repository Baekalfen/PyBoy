from base import MemoryAddressEnum

class PlayerAddress(MemoryAddressEnum):
    NAME = (0xD158, 10)
    NUM_POKEMON_IN_PARTY = (0xD163, 1)
    BADGES = (0xD356, 1)
    MONEY = (0xD347, 3)