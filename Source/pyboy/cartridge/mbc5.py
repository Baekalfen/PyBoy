#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from .mbc import MBC


class MBC5(MBC):
    def setitem(self, address, value):
        raise NotImplementedError()
