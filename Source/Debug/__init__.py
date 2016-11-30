# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import curses
from Window import Window
from Pad import Pad
from UIPads import ProgramPad, ConsolePad, RegistersPad, FlagPad


class Debug():
    def __init__(self):
        window = Window()

        height, width = window._screen.getmaxyx()

        registers_width = 9
        console_height = 20
        console_width = min(80,width-registers_width)-1

        program = ProgramPad((2, 1),(height-console_height-2-1, width-30))
        console = ConsolePad((height-console_height, 1),(console_height, console_width))
        registers = RegistersPad((height-console_height, console_width+2),(7, registers_width))
        flags = FlagPad((height-console_height, console_width+registers_width+3),(7, 7))

        pads = [program, console, registers, flags]

    def tick(self):
        try:
            c = window.getKey()
            if c == -1:
                program.updatePad()
            elif c == ord("q"):
                self.quit()
            elif c == curses.KEY_UP:
                if program.scroll_line > 0:
                    program.scroll_line -= 1
            elif c == curses.KEY_DOWN:
                program.scroll_line += 1

            map(lambda p: p.updatePad(), pads)
        except KeyboardInterrupt:
            self.quit()

    def quit(self):
        window._screen.move(0, 0)
        window.quit()
