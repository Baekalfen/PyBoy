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
    def _bitfield_to_byte(bitlist, reverse : bool):

        if reverse: 
            bitlist.reverse()

        bit_str = ''.join(bitlist)

        return int(bit_str)
    
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
    
    def _write_byte(self, value, addr):
        return self.pyboy.set_memory_value(addr, value)

    def read_address_from_memory(self, addr, num_bytes=1):
        p_addr = 0
        for i in range(num_bytes):
            p_addr += self._read_byte(addr+i) << i*8
        return p_addr
    
    def read_hex_from_memory(self, addr, num_bytes=1):
        bytes = []
        for i in range(num_bytes):
            bytes.append(self._read_byte(addr + i))
        # Do not believe there is ever a case where we would 
        # need to read this in little endian for Pokemon gen 1
        return int.from_bytes(bytes, byteorder='big')
    
    def read_hex_from_mem_addr(self, mem_addr):
        return self.read_hex_from_memory(mem_addr[0], mem_addr[1])
    
    def write_hex_to_memory(self, value, addr, num_bytes=1):
        bytes = value.to_bytes(2, byteorder='big')
        assert len(bytes) == num_bytes
        for i, byte in enumerate(bytes):
            self._write_byte(addr + i, byte)

    def write_hex_to_mem_addr(self, value, mem_addr):
        self.write_hex_to_memory(value, mem_addr[0], mem_addr[1])

    def read_bcd_from_memory(self, addr, num_bytes=1):
        byte_str = ""
        for i in range(num_bytes):
            byte_str += "%x"%self._read_byte(addr+i)
        return int(byte_str)
    
    def read_bcd_from_mem_addr(self, mem_addr):
        return self.read_bcd_from_memory(mem_addr[0], mem_addr[1])
    
    def write_bcd_to_memory(self, value, addr, num_bytes=1):
        val_str = str(value)
        assert len(val_str) <= num_bytes*2

        padded_val = val_str.zfill(num_bytes*2)
        for i in range(num_bytes):
            sub_val = int(padded_val[i*2:(i*2)+2], 16)
            self._write_byte(sub_val, addr+i)

    def write_bcd_to_mem_addr(self, value, mem_addr):
        self.write_bcd_to_memory(value, mem_addr[0], mem_addr[1])
    
    def read_bitfield_from_memory(self, addr, num_bytes=1, reverse=False):
        bits = []
        for i in range(num_bytes):
            bits.extend(MemoryManager._byte_to_bitfield(self._read_byte(addr+i), reverse))
        return bits
    
    def read_bitfield_from_mem_addr(self, mem_addr, reverse=False):
        return self.read_bitfield_from_memory(mem_addr[0], mem_addr[1], reverse)
    
    def write_bitlist_to_memory(self, value, addr, num_bytes=1, reverse=False):

        # TODO: This check might be too restrictive
        assert len(value) % 8 == 0
        # TODO: Maybe don't need this check if we trust users to make value fit
        assert len(value)/8 == num_bytes
        
        for i in range(num_bytes):
            bit_list_start = i*8
            sub_bit_list = value[bit_list_start:bit_list_start+8]
            byte_val = MemoryManager._bitfield_to_byte(sub_bit_list, reverse)
            self._write_byte(byte_val, addr+i)

    def write_bitlist_to_mem_addr(self, value, mem_addr, reverse=False):
        self.write_bitlist_to_memory(value, mem_addr[0], mem_addr[1], reverse)

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
    
    def read_text_from_mem_addr(self, mem_addr):
        return self.read_text_from_memory(mem_addr[0], mem_addr[1])
    
    def write_text_to_memory_text(self, text, address, num_bytes=1):
        """Sets text at address.

        Will always add a string terminator (80) at the end.
        """

        terminated_text = text + STRING_TERMINATOR
        # TODO: Check that this isn't an odd-by-one issue
        assert terminated_text <= num_bytes

        i = 0
        for i, chr in enumerate(text):
            self.pyboy.set_memory_value(address + i, MemoryManager.get_character_index(chr))

    def write_text_to_mem_addr(self, text, mem_addr):
        self.write_text_to_memory(text, mem_addr[0], mem_addr[1])