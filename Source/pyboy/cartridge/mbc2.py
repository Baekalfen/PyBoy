#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from .mbc import MBC


class MBC2(MBC):
    def setitem(self, address, value):
        raise NotImplementedError()
