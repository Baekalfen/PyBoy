# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import Global
# if not Global.isPyPy:
import cython
import array

# MEMORY SIZES
# if not cython.compiled:
INTERNAL_RAM_0 = 8 * 1024  # 8KB
NON_IO_INTERNAL_RAM0 = 0x60
IO_PORTS = 0x4C
NON_IO_INTERNAL_RAM1 = 0x34
INTERNAL_RAM_1 = 0x7F
INTERRUPT_ENABLE_REGISTER = 1
###########

class RAM():

    def __init__(self, random=False):
        if random: #NOTE: In real life, the RAM is scrambled with random data on boot.
            raise Exception("Random RAM not implemented")

        self.internalRAM0 = array.array('B', [0]*(INTERNAL_RAM_0))
        self.nonIOInternalRAM0 = array.array('B', [0]*(NON_IO_INTERNAL_RAM0))
        self.IOPorts = array.array('B', [0]*(IO_PORTS))
        self.internalRAM1 = array.array('B', [0]*(INTERNAL_RAM_1))
        self.nonIOInternalRAM1 = array.array('B', [0]*(NON_IO_INTERNAL_RAM1))
        self.interruptRegister = array.array('B', [0]*(INTERRUPT_ENABLE_REGISTER))


    def listToHex(self,a,truncate = True, offset=0):
        output = "%s00%s08%s0F\n" % (" "*7," "*(22)," "*(19))

        bytesPerRow = 16
        getSlice = lambda a,x: a[x*bytesPerRow:min(len(a),(x+1)*bytesPerRow)]
        prevWasZero = False

        # Rounding up trick. 0x34 -> 0x40. 0xFF -> 0xFF.
        # To not miss last not bytesPerRow-divisible bytes
        for n in range((len(a)+(bytesPerRow-1))/bytesPerRow):
            currentSlice = getSlice(a,n)

            if truncate and (n == ((len(a)+(bytesPerRow-1))/bytesPerRow)-1) and prevWasZero:
                output += " ... \n"
                pass
            elif truncate and sum(currentSlice) == 0 and prevWasZero:
                continue
            elif truncate and sum(currentSlice) != 0 and prevWasZero:
                output += " ... \n"


            output += "0x%0*X " % (4,(n*bytesPerRow)+offset)
            output += " ".join(["%0*X" % (2,x) for x in currentSlice])
            output += "\n"

            prevWasZero = (sum(currentSlice) == 0)

        return output

    def dump(self):
        dump = "Dump of ROM:\n"
        # dump += "self.bootROMEnabled: " + str(self.bootROMEnabled) + "\n"
        # dump += "self.bootROM:\n"
        # dump += self.listToHex(self.MB.bootROM) + "\n"
        # dump += "self.cartridge:\n"
        # dump += str(self.cartridge) + "\n"
        # dump += "self.cartridge.ROMBanks\n"
        # for i,bank in enumerate(self.cartridge.ROMBanks):
        #     dump += "Bank: %s" % i
        #     dump += self.listToHex(bank,offset=i*16*1024) + "\n" #Offset of 16KB
        # dump += "self.interaction:\n"
        # dump += str(self.interaction) + "\n"
        dump += "self.VRAM:\n"
        dump += self.listToHex(self.VRAM) + "\n"
        dump += "self.internalRAM0:\n"
        dump += self.listToHex(self.internalRAM0) + "\n"
        dump += "self.OAM:\n"
        dump += self.listToHex(self.OAM) + "\n"
        dump += "self.nonIOInternalRAM0:\n"
        dump += self.listToHex(self.nonIOInternalRAM0) + "\n"
        dump += "self.IOPorts:\n"
        dump += self.listToHex(self.IOPorts) + "\n"
        dump += "self.internalRAM1:\n"
        dump += self.listToHex(self.internalRAM1) + "\n"
        dump += "self.nonIOInternalRAM1:\n"
        dump += self.listToHex(self.nonIOInternalRAM1) + "\n"
        dump += "self.interruptRegister:\n"
        dump += self.listToHex(self.interruptRegister) + "\n"

        return dump


    def __str__(self):
        string = "Memory dump:\n"
        for i in 0xFF:
            for j in 0xFF:
                string += self[j+i]
            string += "\n"
        return string
