from enum import Enum, auto
from .base import HexMemoryAddress, BCDMemoryAddress, TextMemoryAddress

class PlayerAddress(Enum):
    NAME = auto()
    NUM_POKEMON_IN_PARTY = auto()
    BADGES = auto()
    MONEY = auto()

PLAYER_ADDRESS_LOOKUP = {
    PlayerAddress.NAME: TextMemoryAddress(0xD158, 10),
    PlayerAddress.NUM_POKEMON_IN_PARTY: HexMemoryAddress(0xD163, 1),
    PlayerAddress.BADGES: HexMemoryAddress(0xD356, 1),
    PlayerAddress.MONEY: BCDMemoryAddress(0xD347, 3)

}