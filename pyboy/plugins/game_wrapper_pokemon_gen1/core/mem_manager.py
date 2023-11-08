STRING_TERMINATOR = 80
ASCII_DELTA = 63

MAX_STRING_LENGTH = 16

class MemoryManager():

    def __init__(self, pyboy):
        self.pyboy = pyboy

    @staticmethod
    def _byte_to_bitfield(n, reverse : bool):
        # Force bit extension to 10 chars; 2 for '0x' and 8 for the bits
        bitlist = [1 if digit=='1' else 0 for digit in format(n, '#010b')[2:]]

        if reverse:
            bitlist.reverse()

        return bitlist
    
    @staticmethod
    def get_character_index(character):
        if character == ' ':
            return 0x7F
        if character == '?':
            return 0xE6
        if character == '!':
            return 0xE7
        if character == 'é':
            return 0xBA

        index = ord(character)
        if index > 47 and index < 58:
            # number
            return index + 197
        return index + ASCII_DELTA

    def _read_byte(self, addr):
        return self.pyboy.get_memory_value(addr)
    
    def read_address_from_memory(self, addr, num_bytes=1):
        p_addr = 0
        for i in range(num_bytes):
            p_addr += self.pyboy.get_memory_value(addr+i) << i*8
        return p_addr
    
    def read_hex_from_memory(self, addr, num_bytes=1):
        bytes = []
        for i in range(num_bytes):
            bytes.append(self.pyboy.get_memory_value(addr + i))
        # Do not believe there is ever a case where we would 
        # need to read this in little endian for Pokemon gen 1
        return int.from_bytes(bytes, byteorder='big')

    def read_bcd_from_memory(self, addr, num_bytes=1):
        byte_str = ""
        for i in range(num_bytes):
            byte_str += "%x"%self.pyboy.get_memory_value(addr+i)
        return int(byte_str)
    
    def read_bitfield_from_memory(self, addr, num_bytes=1, reverse=False):
        bits = []
        for i in range(num_bytes):
            bits.extend(MemoryManager._byte_to_bitfield(self._read_byte(addr+i), reverse))
        return bits

    def read_text_from_memory(self, address, num_bytes):
        """
        Retrieves a string from a given address.

        Args:
            address (int): Address from where to retrieve text from.
            cap (int): Maximum expected length of string (default: 16).
        """
        # Make sure string to write not too large
        assert num_bytes <= MAX_STRING_LENGTH
        text = ''
        for i in range(num_bytes):
            value = self._read_byte(address + i)
            if value == STRING_TERMINATOR:
                break
            text += chr(value - ASCII_DELTA)
        return text
    
    # def set_text(self, text, address):
    #     """Sets text at address.

    #     Will always add a string terminator (80) at the end.
    #     """
    #     i = 0
    #     for character in text:
    #         try:
    #             self.pyboy.set_memory_value(address + i, MemoryManager.get_character_index(character))
    #             i += 1
    #         except:
    #             pass
    #     self.pyboy.set_memory_value(address + i, STRING_TERMINATOR)

    # def set_rom_text(self, text, bank, address):
    #     i = 0
    #     for character in text:
    #         try:
    #             self.pyboy.override_memory_value(bank, address + i, get_character_index(character))
    #             i += 1
    #         except:
    #             pass