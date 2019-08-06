#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys
import time

from . import botsupport
from .screenrecorder import ScreenRecorder
from .mb.mb import Motherboard
from . import windowevent
from . import window

from .opcode_to_name import CPU_COMMANDS, CPU_COMMANDS_EXT
from .logger import logger, addconsolehandler
addconsolehandler()

if "--no-logger" in sys.argv:
    logger.disabled = True

argv_debug = "--debug" in sys.argv
argv_profiling = "--profiling" in sys.argv
argv_loadstate = "--loadstate" in sys.argv


SPF = 1/60. # inverse FPS (frame-per-second)


class PyBoy:
    def __init__(self, win_type, scale, gamerom_file, bootrom_file=None):
        self.gamerom_file = gamerom_file

        self.window = window.window.getwindow(win_type, scale, argv_debug)

        self.mb = Motherboard(gamerom_file, bootrom_file, self.window, profiling=argv_profiling)

        # TODO: Get rid of this extra step
        if argv_debug:
            self.window.set_lcd(self.mb.lcd)

        if argv_loadstate:
            self.mb.load_state(gamerom_file + ".state")

        self.avg_emu = 0
        self.avg_cpu = 0
        self.counter = 0
        self.set_emulation_speed(True, 0)
        self.limit_emulationspeed = True
        self.screen_recorder = None
        self.paused = False

    def tick(self):
        done = False
        t_start = time.perf_counter() # Change to _ns when PyPy supports it

        for event in self.window.get_events():
            if event == windowevent.QUIT:
                done = True
            elif event == windowevent.RELEASE_SPEED_UP:
                self.limit_emulationspeed ^= True
                logger.info("Speed limit: %s" % self.limit_emulationspeed)
            elif event == windowevent.SAVE_STATE:
                self.mb.save_state(self.gamerom_file + ".state")
            elif event == windowevent.LOAD_STATE:
                self.mb.load_state(self.gamerom_file + ".state")
            elif event == windowevent.DEBUG_TOGGLE:
                # self.debugger.running ^= True
                pass
            elif event == windowevent.PASS:
                pass # Used in place of None in Cython, when key isn't mapped to anything
            elif event == windowevent.PAUSE:
                self.paused = True
                logger.info("Emulation paused!")
            elif event == windowevent.UNPAUSE:
                self.paused = False
                logger.info("Emulation unpaused!")
            elif event == windowevent.PAUSE_TOGGLE:
                self.paused ^= True
                if self.paused:
                    logger.info("Emulation paused!")
                else:
                    logger.info("Emulation unpaused!")
            elif event == windowevent.SCREEN_RECORDING_TOGGLE:
                if not self.screen_recorder:
                    self.screen_recorder = ScreenRecorder(self.getScreenBufferFormat())
                else:
                    self.screen_recorder.save()
                    self.screen_recorder = None
            else: # Right now, everything else is a button press
                self.mb.buttonevent(event)

        if not self.paused:
            self.mb.tickframe()
        self.window.update_display(self.paused)
        t_cpu = time.perf_counter()

        if self.screen_recorder:
            self.screen_recorder.add_frame(self.get_screen_buffer())

        if self.paused or self.limit_emulationspeed:
            self.window.frame_limiter(1)
        elif self.max_emulationspeed > 0:
            self.window.frame_limiter(self.max_emulationspeed)

        t_emu = time.perf_counter()

        secs = t_emu-t_start
        self.avg_emu = 0.9 * self.avg_emu + 0.1 * secs

        secs = t_cpu-t_start
        self.avg_cpu = 0.9 * self.avg_cpu + 0.1 * secs

        if self.counter % 60 == 0:
            text = ("CPU/frame: %0.2f%% Emulation: x%d" % (self.avg_cpu/SPF*100, round(SPF/self.avg_emu)))
            self.window.set_title(text)
            self.counter = 0
        self.counter += 1

        return done

    def stop(self, save=True):
        logger.info("###########################")
        logger.info("# Emulator is turning off #")
        logger.info("###########################")
        self.mb.stop(save)

        if argv_profiling:
            print("Profiling report:")
            from operator import itemgetter
            names = [CPU_COMMANDS[n] if n < 0x100 else CPU_COMMANDS_EXT[n-0x100] for n in range(0x200)]
            for hits, n, name in sorted(
                    filter(itemgetter(0), zip(self.mb.cpu.hitRate, range(0x200), names)), reverse=True):
                print("%3x %16s %s" % (n, name, hits))

    ###################################################################
    # Scripts and bot methods
    #

    def get_raw_screen_buffer(self):
        return self.window.get_screen_buffer()

    def get_raw_screen_buffer_as_nparray(self):
        return self.window.get_screen_buffer_as_nparray()

    def get_raw_screen_buffer_dims(self):
        return self.mb.window.buffer_dims

    def get_raw_screen_buffer_format(self):
        return self.mb.window.color_format

    def get_screen_image(self):
        return self.mb.window.get_screen_image()

    def get_memory_value(self, addr):
        return self.mb.getitem(addr)

    def set_memory_value(self, addr, value):
        self.mb.setitem(addr, value)

    def send_input(self, event):
        self.mb.buttonevent(event)

    def get_tile(self, index):
        return botsupport.Tile(self.mb.lcd, index)

    def get_sprite(self, index):
        return botsupport.Sprite(self.mb.lcd, index)

    def get_tile_view(self, high):
        return botsupport.Tile_view(self.mb.lcd, high)

    def get_screen_position(self):
        return self.mb.lcd.getviewport()

    def save_state(self, filename):
        self.mb.save_state(filename)

    def load_state(self, filename):
        self.mb.load_state(filename)

    def get_serial(self):
        return self.mb.getserial()

    def disable_title(self):
        self.window.disable_title()

    def set_emulation_speed(self, v, max_speed=0):
        self.limit_emulationspeed = v
        if max_speed > 5:
            logger.warning("The emulation speed might not be accurate when higher than 5")
        self.max_emulationspeed = max_speed

