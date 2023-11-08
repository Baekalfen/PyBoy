

class MemoryManager():

    def __init__(self, pyboy):
        self.pyboy = pyboy

    def read_byte(self, addr):
        return self.pyboy.get_memory_value(addr)
    
    def read_int_from_bytes(self, addr, num_bytes):
        byte_str = ""
        for i in range(num_bytes):
            byte_str += "%x"%self.pyboy.get_memory_value(addr)
        return int(byte_str)
