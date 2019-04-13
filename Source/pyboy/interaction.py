#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from . import windowevent


P10, P11, P12, P13, P14, P15 = range(6)


def reset_bit(x, bit):
    return x & ~(1 << bit)


def set_bit(x, bit):
    return x | (1 << bit)


class Interaction():
    def __init__(self):
        self.directional = 0xF
        self.standard = 0xF

    def key_event(self, key):
        if key == windowevent.PRESSARROWRIGHT:
            self.directional = reset_bit(self.directional, P10)
        elif key == windowevent.PRESSARROWLEFT:
            self.directional = reset_bit(self.directional, P11)
        elif key == windowevent.PRESSARROWUP:
            self.directional = reset_bit(self.directional, P12)
        elif key == windowevent.PRESSARROWDOWN:
            self.directional = reset_bit(self.directional, P13)
        elif key == windowevent.PRESSBUTTONA:
            self.standard = reset_bit(self.standard, P10)
        elif key == windowevent.PRESSBUTTONB:
            self.standard = reset_bit(self.standard, P11)
        elif key == windowevent.PRESSBUTTONSELECT:
            self.standard = reset_bit(self.standard, P12)
        elif key == windowevent.PRESSBUTTONSTART:
            self.standard = reset_bit(self.standard, P13)
        elif key == windowevent.RELEASEARROWRIGHT:
            self.directional = set_bit(self.directional, P10)
        elif key == windowevent.RELEASEARROWLEFT:
            self.directional = set_bit(self.directional, P11)
        elif key == windowevent.RELEASEARROWUP:
            self.directional = set_bit(self.directional, P12)
        elif key == windowevent.RELEASEARROWDOWN:
            self.directional = set_bit(self.directional, P13)
        elif key == windowevent.RELEASEBUTTONA:
            self.standard = set_bit(self.standard, P10)
        elif key == windowevent.RELEASEBUTTONB:
            self.standard = set_bit(self.standard, P11)
        elif key == windowevent.RELEASEBUTTONSELECT:
            self.standard = set_bit(self.standard, P12)
        elif key == windowevent.RELEASEBUTTONSTART:
            self.standard = set_bit(self.standard, P13)

    def pull(self, joystickbyte):
        P14 = (joystickbyte >> 4) & 1
        P15 = (joystickbyte >> 5) & 1
        # Bit 7 - Not used (No$GMB)
        # Bit 6 - Not used (No$GMB)
        # Bit 5 - P15 out port
        # Bit 4 - P14 out port
        # Bit 3 - P13 in port
        # Bit 2 - P12 in port
        # Bit 1 - P11 in port
        # Bit 0 - P10 in port

        # Guess to make first 4 and last 2 bits true, while keeping
        # selected bits
        joystickByte = 0xFF & (joystickbyte | 0b11001111)
        if P14 == 1 and P15 == 1:
            pass
        elif P14 == 0 and P15 == 0:
            pass
        elif P14 == 0:
            joystickByte &= self.directional
        elif P15 == 0:
            joystickByte &= self.standard

        return joystickByte
