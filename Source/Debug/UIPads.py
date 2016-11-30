# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from Pad import Pad
from Window import Window
import curses

class ProgramPad(Pad):
    def __init__(self, placement, size):
        super(ProgramPad, self).__init__(placement, size, ["a","b","c"]*40,[2,2,2]*40)
        # super(ProgramPad, self).__init__()

    def switch(self):
        self._screen.move(0, 0)

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


class ConsolePad(Window):
    def __init__(self, placement, (line,column)):
        super(ConsolePad, self).__init__(placement, (line,column))
        self.max_line = line
        self.max_column = column
        self.line = 0
        self._screen.setscrreg(0,line-1)
        # assert self._screen.idlok(1), "Couldn't enable scrolling"
        self.switch()

    def switch(self):
        self._screen.move(self.line, 0)

    def writeLine(self, *args):
        # self._screen.scroll(-1)
        # self._screen.clrtoeol()
        self._screen.scrollok(True)
        self._screen.addstr(" ".join([str(x) for x in args])+'\n')
        self.line = min(self.line+1, self.max_line)

    def updatePad(self):
        self._screen.refresh()


