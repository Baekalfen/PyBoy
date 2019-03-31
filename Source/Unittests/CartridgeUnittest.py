# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from Cartridge import *

import unittest

cart = Cartridge("pokemon_blue.gb")


class Test_Cartridge(unittest.TestCase):

    def test_Platform(self):
        dataRead = cart[0x143]
        dataCheck = 0x80  # GGBCPUman.pdf p. 10: $80 = Color GB, $00 or other = not Color GB

        self.assertNotEqual(dataRead, dataCheck)

    def test_GameName(self):
        dataRead = cart[0x134:0x143]
        dataCheck = [0x50, 0x4F, 0x4B, 0x45, 0x4D, 0x4F, 0x4E, 0x20,  #POKEMON␣
                     0x42, 0x4C, 0x55, 0x45, 0x00, 0x00, 0x00]        #BLUE\0\0\0

        self.assertEqual(len(dataRead), 15)
        self.assertEqual(len(dataCheck), 15)
        self.assertEqual(dataRead, dataCheck)

    def test_NintendoLogo(self):
        dataRead = cart[0x104:0x134]
        dataCheck = [0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B,
                     0x03, 0x73, 0x00, 0x83, 0x00, 0x0C, 0x00, 0x0D,
                     0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E,
                     0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99,
                     0xBB, 0xBB, 0x67, 0x63, 0x6E, 0x0E, 0xEC, 0xCC,
                     0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E]

        self.assertEqual(len(dataRead), len(dataCheck))
        self.assertEqual(dataRead, dataCheck)

    def test_Checksum(self):
        # 014E-014F Checksum (higher byte first) produced by adding all bytes of a cartridge except for
        # two checksum bytes and taking two lower bytes of the result. (GameBoy
        # ignores this value.)
        pass

    def test_Complement(self):
        # 014D Complement check
        # (PROGRAM WON'T RUN ON GB IF NOT CORRECT!!!)
        # (It will run on Super GB, however, if incorrect.)
        pass

if __name__ == '__main__':
    unittest.main()
