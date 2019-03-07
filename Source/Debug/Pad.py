# -*- encoding: utf-8 -*-
#
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
        self.cell_data = None
        self.cell_widths = None
        if not cell_data is None:
            self.setData(cell_data, cell_widths)

    def setData(self, data, widths):
        assert not data is None and not widths is None
        assert (len(data[0]) == len(widths))
        self.cell_data = data
        self.cell_widths = widths

    def updatePad(self):
        if not (self.cell_data is None):
            for i in range(min(len(self.cell_data), self.height)):
                # print ("%s %s %s" % (len(self.cell_data), i, self.scroll_line)), '\r'
                # if len(self.cell_data) >= i+self.scroll_line:
                #     break
                n = self.cell_data[i+self.scroll_line]
                # else:
                #     n = ['~' for _ in self.cell_widths]
                self._screen.move(i, 0)
                self._screen.clrtoeol()

                self.addLabelsInColumns(i, 0, n, self.cell_widths)
        self._screen.refresh(0, 0, self.win_line, self.win_column,self.height+self.win_line, self.width+self.win_column)
        # self._screen.refresh(self.scroll_line, self.scroll_column, self.win_line, self.win_column,self.height+self.win_line, self.width+self.win_column)

