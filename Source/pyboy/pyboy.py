#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""
The core module of the emulator
"""

import time
import json
import numpy as np

import io
import base64
import zlib

from . import botsupport
from .screenrecorder import ScreenRecorder
from .mb.mb import Motherboard
from . import windowevent
from . import window

from .opcode_to_name import CPU_COMMANDS, CPU_COMMANDS_EXT
from .logger import logger, addconsolehandler
addconsolehandler()

SPF = 1/60. # inverse FPS (frame-per-second)


class PyBoy:
    def __init__(
            self,
            gamerom_file, *,
            window_type = None,
            window_scale = 3,
            bootrom_file = None,
            autopause = False,
            loadstate_file = None,
            debugging = False,
            profiling = False,
            record_input_file = None,
        ):
        """
        PyBoy is loadable as an object in Python. This means, it can be initialized from another script, and be controlled and probed by the script. It is supported to spawn multiple emulators, just instantiate the class multiple times.

        This object, `pyboy.windowevent`, and the `pyboy.botsupport` module, are the only official user-facing interfaces. All other parts of the emulator, are subject to change.

        A range of methods are exposed, which should allow for complete control of the emulator. Please open an issue on GitHub, if other methods are needed for your projects. Take a look at `interface_example.px` or `tetris_bot.py` for a crude "bot", which interacts with the game.

        Only the `gamerom_file` argument is required.

        Args:
            gamerom_file (str): Filepath to a game-ROM for the original Game Boy.
            window_type (str): Specify one of the supported window types. If unsure, specify `None` to get the default.
            window_scale (int): Multiplier for the native resolution. This scales the host window by the given amount.
            bootrom_file (str): Filepath to a boot-ROM to use. If unsure, specify `None`.
            autopause (bool): Wheter or not the emulator should pause, when the host window looses focus.
            loadstate_file (str): Filepath to a saved state to be loaded at startup.
            debugging (bool): Whether or not to enable some extended debugging features.
            profiling (bool): This will profile the emulator, and report which opcodes are being used the most.
            record_input_file (str): Filepath to save all recorded input for replay later.
        """
        self.gamerom_file = gamerom_file

        self.window = window.window.getwindow(window_type, window_scale, debugging)
        self.mb = Motherboard(gamerom_file, bootrom_file, self.window, profiling=profiling)

        # TODO: Get rid of this extra step
        if debugging:
            self.window.set_lcd(self.mb.lcd)

        if loadstate_file:
            self.mb.load_state(loadstate_file)

        self.avg_emu = 0
        self.avg_cpu = 0
        self.counter = 0
        self.set_emulation_speed(True, 0)
        self.screen_recorder = None
        self.paused = False
        self.autopause = autopause
        self.record_input = bool(record_input_file)
        if self.record_input:
            logger.info("Recording event inputs")
        self.frame_count = 0
        self.record_input_file = record_input_file
        self.recorded_input = []
        self.external_input = []
        self.profiling = profiling

    def tick(self):
        """
        Progresses the emulator ahead by one frame.

        To run the emulator in real-time, this will need to be called 60 times a second (for example in a while-loop).
        This function will block for roughly 16,67ms at a time, to not run faster than real-time, unless you specify otherwise with
        the `PyBoy.set_emulation_speed` method.

        _Open an issue on GitHub if you need finer control, and we will take a look at it._
        """
        done = False
        t_start = time.perf_counter() # Change to _ns when PyPy supports it

        events = self.window.get_events()

        if self.record_input and len(events) != 0:
            self.recorded_input.append((self.frame_count, events, base64.b64encode(np.ascontiguousarray(self.get_screen_ndarray())).decode('utf8')))
        self.frame_count += 1

        events += self.external_input
        self.external_input = []

        for event in events:
            if event == windowevent.QUIT:
                done = True
            elif event == windowevent.RELEASE_SPEED_UP:
                self.limit_emulationspeed ^= True
                logger.info("Speed limit: %s" % self.limit_emulationspeed)
            elif event == windowevent.SAVE_STATE:
                with open(self.gamerom_file + ".state", "wb") as f:
                    self.mb.save_state(f)
            elif event == windowevent.LOAD_STATE:
                with open(self.gamerom_file + ".state", "rb") as f:
                    self.mb.load_state(f)
            elif event == windowevent.DEBUG_TOGGLE:
                # self.debugger.running ^= True
                pass
            elif event == windowevent.PASS:
                pass # Used in place of None in Cython, when key isn't mapped to anything
            elif event == windowevent.PAUSE and self.autopause:
                self.paused = True
                logger.info("Emulation paused!")
            elif event == windowevent.UNPAUSE and self.autopause:
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
                    self.screen_recorder = ScreenRecorder()
                else:
                    self.screen_recorder.save()
                    self.screen_recorder = None
            else: # Right now, everything else is a button press
                self.mb.buttonevent(event)

        # self.paused &= self.autopause # Overrules paused state, if not allowed
        if not self.paused:
            self.mb.tickframe()
        self.window.update_display(self.paused)
        t_cpu = time.perf_counter()

        if self.screen_recorder:
            self.screen_recorder.add_frame(self.get_screen_image())

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
        """
        Gently stops the emulator and all sub-modules.

        Args:
            save (str): Specify whether to save the game upon stopping. It will always be saved in a file next to the provided game-ROM.
        """
        logger.info("###########################")
        logger.info("# Emulator is turning off #")
        logger.info("###########################")
        self.mb.stop(save)

        if self.profiling:
            print("Profiling report:")
            from operator import itemgetter
            names = [CPU_COMMANDS[n] if n < 0x100 else CPU_COMMANDS_EXT[n-0x100] for n in range(0x200)]
            for hits, n, name in sorted(
                    filter(itemgetter(0), zip(self.mb.cpu.hitRate, range(0x200), names)), reverse=True):
                print("%3x %16s %s" % (n, name, hits))

        if self.record_input:
            with open(self.record_input_file, 'wb') as f:
                recorded_data = io.StringIO() # json.dump writes 'str' not bytes...
                json.dump(self.recorded_input, recorded_data)
                f.write(zlib.compress(recorded_data.getvalue().encode('ascii')))


    ###################################################################
    # Scripts and bot methods
    #

    def get_raw_screen_buffer(self):
        """
        Provides a raw, unfiltered `bytes` object with the data from the screen. Check `PyBoy.get_raw_screen_buffer_format` to see which dataformat is used. The returned type and dataformat are subject to change.

        Use this, only if you need to bypass the overhead of `PyBoy.get_screen_image` or `PyBoy.get_screen_ndarray`.

        Returns:
            bytes: 92160 bytes of screen data in a `bytes` object.
        """
        return self.window.get_screen_buffer()

    def get_raw_screen_buffer_dims(self):
        """
        Returns the dimensions of the raw screen buffer.

        Returns:
            numpy.ndarray: Screendata in `ndarray` of bytes with shape (160, 144, 3)
        """
        return self.mb.window.buffer_dims

    def get_raw_screen_buffer_format(self):
        """
        Returns the format of the raw screen buffer.

        Returns:
            str: Color format of the raw screen buffer. E.g. 'RGB'.
        """
        return self.mb.window.color_format

    def get_screen_ndarray(self):
        """
        Provides the screen data in NumPy format. The dataformat is always RGB.

        Returns:
            numpy.ndarray: Screendata in `ndarray` of bytes with shape (160, 144, 3)
        """
        return self.window.get_screen_buffer_as_nparray()

    def get_screen_image(self):
        """
        Generates a PIL Image from the screen buffer.

        Convenient for screen captures, but might be a bottleneck, if you use it to train a neural network. In that case, read up on the `pyboy.botsupport` features, [Pan Docs](http://bgb.bircd.org/pandocs.htm) on tiles/sprites, and join our Discord channel for more help.

        Returns:
            PIL.Image: Screendata in `ndarray` of bytes with shape (160, 144, 3)
        """
        return self.mb.window.get_screen_image()

    def get_memory_value(self, addr):
        """
        Reads a given memory address of the Game Boy's current memory state. This will not directly give you access to all switchable memory banks. Open an issue on GitHub if that is needed, or use `PyBoy.set_memory_value` to send MBC commands to the virtual cartridge.

        Returns:
            int: An integer with the value of the memory address
        """
        return self.mb.getitem(addr)

    def set_memory_value(self, addr, value):
        """
        Write one byte to a given memory address of the Game Boy's current memory state. This will not directly give you access to all switchable memory banks. Open an issue on GitHub if that is needed, or use this function to send "Memory Bank Controller" (MBC) commands to the virtual cartridge. You can read about the MBC at [Pan Docs](http://bgb.bircd.org/pandocs.htm).

        Args:
            addr (int): Address to write to
            value (int): A byte to write
        """
        self.mb.setitem(addr, value)

    def send_input(self, event):
        """
        Send a single input to control the emulator. This is both Game Boy buttons and emulator controls.

        Args:
            event (pyboy.windowevent): The event to send
        """
        # self.mb.buttonevent(event)
        self.external_input.append(event)

    def get_sprite(self, index):
        """
        Provides a `pyboy.botsupport.sprite` object, which makes the OAM data more presentable. The given index corresponds to index of the sprite in the "Object Attribute Memory" (OAM).

        The Game Boy supports 40 sprites in total. Read more details about it, in the [Pan Docs](http://bgb.bircd.org/pandocs.htm).

        Args:
            index (int): Sprite index from 0 to 39.
        Returns:
            `pyboy.botsupport.sprite`: Sprite corresponding to the given index.
        """
        return botsupport.Sprite(self.mb, index)

    def get_background_tile_map(self):
        """
        The Game Boy uses two tile maps at the same time to draw graphics on the screen. Read more details about it, in the [Pan Docs](http://bgb.bircd.org/pandocs.htm).

        Returns:
            `pyboy.botsupport.tilemap`: A TileMap object for the background tile map.
        """
        return botsupport.TileMap(self.mb, window=False)

    def get_window_tile_map(self):
        """
        The Game Boy uses two tile maps at the same time to draw graphics on the screen. Read more details about it, in the [Pan Docs](http://bgb.bircd.org/pandocs.htm).

        Returns:
            `pyboy.botsupport.tilemap`: A TileMap object for the window tile map.
        """
        return botsupport.TileMap(self.mb, window=True)

    def get_screen_position(self):
        """
        These coordinates define the offset in the tile map from where the top-left corner of the screen is place. Note that the tile map defines 256x256 pixels, but the screen can only show 160x144 pixels. When the offset is closer to the right or bottom edge than 160x144 pixels, the screen will wrap around and render from the opposite site of the tile map.

        For more details, see "7.4 Viewport" in the [report](https://github.com/Baekalfen/PyBoy/raw/master/PyBoy.pdf), or the Pan Docs under [LCD Position and Scrolling](http://bgb.bircd.org/pandocs.htm#lcdpositionandscrolling).

        Returns:
            ((int, int), (int, int)): Returns the registers (SCX, SCY), (WX - 7, WY)
        """
        return (self.mb.lcd.getviewport(), self.mb.lcd.getwindowpos())

    def save_state(self, file_handle):
        """
        Saves the complete state of the emulator. It can be called at any time, and enable you to revert any progress in a game.

        You can either save it to a file, or in-memory. The following two examples will provide the file handle in each case. Remember to `seek` the in-memory buffer to the beginning before calling `PyBoy.load_state`:

            # Save to file
            file_handle = open("state_file.state", "wb")

            # Save to memory
            import io
            file_handle = io.BytesIO()
            file_handle.seek(0)

        Args:
            file_handle (io.BufferedIOBase): A file-like object for which to write the emulator state.
        """
        self.mb.save_state(file_handle)

    def load_state(self, file_like_object):
        """
        Restores the complete state of the emulator. It can be called at any time, and enable you to revert any progress in a game.

        You can either load it from a file, or from memory. See `PyBoy.save_state` for how to save the state, before you can load it here.

        Args:
            file_handle (io.BufferedIOBase): A file-like object for which to read the emulator state.
        """
        self.mb.load_state(file_like_object)

    def get_serial(self):
        """
        Provides all data that has been sent over the serial port since last call to this function.

        Returns:
            str : Buffer data
        """
        return self.mb.getserial()

    def disable_title(self):
        """
        Disable window-title updates. These are output to the log, when in `headless` or `dummy` mode.
        """
        self.window.disable_title()

    def set_autopause(self, autopause):
        """
        PyBoy can automatically pause execution, when the game window looses focus. This might not be convenient, when running the emulator autonomously.

        Args:
            autopause (bool): Allow to autopause or not.
        """
        self.autopause = autopause

    def set_emulation_speed(self, limit, target_speed=0):
        """
        Set the target emulation speed. It might loose accuracy of keeping the exact speed, when using a high `target_speed`.

        Args:
            limit (bool): Whether to limit the speed or not.
            target_speed (bool): If limiting the speed, what is the target speed.
        """
        self.limit_emulationspeed = limit
        if target_speed > 5:
            logger.warning("The emulation speed might not be accurate when speed-target is higher than 5")
        self.max_emulationspeed = target_speed

