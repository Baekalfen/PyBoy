#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .base_mbc import BaseMBC


class MBC5(BaseMBC):
    def setitem(self, address, value):
        raise NotImplementedError()
