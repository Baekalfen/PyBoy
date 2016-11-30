# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import GenericScreen
import curses

class Window(GenericScreen.GenericScreen):
    def __init__(self, (win_line, win_column), (height, width)):
        self._screen = curses.newwin(height,width,win_line,win_column)



