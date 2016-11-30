# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import GenericScreen
import curses

class Pad(GenericScreen.GenericScreen):
    def __init__(self, (win_line, win_column), (height, width), cell_data=None, cell_widths=None):
        self.win_line = win_line
        self.win_column = win_column
        self.scroll_line = 0
        self.scroll_column = 0
        self.height = height
        self.width = width
        self._screen = curses.newpad(height, width)
        self.setData(cell_data, cell_widths)

    def setData(self, data, widths):
        assert (len(data) == len(widths)) if not (data is None) else True
        self.cell_data = data
        self.cell_widths = widths

    def updatePad(self):
        if not (self.cell_data is None):
            for i in range(self.scroll_line, self.scroll_line + self.height):
                n = self.cell_data[i]
                self._screen.move(i, 0)
                self._screen.clrtoeol()

                self.addLabelsInColumns(i, 0, [str(i), n], [3,5])
        self._screen.refresh(self.scroll_line, self.scroll_column, self.win_line, self.win_column,self.height+self.win_line, self.width+self.win_column)

