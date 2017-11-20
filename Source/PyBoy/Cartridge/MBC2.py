# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from .. import CoreDump
from GenericMBC import GenericMBC

class MBC2(GenericMBC):
    def __setitem__(self, address, value):
        raise Exception("Not implemented")

