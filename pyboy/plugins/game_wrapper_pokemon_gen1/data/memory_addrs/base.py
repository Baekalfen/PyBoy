from enum import Enum

class MemoryAddressType(Enum):
    HEX = 0
    ADDRESS = 1
    BCD = 2
    BITFIELD = 3
    TEXT = 4

class MemoryAddress():

    def __init__(self, address, num_bytes, memory_type):
        self._address = address
        self._num_bytes = num_bytes
        self._memory_type = memory_type

    @property
    def address(self):
        return self._address
        
    @property
    def num_bytes(self):
        return self._num_bytes
    
    @property
    def memory_type(self):
        return self._memory_type

    def __str__(self):
        return f"Memory address: {self._address}: Length: {self._num_bytes}, memory_addr_type: {self._memory_type}"
    
    def add_offset(self, offset):
        return MemoryAddress(self.address+offset, self.num_bytes, self.memory_type)
    
class HexMemoryAddress(MemoryAddress):

    def __init__(self, address, num_bytes):
        super().__init__(address, num_bytes, MemoryAddressType.HEX)

class AddressMemoryAddress(MemoryAddress):

    def __init__(self, address, num_bytes):
        super().__init__(address, num_bytes, MemoryAddressType.ADDRESS)

class BCDMemoryAddress(MemoryAddress):

    def __init__(self, address, num_bytes):
        super().__init__(address, num_bytes, MemoryAddressType.BCD)

class BitfieldMemoryAddress(MemoryAddress):

    def __init__(self, address, num_bytes):
        super().__init__(address, num_bytes, MemoryAddressType.BITFIELD)

class TextMemoryAddress(MemoryAddress):

    def __init__(self, address, num_bytes):
        super().__init__(address, num_bytes, MemoryAddressType.TEXT)