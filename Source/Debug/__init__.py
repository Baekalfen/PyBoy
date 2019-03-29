# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import curses
import logging
import PyBoy.Logger
from PyBoy.Logger import logger
from MainWindow import MainWindow
from Pad import Pad
from UIPads import ProgramPad, ConsolePad, RegistersPad, FlagPad
from PyBoy.opcodeToName import CPU_COMMANDS, CPU_COMMANDS_EXT

class Debug():
    def __init__(self):
        self.mb = None
        self.window = MainWindow()

        height, width = self.window._screen.getmaxyx()

        registers_width = 9
        console_height = 20
        console_width = min(80,width-registers_width)-1

        self.program = ProgramPad((2, 1),(height-console_height-2-1, width-30))
        self.registers = RegistersPad((height-console_height, console_width+2),(7, registers_width))
        self.flags = FlagPad((height-console_height, console_width+registers_width+3),(7, 7))

        self.console = ConsolePad((height-console_height, 1),(console_height, console_width))
        logger.setLevel(logging.DEBUG)
        ch = CursesHandler(self.console)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter('%(relativeCreated)-8d %(levelname)-8s %(message)s'))
        logger.addHandler(ch)

        self.pads = [self.program, self.console, self.registers, self.flags]
        self.running = False
        self.console.switch()

        self.commandBuffer = []

    def tick(self):
        if self.running:
            try:
                self.console.switch()
                c = self.window.getKey()
                if c == -1:
                    self.program.updatePad()
                    self.commandBuffer = []
                # elif ord("0") <= c <= ord("9"):
                #     self.commandBuffer.append(c - ord(0))
                # elif c == ord("G"):
                #     if len(self.commandBuffer) > 0:
                #         try:
                #             line = 0
                #             for n in self.commandBuffer:
                #                 line == line << 8
                #                 line += n
                #             self.program.scroll_line = line
                #         except:
                #             logger.warn("Error in GOTO command")
                elif c == ord("u"):
                    self.program.scroll_line -= self.program.height/2
                    self.program.scroll_line = max(self.program.scroll_line, 0)
                elif c == ord("d"):
                    self.program.scroll_line += self.program.height/2
                elif c == ord("q"):
                    raise KeyboardInterrupt()
                elif c == curses.KEY_UP:
                    if self.program.scroll_line > 0:
                        self.program.scroll_line -= 1
                elif c == curses.KEY_DOWN:
                    self.program.scroll_line += 1

                if not self.mb is None:
                    self.program.setData(self.getProgramData(), [8, 6, 4, 10])
                    self.registers.setData(
                        [
                            ["Registers",""],
                            ['AF:',"%0.2x%0.2x" % (self.mb.cpu.reg[0], self.mb.cpu.reg[1])],
                            ['BC:',"%0.2x%0.2x" % (self.mb.cpu.reg[2], self.mb.cpu.reg[3])],
                            ['DE:',"%0.2x%0.2x" % (self.mb.cpu.reg[4], self.mb.cpu.reg[5])],
                            ['HL:',"%0.2x%0.2x" % (self.mb.cpu.reg[6], self.mb.cpu.reg[7])],
                            ['SP:',"%0.4x" % (self.mb.cpu.reg[8])],
                            ['PC:',"%0.4x" % (self.mb.cpu.reg[9])],
                        ],
                        [4,4]
                    )
                    self.flags.setData(
                        [
                            ["Flags",""],
                            ['z',"%d" % self.mb.cpu.testFlag(7)],
                            ['n',"%d" % self.mb.cpu.testFlag(6)],
                            ['h',"%d" % self.mb.cpu.testFlag(5)],
                            ['c',"%d" % self.mb.cpu.testFlag(4)]
                        ],
                        [3,2]
                    )

                #TODO: Don't update everything when not necesarry
                self.program.updatePad()
                self.console.updatePad()
                self.registers.updatePad()
                self.flags.updatePad()
                # self.program.switch()
                # map(lambda p: p.updatePad(), self.pads)
            except KeyboardInterrupt:
                # self.quit()
                return False
        else:
            self.console.updatePad()
            # self.program.switch()
        return True

    def quit(self):
        self.window._screen.move(0, 0)
        self.window.quit()

    def getProgramData(self):
        lines = []
        n = 0
        # for _ in xrange(self.program.height*10):
        while True:
            addr = n + self.program.scroll_line

            if addr > 0xFFFF:
                return lines

            info = self.addrInfo(addr)
            opcode = self.mb.getitem(addr)
            lines.append([
                info,
                "%0.4x" % addr,
                "%0.2x" % opcode,
                CPU_COMMANDS[opcode]
            ])
            n += self.mb.cpu.opcodes[opcode][0]
        return lines

    def addrInfo(self, addr):
        info = ""
        if addr < 0x4000:
            info = "ROM0"
        elif addr < 0x8000:
            info = "ROM%d" % self.mb.cartridge.ROMBankSelected
        elif addr < 0xA000:
            info = "VRAM"
        elif addr < 0xC000:
            info = "RAM%d" % self.mb.cartridge.RAMBankSelected
        elif addr < 0xFE00:
            info = "RAM"
        elif addr < 0xFEA0:
            info = "OAM"
        elif addr < 0xFF00:
            pass # "Empty, unusable for I/O"
        elif addr < 0xFF4C:
            info = "I/O"
        elif addr < 0xFF80:
            pass # "Empty, unusable for I/O"
        elif addr < 0xFFFF:
            info = "RAM"
        elif addr == 0xFFFF:
            info = "IntrEn"
        return info

class CursesHandler(logging.Handler):
    def __init__(self, consolePad):
        logging.Handler.__init__(self)
        self.consolePad = consolePad

    def emit(self, record):
        try:
            self.consolePad.writeLine(self.format(record))
        except:
            self.handleError(record)

