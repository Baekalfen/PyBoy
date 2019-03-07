# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from .. import CoreDump
from .GenericMBC import GenericMBC

class MBC5(GenericMBC):
    def __setitem__(self, address, value):
        raise Exception("Not implemented")

