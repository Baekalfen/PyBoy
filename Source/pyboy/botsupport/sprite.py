#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from pyboy.lcd import LCDCRegister


OAM_OFFSET = 0x8000
LCDC_OFFSET = 0xFF40


class Sprite():
    def __init__(self, mb, index):
        self.mb = mb
        self.index = index
        self.offset = index*4

    def get_y(self):
        return self.mb.getitem(OAM_OFFSET + self.offset + 0)

    def get_x(self):
        return self.mb.getitem(OAM_OFFSET + self.offset + 1)

    def get_tile(self):
        return self.mb.getitem(OAM_OFFSET + self.offset + 2)

    def get_attributes(self):
        attr = self.mb.getitem(OAM_OFFSET + self.offset+3)
        return {
            "OBJ-to-BG Priority": get_bit(attr, 7),
            "Y flip": get_bit(attr, 6),
            "X flip": get_bit(attr, 5),
            # non-CGB only
            "Palette number": get_bit(attr, 4),
            # CGB only
            # "Tile VRAM-bank": get_bit(attr, 3),
            # "Palette number": val & 0b11,
        }

    def is_on_screen(self):
        LCDC = LCDCRegister(self.mb.getitem(LCDC_OFFSET))
        spritesize = 16 if LCDC.sprite_size else 16
        return (0 < self.get_y() < 144 + spritesize and
                0 < self.get_x() < 160 + 8)


def get_bit(val, bit):
    return (val & (1 << bit)) >> bit
