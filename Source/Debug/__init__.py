# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import curses
from MainWindow import MainWindow
from Pad import Pad
from UIPads import ProgramPad, ConsolePad, RegistersPad, FlagPad


class Debug():
    def __init__(self):
        self.window = MainWindow()

        height, width = self.window._screen.getmaxyx()

        registers_width = 9
        console_height = 20
        console_width = min(80,width-registers_width)-1

        self.program = ProgramPad((2, 1),(height-console_height-2-1, width-30))
        self.console = ConsolePad((height-console_height, 1),(console_height, console_width))
        registers = RegistersPad((height-console_height, console_width+2),(7, registers_width))
        flags = FlagPad((height-console_height, console_width+registers_width+3),(7, 7))

        self.pads = [self.program, self.console, registers, flags]
        self.running = False
        self.console.switch()

    def tick(self):
        if self.running:
            self.console.switch()
            try:
                c = self.window.getKey()
                if c == -1:
                    self.program.updatePad()
                elif c == ord("q"):
                    raise KeyboardInterrupt()
                elif c == curses.KEY_UP:
                    if self.program.scroll_line > 0:
                        self.program.scroll_line -= 1
                elif c == curses.KEY_DOWN:
                    self.program.scroll_line += 1

                #TODO: Don't update everything when not necesarry
                map(lambda p: p.updatePad(), self.pads)
            except KeyboardInterrupt:
                self.quit()
                return False
        else:
            self.console.updatePad()
            self.program.switch()
        return True

    def quit(self):
        self.window._screen.move(0, 0)
        self.window.quit()
