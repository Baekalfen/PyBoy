from enum import Enum

class MemoryAddressEnum(Enum):

    def __str__(self):
        return f"Memory address: {self.value[0]}: Length: {self.value[1]}"
    
    def add_addr(self, offset):
        # Super hacky way to 'add' an offset to an enum, which just
        # returns a new tuple with the right values
        print(self.value)
        return (self.value[0]+offset, self.value[1])