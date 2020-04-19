#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .base_mbc import BaseMBC


class MBC2(BaseMBC):
    def setitem(self, address, value):
        raise NotImplementedError()
