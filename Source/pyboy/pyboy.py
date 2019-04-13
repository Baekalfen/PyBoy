#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import sys
import time

from . import botsupport
from .screenrecorder import ScreenRecorder
from .motherboard.motherboard import Motherboard
from . import windowevent
from . import window

from .opcode_to_name import CPU_COMMANDS, CPU_COMMANDS_EXT
from .logger import logger, addconsolehandler
addconsolehandler()


SPF = 1/60.  # inverse FPS (frame-per-second)


class PyBoy():
    def __init__(self, win_type, scale, ROM, bootROM=None):
        self.ROM = ROM
        self.debugger = None
        self.window = window.window.getwindow(win_type, scale)

        self.profiling = "profiling" in sys.argv
        self.motherboard = Motherboard(ROM, bootROM, self.window, profiling=self.profiling,
                                       debugger=self.debugger)
        if self.debugger is not None:
            self.debugger.motherboard = self.motherboard

        self.avg_emu = 0
        self.avg_cpu = 0
        self.counter = 0
        self.set_emulation_speed(True, 0)
        self.limit_emulationspeed = True
        self.screen_recorder = None

    def tick(self):
        done = False
        t_start = time.perf_counter()  # Change to _ns when PyPy supports it

        for event in self.window.get_events():
            if event == windowevent.QUIT:
                done = True
            elif event == windowevent.RELEASESPEEDUP:
                self.limit_emulationspeed ^= True
                logger.info("Speed limit: %s" % self.limit_emulationspeed)
            elif event == windowevent.SAVESTATE:
                self.motherboard.save_state(self.ROM + ".state")
            elif event == windowevent.LOADSTATE:
                self.motherboard.load_state(self.ROM + ".state")
            elif event == windowevent.DEBUGTOGGLE:
                self.debugger.running ^= True
            elif event == windowevent.PASS:
                pass  # Used in place of None in Cython, when key isn't mapped to anything
            elif event == windowevent.SCREENRECORDINGTOGGLE:
                if not self.screen_recorder:
                    self.screen_recorder = ScreenRecorder(self.getScreenBufferFormat())
                else:
                    self.screen_recorder.save()
                    self.screen_recorder = None
            else:  # Right now, everything else is a button press
                self.motherboard.buttonevent(event)

        self.motherboard.tickframe()
        self.window.update_display()

        if self.screen_recorder:
            self.screen_recorder.add_frame(self.getscreenbuffer())

        t_cpu = time.perf_counter()

        if self.limit_emulationspeed:
            self.window.frame_limiter(1)
        elif self.max_emulationspeed > 0:
            self.window.frame_limiter(self.max_emulationspeed)

        t_emu = time.perf_counter()

        secs = t_emu-t_start
        self.avg_emu = 0.9 * self.avg_emu + 0.1 * secs

        secs = t_cpu-t_start
        self.avg_cpu = 0.9 * self.avg_cpu + 0.1 * secs

        if self.counter % 60 == 0:
            text = ("CPU/frame: %0.2f%% Emulation: x%d"
                    % (self.avg_cpu/SPF*100, round(SPF/self.avg_emu)))
            self.window.set_title(text)
            self.counter = 0
        self.counter += 1

        return done

    def stop(self, save=True):
        logger.info("###########################")
        logger.info("# Emulator is turning off #")
        logger.info("###########################")
        self.motherboard.stop(save)

        if self.profiling:
            print("Profiling report:")
            from operator import itemgetter
            names = [CPU_COMMANDS[n] if n < 0x100 else CPU_COMMANDS_EXT[n-0x100]
                     for n in range(0x200)]
            for hits, n, name in sorted(filter(
                    itemgetter(0), zip(self.motherboard.cpu.hitRate,
                                       range(0x200), names)), reverse=True):
                print("%3x %16s %s" % (n, name, hits))

    ###################################################################
    # Scripts and bot methods
    #
    def getscreenbuffer(self):
        return self.window.getscreenbuffer()

    def getScreenBufferFormat(self):
        return self.motherboard.window.colorformat

    def getMemoryValue(self, addr):
        return self.motherboard.getitem(addr)

    def setMemoryValue(self, addr, value):
        self.motherboard.setitem(addr, value)

    def sendInput(self, event):
        self.motherboard.buttonEvent(event)

    def getMotherBoard(self):
        return self.motherboard

    def getSprite(self, index):
        return botsupport.Sprite(self.motherboard, index)

    def getTileView(self, high):
        return botsupport.TileView(self.motherboard, high)

    def getScreenPosition(self):
        return (self.motherboard.getitem(0xFF43), self.motherboard.getitem(0xFF42))

    def saveState(self, filename):
        self.motherboard.save_state(filename)

    def loadState(self, filename):
        self.motherboard.load_state(filename)

    def getSerial(self):
        return self.motherboard.getserial()

    def disableTitle(self):
        self.window.disable_title()

    def set_emulation_speed(self, v, max_speed=0):
        self.emulationspeed = v
        if max_speed > 5:
            logger.warning("The emulation speed might not be accurate when higher than 5")
        self.max_emulationspeed = max_speed
