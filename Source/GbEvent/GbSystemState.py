# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#


class GbSystemState(object):

    def __init__(self):
        self.quit = False
        self.debug = False
        self.dpadControl = 0xF
        self.buttonControl = 0xF
        self.speedMultiplier = 1.0

    def getInputState(self, input_reg):

        P14 = (input_reg >> 4) & 1
        P15 = (input_reg >> 5) & 1

        input_reg = 0xFF & (input_reg | 0b11001111)
        if P14 == 1 and P15 == 1:
            pass
        elif P14 == 0 and P15 == 0:
            pass
        elif P14 == 0:
            input_reg &= self.dpadControl
        elif P15 == 0:
            input_reg &= self.buttonControl

        return input_reg
