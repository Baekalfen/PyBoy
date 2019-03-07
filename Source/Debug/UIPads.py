# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from Pad import Pad
from Window import Window
import curses

class ProgramPad(Pad):
    def __init__(self, placement, size):
        super(ProgramPad, self).__init__(placement, size)

    def switch(self):
        self._screen.move(0, 0)

class FlagPad(Pad):
    def __init__(self, placement, size):
        super(FlagPad, self).__init__(placement, size)

class RegistersPad(Pad):
    def __init__(self, placement, size):
        super(RegistersPad, self).__init__(placement, size)

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
        # print " ".join([str(x) for x in args])+'\r'

        self._screen.scrollok(True)
        self._screen.addstr(" ".join([str(x) for x in args])+'\n')
        self.line = min(self.line+1, self.max_line)
        # self._screen.refresh()
        # pass

    def updatePad(self):
        self._screen.refresh()


