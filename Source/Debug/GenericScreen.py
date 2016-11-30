# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import curses

class Screen(object):
    def addLabelsInColumns(self, line, column, labels, cell_widths):
        assert len(labels) == len(cell_widths)

        offset = 0
        for l,c in zip(labels, cell_widths):
            self._screen.addstr(line, column + offset, l)
            offset += c

    def addLabelsOnLine(self, line, column, labels, separator = " "):
        offset = 0
        for l in labels:
            self._screen.addstr(line, offset + column, l + separator)
            offset += len(l + seperator)

    def fill(self, line1,column1,line2,column2, char):
        for l in xrange(line1,line2):
            for c in xrange(column1, column2-1):
                self._screen.addch(l,c,char)
