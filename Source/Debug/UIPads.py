# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from Pad import Pad

class ProgramPad(Pad):
    def __init__(self, placement, size):
        super(ProgramPad, self).__init__(placement, size, ["a","b","c"]*40,[2,2,2]*40)
        # super(ProgramPad, self).__init__()

class FlagPad(Pad):
    def __init__(self, placement, size):
        super(FlagPad, self).__init__(placement, size)
        self._screen.addstr(0,0,"Flags")
        self._screen.addstr(1,0,"z =")
        self._screen.addstr(2,0,"n =")
        self._screen.addstr(3,0,"h =")
        self._screen.addstr(4,0,"c =")

class RegistersPad(Pad):
    def __init__(self, placement, size):
        super(RegistersPad, self).__init__(placement, size)
        self._screen.addstr(0,0,"Registers")
        self._screen.addstr(1,0,"AF:")
        self._screen.addstr(2,0,"BC:")
        self._screen.addstr(3,0,"DE:")
        self._screen.addstr(4,0,"HL:")
        self._screen.addstr(5,0,"SP:")
        self._screen.addstr(6,0,"PC:")


class ConsolePad(Pad):
    def __init__(self, placement, size):
        super(ConsolePad, self).__init__(placement, size, ["a","b","c"]*30,[2,2,2]*30)

