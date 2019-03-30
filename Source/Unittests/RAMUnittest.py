# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from RAM import RAM
import random
import unittest

# cart = Cartridge("pokemon_blue.gb")

RAM = RAM(None,None,False)

def funky(self,ram,x,y):
    y = y - 1
    r = random.random()

    random.seed(r)
    for n in range(x,y):
        ram[n].setInt(random.randint(0, 255))

    random.seed(r)
    for n in range(x,y):
        self.assertEqual(ram[n],random.randint(0, 255))


class Test_RAM(unittest.TestCase):


    def test_videoRAM(self):
        funky(self,RAM,0x8000,0xA000)

    def test_internalRAM(self):
        funky(self,RAM,0xC000,0xE000)

    def test_ECHOinternalRAM0(self):
        funky(self,RAM,0xE000,0xFE00)

    def test_spriteAttributeMemory(self):
        funky(self,RAM,0xFE00,0xFEA0)

    def test_nonIOInternalRAM0(self):
        funky(self,RAM,0xFEA0,0xFF00)

    def test_IOPorts(self):
        funky(self,RAM,0xFF00+1,0xFF4C)

    def test_nonIOInternalRAM1(self):
        funky(self,RAM,0xFF4C,0xFF80)

    def test_internalRAM1(self):
        funky(self,RAM,0xFF80,0xFFFF)

    def test_interruptRegister(self):
        funky(self,RAM,0xFFFF,0xFFFF)



if __name__ == '__main__':
    unittest.main()
