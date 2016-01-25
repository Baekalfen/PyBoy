# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from WindowEvent import WindowEvent
import CoreDump
# from PrimitiveTypes import uint8


class Interaction():
    def __init__(self):
        self.stack = []

    def keyPressed(self, key):
        self.stack.append(key)

    def flush(self):
        self.stack = []

    def pull(self, joystickByte):
        P14 = (joystickByte >> 4) & 1
        P15 = (joystickByte >> 5) & 1

        # Bit 7 - Not used (No$GMB)
        # Bit 6 - Not used (No$GMB)
        # Bit 5 - P15 out port
        # Bit 4 - P14 out port
        # Bit 3 - P13 in port
        # Bit 2 - P12 in port
        # Bit 1 - P11 in port
        # Bit 0 - P10 in port

        joystickByte = 0xFF & (joystickByte | 0b11001111) # Guess to make first 4 and last 2 bits true, while keeping selected bits

        if P14 == 1 and P15 == 1:
            pass
        elif P14 == 0 and P15 == 0:
            raise CoreDump.CoreDump("Undefined behavior")
        elif P14 == 0:
            for key in self.stack:
                if key == WindowEvent.ArrowRight:
                    joystickByte ^= 1<<0 # P10
                elif key == WindowEvent.ArrowLeft:
                    joystickByte ^= 1<<1 # P11
                elif key == WindowEvent.ArrowUp:
                    joystickByte ^= 1<<2 # P12
                elif key == WindowEvent.ArrowDown:
                    joystickByte ^= 1<<3 # P13
        elif P15 == 0:
            for key in self.stack:
                if key == WindowEvent.ButtonA:
                    joystickByte ^= 1<<0 # P10
                elif key == WindowEvent.ButtonB:
                    joystickByte ^= 1<<1 # P11
                elif key == WindowEvent.ButtonSelect:
                    joystickByte ^= 1<<2 # P12
                elif key == WindowEvent.ButtonStart:
                    joystickByte ^= 1<<3 # P13

        return joystickByte
