# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import GenericScreen
import curses

class MainWindow(GenericScreen.GenericScreen):
    def __init__(self):
        self._screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self._screen.keypad(1)
        self._screen.timeout(1000) #ms


        height, width = self._screen.getmaxyx()
        self.fill(0,0,height,width,126)
        self.addLabelsInColumns(0,0, ["Break", "menu1", "menu2"], [6,6,6])
        self.addLabelsInColumns(1,1, ["Info", "Addr", "Op", "Description"], [8, 6, 4, 10])
        self._screen.refresh()

    def getKey(self):
        return self._screen.getch()

    def quit(self):
        curses.echo()
        curses.nocbreak()
        self._screen.keypad(0)
        curses.endwin()

