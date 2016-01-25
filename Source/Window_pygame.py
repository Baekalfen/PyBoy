# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pygame
from WindowEvent import WindowEvent
from colors import black, white

class Window():

    def __init__(self, scale=1, debug=False):
        if not isinstance(scale, int):
            raise Exception("Window scale has to be an integer!")

        print "Pygame initialization. Passed:%s Failed:%s" % pygame.init()
        pygame.font.init()
        self.fonts = {}
        gameboyResolution = (160, 144)
        self._scaledResolution = tuple(x * scale for x in gameboyResolution)
        if debug:
            self._windowScreen = pygame.display.set_mode((self._scaledResolution[0] + 640, 576))
            self.debugScreen = self._windowScreen.subsurface((self._scaledResolution[0], 0), (640, 576))
            self.drawFill((0,255,0),self.debugScreen)
        else:
            self._windowScreen = pygame.display.set_mode(self._scaledResolution)
        self._screenScaled = self._windowScreen.subsurface((0, 0), self._scaledResolution)
        self._screen = pygame.Surface(gameboyResolution)
        pygame.display.set_caption("PyBoy")
        pygame.key.set_repeat(16,16)

    def getEvents(self):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append(WindowEvent.Quit)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    events.append(WindowEvent.ArrowLeft)
                elif event.key == pygame.K_RIGHT:
                    events.append(WindowEvent.ArrowRight)
                elif event.key == pygame.K_UP:
                    events.append(WindowEvent.ArrowUp)
                elif event.key == pygame.K_DOWN:
                    events.append(WindowEvent.ArrowDown)
                # The following should be configurable
                elif event.key == pygame.K_a:
                    events.append(WindowEvent.ButtonA)
                elif event.key == pygame.K_s:
                    events.append(WindowEvent.ButtonB)
                elif event.key == pygame.K_z:
                    events.append(WindowEvent.ButtonA)
                elif event.key == pygame.K_x:
                    events.append(WindowEvent.ButtonB)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    events.append(WindowEvent.ButtonStart)
                elif event.key == pygame.K_BACKSPACE:
                    events.append(WindowEvent.ButtonSelect)
                elif event.key == pygame.K_w:
                    events.append(WindowEvent.DebugNext)
        return events

    def drawFill(self, color, screen = None):
        if screen is None:
            screen = self._screen
        screen.fill(color)

    def drawBitmap(self, bitmap, screen = None):
        if screen is None:
            screen = self._screen

    def drawTile(self, sprite, screen = None):
        if screen is None:
            screen = self._screen

    def drawText(self, text, size, point, color, screen = None):
        if screen is None:
            screen = self._screen

        # Avoid initiating the font every time
        if self.fonts.get(size) is None:
            self.fonts[size] = pygame.font.SysFont("VeraMono.ttf", size)
            # self.fonts[size] = pygame.font.SysFont("PT Mono", size)

        text = self.fonts[size].render(text, True, color)
        screen.blit(text, point)

    def drawRect(self, rect, color, screen = None, width = 1):
        if screen is None:
            screen = self._screen
        pygame.draw.rect(screen, color, rect, width)

    def drawLine(self, p1, p2, color, screen = None, width = 1):
        if screen is None:
            screen = self._screen
        pygame.draw.line(screen, color, p1, p2, width)

    def setupDebug(self):
        # Blit to white
        self.drawFill(white,self.debugScreen)

        # Opcodes from PC
        drawFrom = (0,0)
        drawSize = (160,200)
        self.drawRect(tuple(drawFrom+drawSize),black,self.debugScreen)
        self.drawText("Program",12,(drawFrom[0]+5,drawFrom[1]+2),black,self.debugScreen)
        self.drawLine((drawFrom[0],drawFrom[1]+18),(drawFrom[0]+drawSize[0]-1,drawFrom[1]+18),black,self.debugScreen)
        self.programScreen = self.debugScreen.subsurface((drawFrom[0]+1,drawFrom[1]+19),(drawSize[0]-2,drawSize[1]-20))
        self.drawFill(white,self.programScreen)

        # CPU Registers
        drawFrom = (159,0)
        drawSize = (160,200)
        self.drawRect(tuple(drawFrom+drawSize),black,self.debugScreen)
        self.drawText("Registers",12,(drawFrom[0]+5,drawFrom[1]+2),black,self.debugScreen)
        self.drawLine((drawFrom[0],drawFrom[1]+18),(drawFrom[0]+drawSize[0]-1,drawFrom[1]+18),black,self.debugScreen)
        self.registerScreen = self.debugScreen.subsurface((drawFrom[0]+1,drawFrom[1]+19),(drawSize[0]-2,drawSize[1]-20))
        self.drawFill(white,self.registerScreen)

        # Break points
        drawFrom = (318,0)
        drawSize = (322,200)
        self.drawRect(tuple(drawFrom+drawSize),black,self.debugScreen)
        self.drawText("Break on",12,(drawFrom[0]+5,drawFrom[1]+2),black,self.debugScreen)
        self.drawLine((drawFrom[0],drawFrom[1]+18),(drawFrom[0]+drawSize[0]-1,drawFrom[1]+18),black,self.debugScreen)
        self.breakScreen = self.debugScreen.subsurface((drawFrom[0]+1,drawFrom[1]+19),(drawSize[0]-2,drawSize[1]-20))
        self.drawFill(white,self.breakScreen)

        # Interrupt registers

        # Tiledata

    def updateDisplay(self):
        pygame.transform.scale(
            self._screen, self._scaledResolution, self._screenScaled)
        pygame.display.flip()

    def stop(self):
        pygame.quit()

if __name__ == "__main__":
    debug = True
    window = Window(4, debug)

    window.drawFill(white)
    window.drawLine((5, 5), (40, 40), (0, 0, 0))

    window.setupDebug()
    window.updateDisplay()

    done = False
    clock = pygame.time.Clock()
    while not done:
        for event in window.getEvents():
            if event == WindowEvent.Quit:
                done = True
        clock.tick(60)
    pygame.quit()
