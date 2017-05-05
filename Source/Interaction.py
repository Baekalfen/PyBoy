# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from GbEvent.WindowEvent import WindowEvent
import CoreDump
from MathUint8 import  resetBit, setBit
# from PrimitiveTypes import uint8

P10, P11, P12, P13, P14, P15 = range(0,6)

class Interaction():
    def __init__(self):
        self.directional = 0xF
        self.standard = 0xF

    def keyEvent(self, key):
        if key == WindowEvent.PressArrowRight:
            self.directional = resetBit(self.directional, P10)
        elif key == WindowEvent.PressArrowLeft:
            self.directional = resetBit(self.directional, P11)
        elif key == WindowEvent.PressArrowUp:
            self.directional = resetBit(self.directional, P12)
        elif key == WindowEvent.PressArrowDown:
            self.directional = resetBit(self.directional, P13)

        elif key == WindowEvent.PressButtonA:
            self.standard = resetBit(self.standard, P10)
        elif key == WindowEvent.PressButtonB:
            self.standard = resetBit(self.standard, P11)
        elif key == WindowEvent.PressButtonSelect:
            self.standard = resetBit(self.standard, P12)
        elif key == WindowEvent.PressButtonStart:
            self.standard = resetBit(self.standard, P13)


        elif key == WindowEvent.ReleaseArrowRight:
            self.directional = setBit(self.directional, P10)
        elif key == WindowEvent.ReleaseArrowLeft:
            self.directional = setBit(self.directional, P11)
        elif key == WindowEvent.ReleaseArrowUp:
            self.directional = setBit(self.directional, P12)
        elif key == WindowEvent.ReleaseArrowDown:
            self.directional = setBit(self.directional, P13)

        elif key == WindowEvent.ReleaseButtonA:
            self.standard = setBit(self.standard, P10)
        elif key == WindowEvent.ReleaseButtonB:
            self.standard = setBit(self.standard, P11)
        elif key == WindowEvent.ReleaseButtonSelect:
            self.standard = setBit(self.standard, P12)
        elif key == WindowEvent.ReleaseButtonStart:
            self.standard = setBit(self.standard, P13)

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
            pass
        elif P14 == 0:
            joystickByte &= self.directional
        elif P15 == 0:
            joystickByte &= self.standard

        return joystickByte
