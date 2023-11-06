from .pokemon import Pokemon

# All info from https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map#ROM_banking

SRAM = (0xA000, 0xBFFF)
WRAM = (0xC000, 0xDFFF) # Unsure of where this range ACTUALLY ends
HRAM = (0xFF80, 0xFFFE)
        
class Gen1MemoryManager:

    def __init__(self, pyboy, byte_order='big'):
        self.pyboy = pyboy
        self.byte_order = byte_order

    def load_pokemon_from_party(self, party_location):
        return Pokemon.load_pokemon_from_party(self.pyboy, party_location)