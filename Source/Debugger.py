# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sdl2
import sdl2.ext
import numpy
from MathUint8 import getBit

import time

white = sdl2.ext.Color(0xFF,0xFF,0xFF)
black = sdl2.ext.Color(0x00,0x00,0x00)



class Debugger():
    def __init__(self, mb):
        self.mb = mb

    def tick(self):
        raise Exception("Debugger shouldn't be called!")
        pass

    #     pc = self.mb.cpu.PC.getInt()
    #     if self.oldPC is None or not self.oldPC == pc:
    #         self.oldPC = pc
    #         self.window.drawFill(white,self.window.programScreen)

    #         self.drawRegisters()
    #         self.drawProgram()

    # def drawRegisters(self):
    #     self.window.drawFill(white,self.window.registerScreen)
    #     drawSize = (160,180)
    #     for i,r in enumerate(['A','F','B','C','D','E','H','L','SP','PC']):
    #         if i<8:
    #             coordinate = [(i%2)*(drawSize[0]/2)-1,(i/2)*(drawSize[1]/6)-1,drawSize[0]/2,drawSize[1]/6]
    #         else:
    #             i = i+(i-8)*2
    #             coordinate = [                     -1,(i/2)*(drawSize[1]/6)-1,drawSize[0]  ,drawSize[1]/6]

    #         self.window.drawRect(coordinate,black,self.window.registerScreen)
    #         self.window.drawText(r+": %s" % eval("self.mb.cpu."+r),14,(coordinate[0]+10,coordinate[1]+5),black,self.window.registerScreen)



    # def drawProgram(self):
    #     pc = self.mb.cpu.PC.getInt()
    #     for n in xrange(9):
    #         opcode = ord(self.mb.cpu.bootROM[pc])
    #         if opcode == 0xCB: #Extension code
    #             pc += 1
    #             opcode = ord(self.mb.cpu.bootROM[pc])
    #             opcode += 0xFF #Internally shifting look-up table

    #         text = opcodeToText.opcodeToText[opcode]
    #         # inst = self.mb.cpu.fetchInstruction(pc)
    #         # _, text = self.mb.cpu.resolveTokens(inst)
    #         # text = str(opcodeToText.opcodeToText[inst.operation.value]).ljust(4) + text
    #         # print inst.operation.value
    #         # pc = inst[1][2]
    #         self.window.drawText(text,14,(0,n*20,0,0),black,self.window.programScreen)

    # def setupDebug(self):
    #     # Blit to white
    #     self.drawFill(white,self.debugScreen)

    #     # Opcodes from PC
    #     drawFrom = (0,0)
    #     drawSize = (160,200)
    #     self.drawRect(tuple(drawFrom+drawSize),black,self.debugScreen)
    #     self.drawText("Program",12,(drawFrom[0]+5,drawFrom[1]+2),black,self.debugScreen)
    #     self.drawLine((drawFrom[0],drawFrom[1]+18),(drawFrom[0]+drawSize[0]-1,drawFrom[1]+18),black,self.debugScreen)
    #     self.programScreen = self.debugScreen.subsurface((drawFrom[0]+1,drawFrom[1]+19),(drawSize[0]-2,drawSize[1]-20))
    #     self.drawFill(white,self.programScreen)

    #     # CPU Registers
    #     drawFrom = (159,0)
    #     drawSize = (160,200)
    #     self.drawRect(tuple(drawFrom+drawSize),black,self.debugScreen)
    #     self.drawText("Registers",12,(drawFrom[0]+5,drawFrom[1]+2),black,self.debugScreen)
    #     self.drawLine((drawFrom[0],drawFrom[1]+18),(drawFrom[0]+drawSize[0]-1,drawFrom[1]+18),black,self.debugScreen)
    #     self.registerScreen = self.debugScreen.subsurface((drawFrom[0]+1,drawFrom[1]+19),(drawSize[0]-2,drawSize[1]-20))
    #     self.drawFill(white,self.registerScreen)

    #     # Break points
    #     drawFrom = (318,0)
    #     drawSize = (322,200)
    #     self.drawRect(tuple(drawFrom+drawSize),black,self.debugScreen)
    #     self.drawText("Break on",12,(drawFrom[0]+5,drawFrom[1]+2),black,self.debugScreen)
    #     self.drawLine((drawFrom[0],drawFrom[1]+18),(drawFrom[0]+drawSize[0]-1,drawFrom[1]+18),black,self.debugScreen)
    #     self.breakScreen = self.debugScreen.subsurface((drawFrom[0]+1,drawFrom[1]+19),(drawSize[0]-2,drawSize[1]-20))
    #     self.drawFill(white,self.breakScreen)

    #     # Interrupt registers

    #     # Tilemap

    # def drawBitmap(self, bitmap, screen = None):
    #     if screen is None:
    #         screen = self._screenScaled

    # def drawTile(self, sprite, screen = None):
    #     if screen is None:
    #         screen = self._screenScaled

    # def drawText(self, text, size, point, color, screen = None):
    #     return
    #     if screen is None:
    #         screen = self._screenScaled

    #     # Avoid initiating the font every time
    #     if self.fonts.get(size) is None:
    #         self.fonts[size] = pygame.font.SysFont("VeraMono.ttf", size)
    #         # self.fonts[size] = pygame.font.SysFont("PT Mono", size)

    #     text = self.fonts[size].render(text, True, color)
    #     screen.blit(text, point)

    # def drawRect(self, rect, color, screen = None):
    #     if screen is None:
    #         screen = self._screenScaled

    #     p0 = (rect[0],rect[1])
    #     p1 = (rect[1],rect[2])
    #     p2 = (rect[2],rect[3])
    #     p3 = (rect[3],rect[0])

    #     sdl2.ext.line(screen, color, p0+p1)
    #     sdl2.ext.line(screen, color, p1+p2)
    #     sdl2.ext.line(screen, color, p2+p3)
    #     sdl2.ext.line(screen, color, p3+p0)

    # def drawLine(self, p1, p2, color, screen = None):
    #     if screen is None:
    #         screen = self._screenScaled
    #     sdl2.ext.line(screen, color, p1+p2)
