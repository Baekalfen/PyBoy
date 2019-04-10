#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from .GenericMBC import GenericMBC

class MBC5(GenericMBC):
    def setitem(self, address, value):
        raise Exception("Not implemented")

