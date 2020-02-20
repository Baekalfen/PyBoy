#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""
The core module of the emulator
"""

import os
import time

from pyboy.plugins.manager import PluginManager

from . import botsupport, windowevent
from .core.mb import Motherboard
from .logger import addconsolehandler, logger
from .utils import IntIOWrapper

addconsolehandler()

SPF = 1/60. # inverse FPS (frame-per-second)

defaults = {
    "color_palette": (0xFFFFFF, 0x999999, 0x555555, 0x000000),
    "scale": 3,
    "window_type": "SDL2",
}


class PyBoy:
    def __init__(
                self,
                gamerom_file, *,
                bootrom_file=None,
                profiling=False,
                disable_renderer=False,
                **kwargs
            ):
        """
        PyBoy is loadable as an object in Python. This means, it can be initialized from another script, and be
        controlled and probed by the script. It is supported to spawn multiple emulators, just instantiate the class
        multiple times.

        This object, `pyboy.windowevent`, and the `pyboy.botsupport` module, are the only official user-facing
        interfaces. All other parts of the emulator, are subject to change.

        A range of methods are exposed, which should allow for complete control of the emulator. Please open an issue on
        GitHub, if other methods are needed for your projects. Take a look at `interface_example.py` or `tetris_bot.py`
        for a crude "bot", which interacts with the game.

        Only the `gamerom_file` argument is required.

        Args:
            gamerom_file (str): Filepath to a game-ROM for the original Game Boy.

        Kwargs:
            bootrom_file (str): Filepath to a boot-ROM to use. If unsure, specify `None`.
            profiling (bool): Profile the emulator and report opcode usage (internal use).
            disable_renderer (bool): Can be used to optimize performance, by internally disable rendering of the screen.
            color_palette (tuple): Specify the color palette to use for rendering.
        """

        for k, v in defaults.items():
            if k not in kwargs:
                kwargs[k] = kwargs.get(k, defaults[k])

        if not os.path.isfile(gamerom_file):
            raise FileNotFoundError(f"ROM file {gamerom_file} was not found!")
        self.gamerom_file = gamerom_file

        self.mb = Motherboard(
            gamerom_file,
            bootrom_file,
            kwargs["color_palette"],
            disable_renderer,
            profiling=profiling
        )

        # Performance measures
        self.avg_pre = 0
        self.avg_tick = 0
        self.avg_post = 0

        # Absolute frame count of the emulation
        self.frame_count = 0

        self.set_emulation_speed(1)
        self.paused = False
        # self.autopause = autopause
        self.events = []
        self.done = False
        self.window_title = "PyBoy"
        self.window_title_disabled = False

        ###################
        # Plugins

        self.plugin_manager = PluginManager(self, kwargs)

    def tick(self):
        """
        Progresses the emulator ahead by one frame.

        To run the emulator in real-time, this will need to be called 60 times a second (for example in a while-loop).
        This function will block for roughly 16,67ms at a time, to not run faster than real-time, unless you specify
        otherwise with the `PyBoy.set_emulation_speed` method.

        _Open an issue on GitHub if you need finer control, and we will take a look at it._
        """

        t_start = time.perf_counter() # Change to _ns when PyPy supports it
        self._handle_events(self.events)
        t_pre = time.perf_counter()
        self.frame_count += 1
        if not self.paused:
            self.mb.tickframe()
        t_tick = time.perf_counter()
        self._post_tick()
        t_post = time.perf_counter()

        secs = t_pre-t_start
        self.avg_pre = 0.9 * self.avg_pre + 0.1 * secs

        secs = t_tick-t_pre
        self.avg_tick = 0.9 * self.avg_tick + 0.1 * secs

        secs = t_post-t_tick
        self.avg_post = 0.9 * self.avg_post + 0.1 * secs

        return self.done

    def _handle_events(self, events):
        # This feeds events into the tick-loop from the window. There might already be events in the list from the API.
        events = self.plugin_manager.handle_events(events)

        for event in events:
            if event == windowevent.QUIT:
                self.done = True
            elif event == windowevent.RELEASE_SPEED_UP:
                # Switch between unlimited and 1x real-time emulation speed
                self.target_emulationspeed = int(bool(self.target_emulationspeed) ^ True)
                logger.info("Speed limit: %s" % self.target_emulationspeed)
            elif event == windowevent.SAVE_STATE:
                with open(self.gamerom_file + ".state", "wb") as f:
                    self.mb.save_state(IntIOWrapper(f))
            elif event == windowevent.LOAD_STATE:
                with open(self.gamerom_file + ".state", "rb") as f:
                    self.mb.load_state(IntIOWrapper(f))
            elif event == windowevent.DEBUG_TOGGLE:
                # self.debugger.running ^= True
                pass
            elif event == windowevent.PASS:
                pass # Used in place of None in Cython, when key isn't mapped to anything
            elif event == windowevent.PAUSE_TOGGLE:
                if self.paused:
                    self.unpause()
                else:
                    self.pause()
            elif event == windowevent.PAUSE:
                self.pause()
            elif event == windowevent.UNPAUSE:
                self.unpause()
            elif event == windowevent.INTERNAL_RENDERER_FLUSH:
                self.mb.renderer.render_screen(self.mb.lcd)
                self.plugin_manager._post_tick_windows()
            else:
                self.mb.buttonevent(event)

    def pause(self):
        if self.paused:
            return
        self.paused = True
        self.save_target_emulationspeed = self.target_emulationspeed
        self.target_emulationspeed = 1
        logger.info("Emulation paused!")

    def unpause(self):
        if not self.paused:
            return
        self.paused = False
        self.target_emulationspeed = self.save_target_emulationspeed
        logger.info("Emulation unpaused!")

    def _post_tick(self):
        if not self.window_title_disabled and self.frame_count % 60 == 0:
            self._update_window_title()
        self.plugin_manager.post_tick()
        self.plugin_manager.frame_limiter(self.target_emulationspeed)

        # Prepare an empty list, as the API might be used to send in events between ticks
        self.events = []

    def _update_window_title(self):
        avg_emu = self.avg_pre + self.avg_tick + self.avg_post
        self.window_title = "CPU/frame: %0.2f%%" % ((self.avg_pre + self.avg_tick)/SPF*100)
        self.window_title += "Emulation: x%d" % (round(SPF/avg_emu) if avg_emu != 0 else 0)
        if self.paused:
            self.window_title += " [PAUSED]"
        self.window_title += self.plugin_manager.window_title()

    def __del__(self):
        self.stop(save=False)

    def stop(self, save=True):
        """
        Gently stops the emulator and all sub-modules.

        Args:
            save (bool): Specify whether to save the game upon stopping. It will always be saved in a file next to the
                provided game-ROM.
        """
        logger.info("###########################")
        logger.info("# Emulator is turning off #")
        logger.info("###########################")
        self.plugin_manager.stop()
        self.mb.stop(save)

    def _get_cpu_hitrate(self):
        logger.warning("You are calling an internal function. The output and the function is subject to change.")
        return self.mb.cpu.hitrate

    ###################################################################
    # Scripts and bot methods
    #

    def get_raw_screen_buffer(self):
        """
        Provides a raw, unfiltered `bytes` object with the data from the screen. Check
        `PyBoy.get_raw_screen_buffer_format` to see which dataformat is used. The returned type and dataformat are
        subject to change.

        Use this, only if you need to bypass the overhead of `PyBoy.get_screen_image` or `PyBoy.get_screen_ndarray`.

        Returns:
            bytes: 92160 bytes of screen data in a `bytes` object.
        """
        return self.mb.renderer.get_screen_buffer()

    def get_raw_screen_buffer_dims(self):
        """
        Returns the dimensions of the raw screen buffer.

        Returns:
            tuple: A two-tuple of the buffer dimensions. E.g. (160, 144).
        """
        return self.mb.renderer.buffer_dims

    def get_raw_screen_buffer_format(self):
        """
        Returns the color format of the raw screen buffer.

        Returns:
            str: Color format of the raw screen buffer. E.g. 'RGB'.
        """
        return self.mb.renderer.color_format

    def get_screen_ndarray(self):
        """
        Provides the screen data in NumPy format. The dataformat is always RGB.

        Returns:
            numpy.ndarray: Screendata in `ndarray` of bytes with shape (160, 144, 3)
        """
        return self.mb.renderer.get_screen_buffer_as_ndarray()

    def get_screen_image(self):
        """
        Generates a PIL Image from the screen buffer.

        Convenient for screen captures, but might be a bottleneck, if you use it to train a neural network. In which
        case, read up on the `pyboy.botsupport` features, [Pan Docs](http://bgb.bircd.org/pandocs.htm) on tiles/sprites,
        and join our Discord channel for more help.

        Returns:
            PIL.Image: RGB image of (160, 144) pixels
        """
        return self.mb.renderer.get_screen_image()

    def get_memory_value(self, addr):
        """
        Reads a given memory address of the Game Boy's current memory state. This will not directly give you access to
        all switchable memory banks. Open an issue on GitHub if that is needed, or use `PyBoy.set_memory_value` to send
        MBC commands to the virtual cartridge.

        Returns:
            int: An integer with the value of the memory address
        """
        return self.mb.getitem(addr)

    def set_memory_value(self, addr, value):
        """
        Write one byte to a given memory address of the Game Boy's current memory state.

        This will not directly give you access to all switchable memory banks. Open an issue on GitHub if that is
        needed, or use this function to send "Memory Bank Controller" (MBC) commands to the virtual cartridge. You can
        read about the MBC at [Pan Docs](http://bgb.bircd.org/pandocs.htm).

        Args:
            addr (int): Address to write the byte
            value (int): A byte of data
        """
        self.mb.setitem(addr, value)

    def send_input(self, event):
        """
        Send a single input to control the emulator. This is both Game Boy buttons and emulator controls.

        See `pyboy.windowevent` for which events to send.

        Args:
            event (pyboy.windowevent): The event to send
        """
        self.events.append(event)

    def get_sprite(self, index):
        """
        Provides a `pyboy.botsupport.sprite.Sprite` object, which makes the OAM data more presentable. The given index
        corresponds to index of the sprite in the "Object Attribute Memory" (OAM).

        The Game Boy supports 40 sprites in total. Read more details about it, in the [Pan
        Docs](http://bgb.bircd.org/pandocs.htm).

        Args:
            index (int): Sprite index from 0 to 39.
        Returns:
            `pyboy.botsupport.sprite.Sprite`: Sprite corresponding to the given index.
        """
        return botsupport.Sprite(self.mb, index)

    def get_tile(self, identifier):
        """
        The Game Boy can have 384 tiles loaded in memory at once. Use this method to get a
        `pyboy.botsupport.tile.Tile`-object for given identifier.

        The `pyboy.botsupport.tile.Tile.identifier` should not be confused with the `pyboy.botsupport.tile.Tile.index`.
        The identifier is a PyBoy construct, which unifies two different scopes of indexes in the Game Boy hardware. See
        the `pyboy.botsupport.tile.Tile` object for more information.

        Returns:
            `pyboy.botsupport.tile.Tile`: A Tile object for the given identifier.
        """
        return botsupport.Tile(self.mb, identifier=identifier)

    def get_background_tile_map(self):
        """
        The Game Boy uses two tile maps at the same time to draw graphics on the screen. This method will provide one
        for the background tiles.

        Read more details about it, in the [Pan Docs](http://bgb.bircd.org/pandocs.htm#vrambackgroundmaps).

        Returns:
            `pyboy.botsupport.tilemap.TileMap`: A TileMap object for the background tile map.
        """
        return botsupport.TileMap(self.mb, window=False)

    def get_window_tile_map(self):
        """
        The Game Boy uses two tile maps at the same time to draw graphics on the screen. This method will provide one
        for the window tiles.

        Read more details about it, in the [Pan Docs](http://bgb.bircd.org/pandocs.htm#vrambackgroundmaps).

        Returns:
            `pyboy.botsupport.tilemap.TileMap`: A TileMap object for the window tile map.
        """
        return botsupport.TileMap(self.mb, window=True)

    # TODO: We actually need the scanline_parameters. Mario might always report (0,0) at the end of frame.
    def get_screen_position(self):
        """
        These coordinates define the offset in the tile map from where the top-left corner of the screen is place. Note
        that the tile map defines 256x256 pixels, but the screen can only show 160x144 pixels. When the offset is closer
        to the right or bottom edge than 160x144 pixels, the screen will wrap around and render from the opposite site
        of the tile map.

        For more details, see "7.4 Viewport" in the [report](https://github.com/Baekalfen/PyBoy/raw/master/PyBoy.pdf),
        or the Pan Docs under [LCD Position and Scrolling](http://bgb.bircd.org/pandocs.htm#lcdpositionandscrolling).

        Returns:
            ((int, int), (int, int)): Returns the registers (SCX, SCY), (WX - 7, WY)
        """
        return (self.mb.lcd.getviewport(), self.mb.lcd.getwindowpos())

    def save_state(self, file_like_object):
        """
        Saves the complete state of the emulator. It can be called at any time, and enable you to revert any progress in
        a game.

        You can either save it to a file, or in-memory. The following two examples will provide the file handle in each
        case. Remember to `seek` the in-memory buffer to the beginning before calling `PyBoy.load_state`:

            # Save to file
            file_like_object = open("state_file.state", "wb")

            # Save to memory
            import io
            file_like_object = io.BytesIO()
            file_like_object.seek(0)

        Args:
            file_like_object (io.BufferedIOBase): A file-like object for which to write the emulator state.
        """

        if isinstance(file_like_object, str):
            raise Exception("String not allowed. Did you specify a filepath instead of a file-like object?")

        self.mb.save_state(IntIOWrapper(file_like_object))

    def load_state(self, file_like_object):
        """
        Restores the complete state of the emulator. It can be called at any time, and enable you to revert any progress
        in a game.

        You can either load it from a file, or from memory. See `PyBoy.save_state` for how to save the state, before you
        can load it here.

        To load a file, remember to load it as bytes:

            # Load file
            file_like_object = open("state_file.state", "rb")


        Args:
            file_like_object (io.BufferedIOBase): A file-like object for which to read the emulator state.
        """

        if isinstance(file_like_object, str):
            raise Exception("String not allowed. Did you specify a filepath instead of a file-like object?")

        self.mb.load_state(IntIOWrapper(file_like_object))

    def get_serial(self):
        """
        Provides all data that has been sent over the serial port since last call to this function.

        Returns:
            str : Buffer data
        """
        return self.mb.getserial()

    def disable_title(self):
        """
        Disable window title updates. These are output to the log, when in `headless` or `dummy` mode.
        """
        self.window_title_disabled = True

    def set_emulation_speed(self, target_speed):
        """
        Set the target emulation speed. It might loose accuracy of keeping the exact speed, when using a high
        `target_speed`.

        The speed is defined as a multiple of real-time. I.e `target_speed=2` is double speed.

        A `target_speed` of `0` means unlimited. I.e. fastest possible execution.

        Args:
            target_speed (int): Target emulation speed as multiplier of real-time.
        """
        if target_speed > 5:
            logger.warning("The emulation speed might not be accurate when speed-target is higher than 5")
        self.target_emulationspeed = target_speed

    def get_cartridge_title(self):
        """
        Get the title stored on the currently loaded cartridge ROM. The title is all upper-case ASCII and may
        have been truncated to 11 characters.

        Returns:
            str : Game name
        """
        return self.mb.cartridge.gamename
