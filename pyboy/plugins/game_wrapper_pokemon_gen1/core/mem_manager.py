

class MemoryManager():

    def __init__(self, pyboy):
        self.pyboy = pyboy

    def read_byte(self, addr):
        return self.pyboy.get_memory_value(addr)
    
    def read_address_from_memory(self, addr, num_bytes):
        p_addr = 0
        for i in range(num_bytes):
            p_addr += self.pyboy.get_memory_value(addr+i) << i*8
        return p_addr
    
    def read_hex_from_memory(self, addr, num_bytes):
        bytes = []
        for i in range(num_bytes):
            bytes.append(self.pyboy.get_memory_value(addr + i))
        # Do not believe there is ever a case where we would 
        # need to read this in little endian for Pokemon gen 1
        return int.from_bytes(bytes, byteorder='big')

    def read_bcd_from_memory(self, addr, num_bytes):
        byte_str = ""
        for i in range(num_bytes):
            byte_str += "%x"%self.pyboy.get_memory_value(addr)
        return int(byte_str)