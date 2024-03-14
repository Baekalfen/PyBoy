#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
"""
The core module of the emulator
"""

import heapq
import os
import re
import time

import numpy as np

from pyboy.api.memory_scanner import MemoryScanner
from pyboy.api.screen import Screen
from pyboy.api.tilemap import TileMap
from pyboy.logging import get_logger
from pyboy.plugins.manager import PluginManager
from pyboy.utils import IntIOWrapper, WindowEvent

from .api import Sprite, Tile, constants
from .core.mb import Motherboard

logger = get_logger(__name__)

SPF = 1 / 60. # inverse FPS (frame-per-second)

defaults = {
    "color_palette": (0xFFFFFF, 0x999999, 0x555555, 0x000000),
    "cgb_color_palette": ((0xFFFFFF, 0x7BFF31, 0x0063C5, 0x000000), (0xFFFFFF, 0xFF8484, 0x943A3A, 0x000000),
                          (0xFFFFFF, 0xFF8484, 0x943A3A, 0x000000)),
    "scale": 3,
    "window_type": "SDL2",
}


class PyBoy:
    def __init__(
        self,
        gamerom_file,
        *,
        symbols_file=None,
        bootrom_file=None,
        sound=False,
        sound_emulated=False,
        cgb=None,
        randomize=False,
        **kwargs
    ):
        """
        PyBoy is loadable as an object in Python. This means, it can be initialized from another script, and be
        controlled and probed by the script. It is supported to spawn multiple emulators, just instantiate the class
        multiple times.

        A range of methods are exposed, which should allow for complete control of the emulator. Please open an issue on
        GitHub, if other methods are needed for your projects. Take a look at the files in `examples/` for a crude
        "bots", which interact with the game.

        Only the `gamerom_file` argument is required.

        Example:
        ```python
        >>> pyboy = PyBoy('game_rom.gb')
        >>> for _ in range(60): # Use 'while True:' for infinite
        ...     pyboy.tick()
        True...
        >>> pyboy.stop()

        ```

        Args:
            gamerom_file (str): Filepath to a game-ROM for Game Boy or Game Boy Color.

        Kwargs:
            * symbols_file (str): Filepath to a .sym file to use. If unsure, specify `None`.

            * bootrom_file (str): Filepath to a boot-ROM to use. If unsure, specify `None`.

            * sound (bool): Enable sound emulation and output

            * sound_emulated (bool): Enable sound emulation without any output. Used for compatibility.

            * color_palette (tuple): Specify the color palette to use for rendering.

            * cgb_color_palette (list of tuple): Specify the color palette to use for rendering in CGB-mode for non-color games.

        Other keyword arguments may exist for plugins that are not listed here. They can be viewed by running `pyboy --help` in the terminal.
        """

        self.initialized = False

        for k, v in defaults.items():
            if k not in kwargs:
                kwargs[k] = kwargs.get(k, defaults[k])

        if not os.path.isfile(gamerom_file):
            raise FileNotFoundError(f"ROM file {gamerom_file} was not found!")
        self.gamerom_file = gamerom_file

        self.rom_symbols = {}
        if symbols_file is not None:
            if not os.path.isfile(symbols_file):
                raise FileNotFoundError(f"Symbols file {symbols_file} was not found!")
        self.symbols_file = symbols_file
        self._load_symbols()

        self.mb = Motherboard(
            gamerom_file,
            bootrom_file or kwargs.get("bootrom"), # Our current way to provide cli arguments is broken
            kwargs["color_palette"],
            kwargs["cgb_color_palette"],
            sound,
            sound_emulated,
            cgb,
            randomize=randomize,
        )

        # Performance measures
        self.avg_pre = 0
        self.avg_tick = 0
        self.avg_post = 0

        # Absolute frame count of the emulation
        self.frame_count = 0

        self.set_emulation_speed(1)
        self.paused = False
        self.events = []
        self.queued_input = []
        self.quitting = False
        self.stopped = False
        self.window_title = "PyBoy"

        ###################
        # API attributes
        self.screen = Screen(self.mb)
        """
        Use this method to get a `pyboy.api.screen.Screen` object. This can be used to get the screen buffer in
        a variety of formats.

        It's also here you can find the screen position (SCX, SCY, WX, WY) for each scan line in the screen buffer. See
        `pyboy.api.screen.Screen.tilemap_position_list` for more information.

        Example:
        ```python
        >>> pyboy.screen.image.show()
        >>> pyboy.screen.ndarray.shape
        (144, 160, 4)
        >>> pyboy.screen.raw_buffer_format
        'RGBA'

        ```

        Returns
        -------
        `pyboy.api.screen.Screen`:
            A Screen object with helper functions for reading the screen buffer.
        """
        self.memory = PyBoyMemoryView(self.mb)
        """
        Provides a `pyboy.PyBoyMemoryView` object for reading and writing the memory space of the Game Boy.

        For a more comprehensive description, see the `pyboy.PyBoyMemoryView` class.

        Example:
        ```python
        >>> pyboy.memory[0x0000:0x0010] # Read 16 bytes from ROM bank 0
        [49, 254, 255, 33, 0, 128, 175, 34, 124, 254, 160, 32, 249, 6, 48, 33]
        >>> pyboy.memory[1, 0x2000] = 12 # Override address 0x2000 from ROM bank 1 with the value 12
        >>> pyboy.memory[0xC000] = 1 # Write to address 0xC000 with value 1
        ```

        """

        self.memory_scanner = MemoryScanner(self)
        """
        Provides a `pyboy.api.memory_scanner.MemoryScanner` object for locating addresses of interest in the memory space
        of the Game Boy. This might require some trial and error. Values can be represented in memory in surprising ways.

        _Open an issue on GitHub if you need finer control, and we will take a look at it._

        Example:
        ```python
        >>> current_score = 4 # You write current score in game
        >>> pyboy.memory_scanner.scan_memory(current_score, start_addr=0xC000, end_addr=0xDFFF)
        []
        >>> for _ in range(175):
        ...     pyboy.tick(1, True) # Progress the game to change score
        True...
        >>> current_score = 8 # You write the new score in game
        >>> from pyboy.api.memory_scanner import DynamicComparisonType
        >>> addresses = pyboy.memory_scanner.rescan_memory(current_score, DynamicComparisonType.MATCH)
        >>> print(addresses) # If repeated enough, only one address will remain
        []

        ```
        """

        self.tilemap_background = TileMap(self, self.mb, "BACKGROUND")
        """
        The Game Boy uses two tile maps at the same time to draw graphics on the screen. This method will provide one
        for the _background_ tiles. The game chooses whether it wants to use the low or the high tilemap.

        Read more details about it, in the [Pan Docs](https://gbdev.io/pandocs/Tile_Maps.html).

        Example:
        ```
        >>> pyboy.tilemap_background[8,8]
        1
        >>> pyboy.tilemap_background[7:12,8]
        [0, 1, 0, 1, 0]
        >>> pyboy.tilemap_background[7:12,8:11]
        [[0, 1, 0, 1, 0], [0, 2, 3, 4, 5], [0, 0, 6, 0, 0]]

        ```

        Returns
        -------
        `pyboy.api.tilemap.TileMap`:
            A TileMap object for the tile map.
        """

        self.tilemap_window = TileMap(self, self.mb, "WINDOW")
        """
        The Game Boy uses two tile maps at the same time to draw graphics on the screen. This method will provide one
        for the _window_ tiles. The game chooses whether it wants to use the low or the high tilemap.

        Read more details about it, in the [Pan Docs](https://gbdev.io/pandocs/Tile_Maps.html).

        Example:
        ```
        >>> pyboy.tilemap_window[8,8]
        1
        >>> pyboy.tilemap_window[7:12,8]
        [0, 1, 0, 1, 0]
        >>> pyboy.tilemap_window[7:12,8:11]
        [[0, 1, 0, 1, 0], [0, 2, 3, 4, 5], [0, 0, 6, 0, 0]]

        ```

        Returns
        -------
        `pyboy.api.tilemap.TileMap`:
            A TileMap object for the tile map.
        """

        self.cartridge_title = self.mb.cartridge.gamename
        """
        The title stored on the currently loaded cartridge ROM. The title is all upper-case ASCII and may
        have been truncated to 11 characters.

        Example:
        ```python
        >>> pyboy.cartridge_title # Title of PyBoy's default ROM
        'DEFAULT-ROM'

        ```

        Returns
        -------
        str :
            Game title
        """

        self._hooks = {}

        self._plugin_manager = PluginManager(self, self.mb, kwargs)
        """
        Returns
        -------
        `pyboy.plugins.manager.PluginManager`:
            Object for handling plugins in PyBoy
        """

        self.game_wrapper = self._plugin_manager.gamewrapper()
        """
        Provides an instance of a game-specific or generic wrapper. The game is detected by the cartridge's hard-coded
        game title (see `pyboy.PyBoy.cartridge_title`).

        If a game-specific wrapper is not found, a generic wrapper will be returned.

        To get more information, find the wrapper for your game in `pyboy.plugins`.

        Example:
        ```python
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.reset_game()

        ```

        Returns
        -------
        `pyboy.plugins.base_plugin.PyBoyGameWrapper`:
            A game-specific wrapper object.
        """

        self.initialized = True

    def _tick(self, render):
        if self.stopped:
            return False

        t_start = time.perf_counter_ns()
        self._handle_events(self.events)
        t_pre = time.perf_counter_ns()
        if not self.paused:
            self.__rendering(render)
            # Reenter mb.tick until we eventually get a clean exit without breakpoints
            while self.mb.tick():
                # Breakpoint reached
                # NOTE: Potentially reinject breakpoint that we have now stepped passed
                self.mb.breakpoint_reinject()

                # NOTE: PC has not been incremented when hitting breakpoint!
                breakpoint_index = self.mb.breakpoint_reached()
                if breakpoint_index != -1:
                    self.mb.breakpoint_remove(breakpoint_index)
                    self.mb.breakpoint_singlestep_latch = 0

                    if not self._handle_hooks():
                        self._plugin_manager.handle_breakpoint()
                else:
                    if self.mb.breakpoint_singlestep_latch:
                        if not self._handle_hooks():
                            self._plugin_manager.handle_breakpoint()
                    # Keep singlestepping on, if that's what we're doing
                    self.mb.breakpoint_singlestep = self.mb.breakpoint_singlestep_latch

            self.frame_count += 1
        t_tick = time.perf_counter_ns()
        self._post_tick()
        t_post = time.perf_counter_ns()

        nsecs = t_pre - t_start
        self.avg_pre = 0.9 * self.avg_pre + (0.1*nsecs/1_000_000_000)

        nsecs = t_tick - t_pre
        self.avg_tick = 0.9 * self.avg_tick + (0.1*nsecs/1_000_000_000)

        nsecs = t_post - t_tick
        self.avg_post = 0.9 * self.avg_post + (0.1*nsecs/1_000_000_000)

        return not self.quitting

    def tick(self, count=1, render=True):
        """
        Progresses the emulator ahead by `count` frame(s).

        To run the emulator in real-time, it will need to process 60 frames a second (for example in a while-loop).
        This function will block for roughly 16,67ms per frame, to not run faster than real-time, unless you specify
        otherwise with the `PyBoy.set_emulation_speed` method.

        If you need finer control than 1 frame, have a look at `PyBoy.hook_register` to inject code at a specific point
        in the game.

        Setting `render` to `True` will make PyBoy render the screen for *the last frame* of this tick. This can be seen
        as a type of "frameskipping" optimization.

        For AI training, it's adviced to use as high a count as practical, as it will otherwise reduce performance
        substantially. While setting `render` to `False`, you can still access the `PyBoy.game_area` to get a simpler
        representation of the game.

        If `render` was enabled, use `pyboy.api.screen.Screen` to get a NumPy buffer or raw memory buffer.

        Example:
        ```python
        >>> pyboy.tick() # Progress 1 frame with rendering
        True
        >>> pyboy.tick(1) # Progress 1 frame with rendering
        True
        >>> pyboy.tick(60, False) # Progress 60 frames *without* rendering
        True
        >>> pyboy.tick(60, True) # Progress 60 frames and render *only the last frame*
        True
        >>> for _ in range(60): # Progress 60 frames and render every frame
        ...     if not pyboy.tick(1, True):
        ...         break
        >>>
        ```

        Args:
            count (int): Number of ticks to process
            render (bool): Whether to render an image for this tick
        Returns
        -------
        (True or False):
            False if emulation has ended otherwise True
        """

        running = False
        while count != 0:
            _render = render and count == 1 # Only render on last tick to improve performance
            running = self._tick(_render)
            count -= 1
        return running

    def _handle_events(self, events):
        # This feeds events into the tick-loop from the window. There might already be events in the list from the API.
        events = self._plugin_manager.handle_events(events)
        for event in events:
            if event == WindowEvent.QUIT:
                self.quitting = True
            elif event == WindowEvent.RELEASE_SPEED_UP:
                # Switch between unlimited and 1x real-time emulation speed
                self.target_emulationspeed = int(bool(self.target_emulationspeed) ^ True)
                logger.debug("Speed limit: %d", self.target_emulationspeed)
            elif event == WindowEvent.STATE_SAVE:
                with open(self.gamerom_file + ".state", "wb") as f:
                    self.mb.save_state(IntIOWrapper(f))
            elif event == WindowEvent.STATE_LOAD:
                state_path = self.gamerom_file + ".state"
                if not os.path.isfile(state_path):
                    logger.error("State file not found: %s", state_path)
                    continue
                with open(state_path, "rb") as f:
                    self.mb.load_state(IntIOWrapper(f))
            elif event == WindowEvent.PASS:
                pass # Used in place of None in Cython, when key isn't mapped to anything
            elif event == WindowEvent.PAUSE_TOGGLE:
                if self.paused:
                    self._unpause()
                else:
                    self._pause()
            elif event == WindowEvent.PAUSE:
                self._pause()
            elif event == WindowEvent.UNPAUSE:
                self._unpause()
            elif event == WindowEvent._INTERNAL_RENDERER_FLUSH:
                self._plugin_manager._post_tick_windows()
            else:
                self.mb.buttonevent(event)

    def _pause(self):
        if self.paused:
            return
        self.paused = True
        self.save_target_emulationspeed = self.target_emulationspeed
        self.target_emulationspeed = 1
        logger.info("Emulation paused!")
        self._update_window_title()

    def _unpause(self):
        if not self.paused:
            return
        self.paused = False
        self.target_emulationspeed = self.save_target_emulationspeed
        logger.info("Emulation unpaused!")
        self._update_window_title()

    def _post_tick(self):
        # Fix buggy PIL. They will copy our image buffer and destroy the
        # reference on some user operations like .save().
        if not self.screen.image.readonly:
            self.screen._set_image()

        if self.frame_count % 60 == 0:
            self._update_window_title()
        self._plugin_manager.post_tick()
        self._plugin_manager.frame_limiter(self.target_emulationspeed)

        # Prepare an empty list, as the API might be used to send in events between ticks
        self.events = []
        while self.queued_input and self.frame_count == self.queued_input[0][0]:
            _, _event = heapq.heappop(self.queued_input)
            self.events.append(WindowEvent(_event))

    def _update_window_title(self):
        avg_emu = self.avg_pre + self.avg_tick + self.avg_post
        self.window_title = f"CPU/frame: {(self.avg_pre + self.avg_tick) / SPF * 100:0.2f}%"
        self.window_title += f' Emulation: x{(round(SPF / avg_emu) if avg_emu > 0 else "INF")}'
        if self.paused:
            self.window_title += "[PAUSED]"
        self.window_title += self._plugin_manager.window_title()
        self._plugin_manager._set_title()

    def __del__(self):
        self.stop(save=False)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def stop(self, save=True):
        """
        Gently stops the emulator and all sub-modules.

        Example:
        ```python
        >>> pyboy.stop() # Stop emulator and save game progress (cartridge RAM)
        >>> pyboy.stop(False) # Stop emulator and discard game progress (cartridge RAM)

        ```

        Args:
            save (bool): Specify whether to save the game upon stopping. It will always be saved in a file next to the
                provided game-ROM.
        """
        if self.initialized and not self.stopped:
            logger.info("###########################")
            logger.info("# Emulator is turning off #")
            logger.info("###########################")
            self._plugin_manager.stop()
            self.mb.stop(save)
            self.stopped = True

    ###################################################################
    # Scripts and bot methods
    #

    def button(self, input, delay=1):
        """
        Send input to PyBoy in the form of "a", "b", "start", "select", "left", "right", "up" and "down".

        The button will automatically be released at the following call to `PyBoy.tick`.

        Example:
        ```python
        >>> pyboy.button('a') # Press button 'a' and release after `pyboy.tick()`
        >>> pyboy.tick() # Button 'a' pressed
        True
        >>> pyboy.tick() # Button 'a' released
        True
        >>> pyboy.button('a', 3) # Press button 'a' and release after 3 `pyboy.tick()`
        >>> pyboy.tick() # Button 'a' pressed
        True
        >>> pyboy.tick() # Button 'a' still pressed
        True
        >>> pyboy.tick() # Button 'a' still pressed
        True
        >>> pyboy.tick() # Button 'a' released
        True
        ```

        Args:
            input (str): button to press
            delay (int, optional): Number of frames to delay the release. Defaults to 1
        """
        input = input.lower()
        if input == "left":
            self.send_input(WindowEvent.PRESS_ARROW_LEFT)
            heapq.heappush(self.queued_input, (self.frame_count + delay, WindowEvent.RELEASE_ARROW_LEFT))
        elif input == "right":
            self.send_input(WindowEvent.PRESS_ARROW_RIGHT)
            heapq.heappush(self.queued_input, (self.frame_count + delay, WindowEvent.RELEASE_ARROW_RIGHT))
        elif input == "up":
            self.send_input(WindowEvent.PRESS_ARROW_UP)
            heapq.heappush(self.queued_input, (self.frame_count + delay, WindowEvent.RELEASE_ARROW_UP))
        elif input == "down":
            self.send_input(WindowEvent.PRESS_ARROW_DOWN)
            heapq.heappush(self.queued_input, (self.frame_count + delay, WindowEvent.RELEASE_ARROW_DOWN))
        elif input == "a":
            self.send_input(WindowEvent.PRESS_BUTTON_A)
            heapq.heappush(self.queued_input, (self.frame_count + delay, WindowEvent.RELEASE_BUTTON_A))
        elif input == "b":
            self.send_input(WindowEvent.PRESS_BUTTON_B)
            heapq.heappush(self.queued_input, (self.frame_count + delay, WindowEvent.RELEASE_BUTTON_B))
        elif input == "start":
            self.send_input(WindowEvent.PRESS_BUTTON_START)
            heapq.heappush(self.queued_input, (self.frame_count + delay, WindowEvent.RELEASE_BUTTON_START))
        elif input == "select":
            self.send_input(WindowEvent.PRESS_BUTTON_SELECT)
            heapq.heappush(self.queued_input, (self.frame_count + delay, WindowEvent.RELEASE_BUTTON_SELECT))
        else:
            raise Exception("Unrecognized input:", input)

    def button_press(self, input):
        """
        Send input to PyBoy in the form of "a", "b", "start", "select", "left", "right", "up" and "down".

        The button will remain press until explicitly released with `PyBoy.button_release` or `PyBoy.send_input`.

        Example:
        ```python
        >>> pyboy.button_press('a') # Press button 'a' and keep pressed after `PyBoy.tick()`
        >>> pyboy.tick() # Button 'a' pressed
        True
        >>> pyboy.tick() # Button 'a' still pressed
        True
        >>> pyboy.button_release('a') # Release button 'a' on next call to `PyBoy.tick()`
        >>> pyboy.tick() # Button 'a' released
        True

        ```

        Args:
            input (str): button to press
        """
        input = input.lower()

        if input == "left":
            self.send_input(WindowEvent.PRESS_ARROW_LEFT)
        elif input == "right":
            self.send_input(WindowEvent.PRESS_ARROW_RIGHT)
        elif input == "up":
            self.send_input(WindowEvent.PRESS_ARROW_UP)
        elif input == "down":
            self.send_input(WindowEvent.PRESS_ARROW_DOWN)
        elif input == "a":
            self.send_input(WindowEvent.PRESS_BUTTON_A)
        elif input == "b":
            self.send_input(WindowEvent.PRESS_BUTTON_B)
        elif input == "start":
            self.send_input(WindowEvent.PRESS_BUTTON_START)
        elif input == "select":
            self.send_input(WindowEvent.PRESS_BUTTON_SELECT)
        else:
            raise Exception("Unrecognized input")

    def button_release(self, input):
        """
        Send input to PyBoy in the form of "a", "b", "start", "select", "left", "right", "up" and "down".

        This will release a button after a call to `PyBoy.button_press` or `PyBoy.send_input`.

        Example:
        ```python
        >>> pyboy.button_press('a') # Press button 'a' and keep pressed after `PyBoy.tick()`
        >>> pyboy.tick() # Button 'a' pressed
        True
        >>> pyboy.tick() # Button 'a' still pressed
        True
        >>> pyboy.button_release('a') # Release button 'a' on next call to `PyBoy.tick()`
        >>> pyboy.tick() # Button 'a' released
        True

        ```

        Args:
            input (str): button to release
        """
        input = input.lower()
        if input == "left":
            self.send_input(WindowEvent.RELEASE_ARROW_LEFT)
        elif input == "right":
            self.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
        elif input == "up":
            self.send_input(WindowEvent.RELEASE_ARROW_UP)
        elif input == "down":
            self.send_input(WindowEvent.RELEASE_ARROW_DOWN)
        elif input == "a":
            self.send_input(WindowEvent.RELEASE_BUTTON_A)
        elif input == "b":
            self.send_input(WindowEvent.RELEASE_BUTTON_B)
        elif input == "start":
            self.send_input(WindowEvent.RELEASE_BUTTON_START)
        elif input == "select":
            self.send_input(WindowEvent.RELEASE_BUTTON_SELECT)
        else:
            raise Exception("Unrecognized input")

    def send_input(self, event):
        """
        Send a single input to control the emulator. This is both Game Boy buttons and emulator controls. See
        `pyboy.utils.WindowEvent` for which events to send.

        Consider using `PyBoy.button` instead for easier access.

        Example:
        ```python
        >>> from pyboy.utils import WindowEvent
        >>> pyboy.send_input(WindowEvent.PRESS_BUTTON_A) # Press button 'a' and keep pressed after `PyBoy.tick()`
        >>> pyboy.tick() # Button 'a' pressed
        True
        >>> pyboy.tick() # Button 'a' still pressed
        True
        >>> pyboy.send_input(WindowEvent.RELEASE_BUTTON_A) # Release button 'a' on next call to `PyBoy.tick()`
        >>> pyboy.tick() # Button 'a' released
        True

        ```

        Args:
            event (pyboy.WindowEvent): The event to send
        """
        self.events.append(WindowEvent(event))

    def save_state(self, file_like_object):
        """
        Saves the complete state of the emulator. It can be called at any time, and enable you to revert any progress in
        a game.

        You can either save it to a file, or in-memory. The following two examples will provide the file handle in each
        case. Remember to `seek` the in-memory buffer to the beginning before calling `PyBoy.load_state`:

        ```python
        >>> # Save to file
        >>> with open("state_file.state", "wb") as f:
        ...     pyboy.save_state(f)
        >>>
        >>> # Save to memory
        >>> import io
        >>> with io.BytesIO() as f:
        ...     f.seek(0)
        ...     pyboy.save_state(f)
        0

        ```

        Args:
            file_like_object (io.BufferedIOBase): A file-like object for which to write the emulator state.
        """

        if isinstance(file_like_object, str):
            raise Exception("String not allowed. Did you specify a filepath instead of a file-like object?")

        if file_like_object.__class__.__name__ == "TextIOWrapper":
            raise Exception("Text file not allowed. Did you specify open(..., 'wb')?")

        self.mb.save_state(IntIOWrapper(file_like_object))

    def load_state(self, file_like_object):
        """
        Restores the complete state of the emulator. It can be called at any time, and enable you to revert any progress
        in a game.

        You can either load it from a file, or from memory. See `PyBoy.save_state` for how to save the state, before you
        can load it here.

        To load a file, remember to load it as bytes:
        ```python
        >>> # Load file
        >>> with open("state_file.state", "rb") as f:
        ...     pyboy.load_state(f)
        >>>
        ```

        Args:
            file_like_object (io.BufferedIOBase): A file-like object for which to read the emulator state.
        """

        if isinstance(file_like_object, str):
            raise Exception("String not allowed. Did you specify a filepath instead of a file-like object?")

        if file_like_object.__class__.__name__ == "TextIOWrapper":
            raise Exception("Text file not allowed. Did you specify open(..., 'rb')?")

        self.mb.load_state(IntIOWrapper(file_like_object))

    def game_area_dimensions(self, x, y, width, height, follow_scrolling=True):
        """
        If using the generic game wrapper (see `pyboy.PyBoy.game_wrapper`), you can use this to set the section of the
        tilemaps to extract. This will default to the entire tilemap.

        Example:
        ```python
        >>> pyboy.game_wrapper.shape
        (32, 32)
        >>> pyboy.game_area_dimensions(2, 2, 10, 18, False)
        >>> pyboy.game_wrapper.shape
        (10, 18)
        ```

        Args:
            x (int): Offset from top-left corner of the screen
            y (int): Offset from top-left corner of the screen
            width (int): Width of game area
            height (int): Height of game area
            follow_scrolling (bool): Whether to follow the scrolling of [SCX and SCY](https://gbdev.io/pandocs/Scrolling.html)
        """
        self.game_wrapper._set_dimensions(x, y, width, height, follow_scrolling=True)

    def game_area_collision(self):
        """
        Some game wrappers define a collision map. Check if your game wrapper has this feature implemented: `pyboy.plugins`.

        The output will be unique for each game wrapper.

        Example:
        ```python
        >>> # This example show nothing, but a supported game will
        >>> pyboy.game_area_collision()
        array([[0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=uint32)

        ```

        Returns
        -------
        memoryview:
            Simplified 2-dimensional memoryview of the collision map
        """
        return self.game_wrapper.game_area_collision()

    def game_area_mapping(self, mapping, sprite_offset=0):
        """
        Define custom mappings for tile identifiers in the game area.

        Example of custom mapping:
        ```python
        >>> mapping = [x for x in range(384)] # 1:1 mapping
        >>> mapping[0] = 0 # Map tile identifier 0 -> 0
        >>> mapping[1] = 0 # Map tile identifier 1 -> 0
        >>> mapping[2] = 0 # Map tile identifier 2 -> 0
        >>> mapping[3] = 0 # Map tile identifier 3 -> 0
        >>> pyboy.game_area_mapping(mapping, 1000)

        ```

        Some game wrappers will supply mappings as well. See the specific documentation for your game wrapper:
        `pyboy.plugins`.
        ```python
        >>> pyboy.game_area_mapping(pyboy.game_wrapper.mapping_one_to_one, 0)

        ```

        Args:
            mapping (list or ndarray): list of 384 (DMG) or 768 (CGB) tile mappings. Use `None` to reset to a 1:1 mapping.
            sprite_offest (int): Optional offset add to tile id for sprites
        """

        if mapping is None:
            mapping = [x for x in range(768)]

        assert isinstance(sprite_offset, int)
        assert isinstance(mapping, (np.ndarray, list))
        assert len(mapping) == 384 or len(mapping) == 768

        self.game_wrapper.game_area_mapping(mapping, sprite_offset)

    def game_area(self):
        """
        Use this method to get a matrix of the "game area" of the screen. This view is simplified to be perfect for
        machine learning applications.

        The layout will vary from game to game. Below is an example from Tetris:

        Example:
        ```python
        >>> pyboy.game_area()
        array([[ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47, 130, 130,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47, 130, 130,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47],
               [ 47,  47,  47,  47,  47,  47,  47,  47,  47,  47]], dtype=uint32)

        ```

        If you want a "compressed", "minimal" or raw mapping of tiles, you can change the mapping using
        `pyboy.PyBoy.game_area_mapping`. Either you'll have to supply your own mapping, or you can find one
        that is built-in with the game wrapper plugin for your game. See `pyboy.PyBoy.game_area_mapping`.

        Returns
        -------
        memoryview:
            Simplified 2-dimensional memoryview of the screen
        """

        return self.game_wrapper.game_area()

    def _serial(self):
        """
        Provides all data that has been sent over the serial port since last call to this function.

        Returns
        -------
        str :
            Buffer data
        """
        return self.mb.getserial()

    def set_emulation_speed(self, target_speed):
        """
        Set the target emulation speed. It might loose accuracy of keeping the exact speed, when using a high
        `target_speed`.

        The speed is defined as a multiple of real-time. I.e `target_speed=2` is double speed.

        A `target_speed` of `0` means unlimited. I.e. fastest possible execution.

        Some window types do not implement a frame-limiter, and will always run at full speed.

        Example:
        ```python
        >>> pyboy.tick() # Delays 16.67ms
        True
        >>> pyboy.set_emulation_speed(0) # Disable limit
        >>> pyboy.tick() # As fast as possible
        True
        ```

        Args:
            target_speed (int): Target emulation speed as multiplier of real-time.
        """
        if self.initialized and self._plugin_manager.window_null_enabled:
            logger.warning(
                'This window type does not support frame-limiting. `pyboy.set_emulation_speed(...)` will have no effect, as it\'s always running at full speed.'
            )

        if target_speed > 5:
            logger.warning("The emulation speed might not be accurate when speed-target is higher than 5")
        self.target_emulationspeed = target_speed

    def __rendering(self, value):
        """
        Disable or enable rendering
        """
        self.mb.lcd.disable_renderer = not value

    def _is_cpu_stuck(self):
        return self.mb.cpu.is_stuck

    def _load_symbols(self):
        gamerom_file_no_ext, rom_ext = os.path.splitext(self.gamerom_file)
        for sym_path in [self.symbols_file, gamerom_file_no_ext + ".sym", gamerom_file_no_ext + rom_ext + ".sym"]:
            if sym_path and os.path.isfile(sym_path):
                logger.info("Loading symbol file: %s", sym_path)
                with open(sym_path) as f:
                    for _line in f.readlines():
                        line = _line.strip()
                        if line == "":
                            continue
                        elif line.startswith(";"):
                            continue
                        elif line.startswith("["):
                            # Start of key group
                            # [labels]
                            # [definitions]
                            continue

                        try:
                            bank, addr, sym_label = re.split(":| ", line.strip())
                            bank = int(bank, 16)
                            addr = int(addr, 16)
                            if not bank in self.rom_symbols:
                                self.rom_symbols[bank] = {}

                            self.rom_symbols[bank][addr] = sym_label
                        except ValueError as ex:
                            logger.warning("Skipping .sym line: %s", line.strip())
        return self.rom_symbols

    def _lookup_symbol(self, symbol):
        for bank, addresses in self.rom_symbols.items():
            for addr, label in addresses.items():
                if label == symbol:
                    return bank, addr
        raise ValueError("Symbol not found: %s" % symbol)

    def symbol_lookup(self, symbol):
        """
        Look up a specific symbol from provided symbols file.

        This can be useful in combination with `PyBoy.memory` or even `PyBoy.hook_register`.

        See `PyBoy.hook_register` for how to load symbol into PyBoy.

        Example:
        ```python
        >>> # Continued example above
        >>> bank, addr = pyboy.symbol_lookup("Tileset")
        >>> pyboy.memory[bank, addr]
        0
        >>> pyboy.memory[bank, addr:addr+10]
        [0, 0, 0, 0, 0, 0, 102, 102, 102, 102]

        ```
        Returns
        -------
        (int, int):
            ROM/RAM bank, address
        """
        return self._lookup_symbol(symbol)

    def hook_register(self, bank, addr, callback, context):
        """
        Adds a hook into a specific bank and memory address.
        When the Game Boy executes this address, the provided callback function will be called.

        By providing an object as `context`, you can later get access to information inside and outside of the callback.

        Example:
        ```python
        >>> context = "Hello from hook"
        >>> def my_callback(context):
        ...     print(context)
        >>> pyboy.hook_register(0, 0x100, my_callback, context)
        >>> pyboy.tick(70)
        Hello from hook
        True

        ```

        If a symbol file is loaded, this function can also automatically resolve a bank and address from a symbol. To
        enable this, you'll need to place a `.sym` file next to your ROM, or provide it using:
        `PyBoy(..., symbols_file="game_rom.gb.sym")`.

        Then provide `None` for `bank` and the symbol for `addr` to trigger the automatic lookup.

        Example:
        ```python
        >>> # Continued example above
        >>> pyboy.hook_register(None, "Main.move", lambda x: print(x), "Hello from hook2")
        >>> pyboy.tick(80)
        Hello from hook2
        True

        ```

        Args:
            bank (int or None): ROM or RAM bank (None for symbol lookup)
            addr (int or str): Address in the Game Boy's address space (str for symbol lookup)
            callback (func): A function which takes `context` as argument
            context (object): Argument to pass to callback when hook is called
        """
        if bank is None and isinstance(addr, str):
            bank, addr = self._lookup_symbol(addr)

        opcode = self.memory[bank, addr]
        if opcode == 0xDB:
            raise ValueError("Hook already registered for this bank and address.")
        self.mb.breakpoint_add(bank, addr)
        bank_addr_opcode = (bank & 0xFF) << 24 | (addr & 0xFFFF) << 8 | (opcode & 0xFF)
        self._hooks[bank_addr_opcode] = (callback, context)

    def hook_deregister(self, bank, addr):
        """
        Remove a previously registered hook from a specific bank and memory address.

        Example:
        ```python
        >>> context = "Hello from hook"
        >>> def my_callback(context):
        ...     print(context)
        >>> pyboy.hook_register(0, 0x2000, my_callback, context)
        >>> pyboy.hook_deregister(0, 0x2000)

        ```

        This function can also deregister a hook based on a symbol. See `PyBoy.hook_register` for details.

        Example:
        ```python
        >>> pyboy.hook_register(None, "Main", lambda x: print(x), "Hello from hook")
        >>> pyboy.hook_deregister(None, "Main")

        ```

        Args:
            bank (int or None): ROM or RAM bank (None for symbol lookup)
            addr (int or str): Address in the Game Boy's address space (str for symbol lookup)
        """
        if bank is None and isinstance(addr, str):
            bank, addr = self._lookup_symbol(addr)

        index = self.mb.breakpoint_find(bank, addr)
        if index == -1:
            raise ValueError("Breakpoint not found for bank and addr")

        _, _, opcode = self.mb.breakpoints_list[index]
        self.mb.breakpoint_remove(index)
        bank_addr_opcode = (bank & 0xFF) << 24 | (addr & 0xFFFF) << 8 | (opcode & 0xFF)
        self._hooks.pop(bank_addr_opcode)

    def _handle_hooks(self):
        if _handler := self._hooks.get(self.mb.breakpoint_waiting):
            (callback, context) = _handler
            callback(context)
            return True
        return False

    def get_sprite(self, sprite_index):
        """
        Provides a `pyboy.api.sprite.Sprite` object, which makes the OAM data more presentable. The given index
        corresponds to index of the sprite in the "Object Attribute Memory" (OAM).

        The Game Boy supports 40 sprites in total. Read more details about it, in the [Pan
        Docs](http://bgb.bircd.org/pandocs.htm).

        ```python
        >>> s = pyboy.get_sprite(12)
        >>> s
        Sprite [12]: Position: (-8, -16), Shape: (8, 8), Tiles: (Tile: 0), On screen: False
        >>> s.on_screen
        False
        >>> s.tiles
        [Tile: 0]

        ```

        Args:
            index (int): Sprite index from 0 to 39.
        Returns
        -------
        `pyboy.api.sprite.Sprite`:
            Sprite corresponding to the given index.
        """
        return Sprite(self.mb, sprite_index)

    def get_sprite_by_tile_identifier(self, tile_identifiers, on_screen=True):
        """
        Provided a list of tile identifiers, this function will find all occurrences of sprites using the tile
        identifiers and return the sprite indexes where each identifier is found. Use the sprite indexes in the
        `pyboy.PyBoy.get_sprite` function to get a `pyboy.api.sprite.Sprite` object.

        Example:
        ```python
        >>> print(pyboy.get_sprite_by_tile_identifier([43, 123]))
        [[0, 2, 4], []]

        ```

        Meaning, that tile identifier `43` is found at the sprite indexes: 0, 2, and 4, while tile identifier
        `123` was not found anywhere.

        Args:
            identifiers (list): List of tile identifiers (int)
            on_screen (bool): Require that the matched sprite is on screen

        Returns
        -------
        list:
            list of sprite matches for every tile identifier in the input
        """

        matches = []
        for i in tile_identifiers:
            match = []
            for s in range(constants.SPRITES):
                sprite = Sprite(self.mb, s)
                for t in sprite.tiles:
                    if t.tile_identifier == i and (not on_screen or (on_screen and sprite.on_screen)):
                        match.append(s)
            matches.append(match)
        return matches

    def get_tile(self, identifier):
        """
        The Game Boy can have 384 tiles loaded in memory at once (768 for Game Boy Color). Use this method to get a
        `pyboy.api.tile.Tile`-object for given identifier.

        The identifier is a PyBoy construct, which unifies two different scopes of indexes in the Game Boy hardware. See
        the `pyboy.api.tile.Tile` object for more information.

        Example:
        ```python
        >>> t = pyboy.get_tile(2)
        >>> t
        Tile: 2
        >>> t.shape
        (8, 8)

        ```

        Returns
        -------
        `pyboy.api.tile.Tile`:
            A Tile object for the given identifier.
        """
        return Tile(self.mb, identifier=identifier)


class PyBoyMemoryView:
    """
    This class cannot be used directly, but is accessed through `PyBoy.memory`.

    This class serves four purposes: Reading memory (ROM/RAM), writing memory (ROM/RAM), overriding memory (ROM/RAM) and special registers.

    See the [Pan Docs: Memory Map](https://gbdev.io/pandocs/Memory_Map.html) for a great overview of the memory space.

    Memory can be accessed as individual bytes (`pyboy.memory[0x00]`) or as slices (`pyboy.memory[0x00:0x10]`). And if
    applicable, a specific ROM/RAM bank can be defined before the address (`pyboy.memory[0, 0x00]` or `pyboy.memory[0, 0x00:0x10]`).

    The boot ROM is accessed using the special "-1" ROM bank.

    The find addresses of interest, either search online for something like: "[game title] RAM map", or find them yourself
    using `PyBoy.memory_scanner`.

    **Read:**

    If you're developing a bot or AI with this API, you're most likely going to be using read the most. This is how you
    would efficiently read the score, time, coins, positions etc. in a game's memory.

    ```python
    >>> pyboy.memory[0x0000] # Read one byte at address 0x0000
    49
    >>> pyboy.memory[0x0000:0x0010] # Read 16 bytes from 0x0000 to 0x0010 (excluding 0x0010)
    [49, 254, 255, 33, 0, 128, 175, 34, 124, 254, 160, 32, 249, 6, 48, 33]
    >>> pyboy.memory[-1, 0x0000:0x0010] # Read 16 bytes from 0x0000 to 0x0010 (excluding 0x0010) from the boot ROM
    [49, 254, 255, 33, 0, 128, 175, 34, 124, 254, 160, 32, 249, 6, 48, 33]
    >>> pyboy.memory[0, 0x0000:0x0010] # Read 16 bytes from 0x0000 to 0x0010 (excluding 0x0010) from ROM bank 0
    [64, 65, 66, 67, 68, 69, 70, 65, 65, 65, 71, 65, 65, 65, 72, 73]
    >>> pyboy.memory[2, 0xA000] # Read from external RAM on cartridge (if any) from bank 2 at address 0xA000
    0
    ```

    **Write:**

    Writing to Game Boy memory can be complicated because of the limited address space. There's a lot of memory that
    isn't directly accessible, and can be hidden through "memory banking". This means that the same address range
    (for example 0x4000 to 0x8000) can change depending on what state the game is in.

    If you want to change an address in the ROM, then look at override below. Issuing writes to the ROM area actually
    sends commands to the [Memory Bank Controller (MBC)](https://gbdev.io/pandocs/MBCs.html#mbcs) on the cartridge.

    A write is done by assigning to the `PyBoy.memory` object. It's recommended to define the bank to avoid mistakes
    (`pyboy.memory[2, 0xA000]=1`). Without defining the bank, PyBoy will pick the current bank for the given address if
    needed (`pyboy.memory[0xA000]=1`).

    At this point, all reads will return a new list of the values in the given range. The slices will not reference back to the PyBoy memory. This feature might come in the future.

    ```python
    >>> pyboy.memory[0xC000] = 123 # Write to WRAM at address 0xC000
    >>> pyboy.memory[0xC000:0xC00A] = [0,1,2,3,4,5,6,7,8,9] # Write to WRAM from address 0xC000 to 0xC00A
    >>> pyboy.memory[0xC010:0xC01A] = 0 # Write to WRAM from address 0xC010 to 0xC01A
    >>> pyboy.memory[0x1000] = 123 # Not writing 123 at address 0x1000! This sends a command to the cartridge's MBC.
    >>> pyboy.memory[2, 0xA000] = 123 # Write to external RAM on cartridge (if any) for bank 2 at address 0xA000
    >>> # Game Boy Color (CGB) only:
    >>> pyboy_cgb.memory[1, 0x8000] = 25 # Write to VRAM bank 1 at address 0xD000 when in CGB mode
    >>> pyboy_cgb.memory[6, 0xD000] = 25 # Write to WRAM bank 6 at address 0xD000 when in CGB mode
    ```

    **Override:**

    Override data at a given memory address of the Game Boy's ROM.

    This can be used to reprogram a game ROM to change its behavior.

    This will not let your override RAM or a special register. This will let you override data in the ROM at any given bank.
    This is the memory allocated at 0x0000 to 0x8000, where 0x4000 to 0x8000 can be changed from the MBC.

    _NOTE_: Any changes here are not saved or loaded to game states! Use this function with caution and reapply
    any overrides when reloading the ROM.

    To override, it's required to provide the ROM-bank you're changing. Otherwise, it'll be considered a regular 'write' as described above.

    ```python
    >>> pyboy.memory[0, 0x0010] = 10 # Override ROM-bank 0 at address 0x0010
    >>> pyboy.memory[0, 0x0010:0x001A] = [0,1,2,3,4,5,6,7,8,9] # Override ROM-bank 0 at address 0x0010 to 0x001A
    >>> pyboy.memory[-1, 0x0010] = 10 # Override boot ROM at address 0x0010
    >>> pyboy.memory[1, 0x6000] = 12 # Override ROM-bank 1 at address 0x6000
    >>> pyboy.memory[0x1000] = 12 # This will not override, as there is no ROM bank assigned!
    ```

    **Special Registers:**

    The Game Boy has a range of memory addresses known as [hardware registers](https://gbdev.io/pandocs/Hardware_Reg_List.html). These control parts of the hardware like LCD,
    Timer, DMA, serial and so on. Even though they might appear as regular RAM addresses, reading/writing these addresses
    often results in special side-effects.

    The [DIV (0xFF04) register](https://gbdev.io/pandocs/Timer_and_Divider_Registers.html#ff04--div-divider-register) for example provides a number that increments 16 thousand times each second. This can be
    used as a source of randomness in games. If you read the value, you'll get a pseudo-random number. But if you write
    *any* value to the register, it'll reset to zero.

    ```python
    >>> pyboy.memory[0xFF04] # DIV register
    163
    >>> pyboy.memory[0xFF04] = 123 # Trying to write to it will always reset it to zero
    >>> pyboy.memory[0xFF04]
    0
    ```

    """
    def __init__(self, mb):
        self.mb = mb

    def _fix_slice(self, addr):
        if addr.start is None:
            return (-1, 0, 0)
        if addr.stop is None:
            return (0, -1, 0)
        start = addr.start
        stop = addr.stop
        if start > stop:
            return (-1, -1, 0)
        if addr.step is None:
            step = 1
        else:
            step = addr.step
        return start, stop, step

    def __getitem__(self, addr):
        is_bank = isinstance(addr, tuple)
        bank = 0
        if is_bank:
            bank, addr = addr
            assert isinstance(bank, int), "Bank has to be integer. Slicing is not supported."
        is_single = isinstance(addr, int)
        if not is_single:
            start, stop, step = self._fix_slice(addr)
            assert start >= 0 or stop >= 0, "Start address has to come before end address"
            assert start >= 0, "Start address required"
            assert stop >= 0, "End address required"
            return self.__getitem(start, stop, step, bank, is_single, is_bank)
        else:
            return self.__getitem(addr, 0, 1, bank, is_single, is_bank)

    def __getitem(self, start, stop, step, bank, is_single, is_bank):
        slice_length = (stop-start) // step
        if is_bank:
            # Reading a specific bank
            if start < 0x8000:
                if start >= 0x4000:
                    start -= 0x4000
                    stop -= 0x4000
                # Cartridge ROM Banks
                assert stop < 0x4000, "Out of bounds for reading ROM bank"
                if bank == -1:
                    assert start <= 0xFF, "Start address out of range for bootrom"
                    assert stop <= 0xFF, "Start address out of range for bootrom"
                    if not is_single:
                        mem_slice = [0] * slice_length
                        for x in range(start, stop, step):
                            mem_slice[(x-start) // step] = self.mb.bootrom.bootrom[x]
                        return mem_slice
                    else:
                        return self.mb.bootrom.bootrom[start]
                else:
                    assert bank <= self.mb.cartridge.external_rom_count, "ROM Bank out of range"
                    if not is_single:
                        mem_slice = [0] * slice_length
                        for x in range(start, stop, step):
                            mem_slice[(x-start) // step] = self.mb.cartridge.rombanks[bank, x]
                        return mem_slice
                    else:
                        return self.mb.cartridge.rombanks[bank, start]
            elif start < 0xA000:
                start -= 0x8000
                stop -= 0x8000
                # CGB VRAM Banks
                assert self.mb.cgb, "Selecting bank of VRAM is only supported for CGB mode"
                assert stop < 0x2000, "Out of bounds for reading VRAM bank"
                assert bank <= 1, "VRAM Bank out of range"

                if bank == 0:
                    if not is_single:
                        mem_slice = [0] * slice_length
                        for x in range(start, stop, step):
                            mem_slice[(x-start) // step] = self.mb.lcd.VRAM0[x]
                        return mem_slice
                    else:
                        return self.mb.lcd.VRAM0[start]
                else:
                    if not is_single:
                        mem_slice = [0] * slice_length
                        for x in range(start, stop, step):
                            mem_slice[(x-start) // step] = self.mb.lcd.VRAM1[x]
                        return mem_slice
                    else:
                        return self.mb.lcd.VRAM1[start]
            elif start < 0xC000:
                start -= 0xA000
                stop -= 0xA000
                # Cartridge RAM banks
                assert stop < 0x2000, "Out of bounds for reading cartridge RAM bank"
                assert bank <= self.mb.cartridge.external_ram_count, "ROM Bank out of range"
                if not is_single:
                    mem_slice = [0] * slice_length
                    for x in range(start, stop, step):
                        mem_slice[(x-start) // step] = self.mb.cartridge.rambanks[bank, x]
                    return mem_slice
                else:
                    return self.mb.cartridge.rambanks[bank, start]
            elif start < 0xE000:
                start -= 0xC000
                stop -= 0xC000
                if start >= 0x1000:
                    start -= 0x1000
                    stop -= 0x1000
                # CGB VRAM banks
                assert self.mb.cgb, "Selecting bank of WRAM is only supported for CGB mode"
                assert stop < 0x1000, "Out of bounds for reading VRAM bank"
                assert bank <= 7, "WRAM Bank out of range"
                if not is_single:
                    mem_slice = [0] * slice_length
                    for x in range(start, stop, step):
                        mem_slice[(x-start) // step] = self.mb.ram.internal_ram0[x + bank*0x1000]
                    return mem_slice
                else:
                    return self.mb.ram.internal_ram0[start + bank*0x1000]
            else:
                assert None, "Invalid memory address for bank"
        elif not is_single:
            # Reading slice of memory space
            mem_slice = [0] * slice_length
            for x in range(start, stop, step):
                mem_slice[(x-start) // step] = self.mb.getitem(x)
            return mem_slice
        else:
            # Reading specific address of memory space
            return self.mb.getitem(start)

    def __setitem__(self, addr, v):
        is_bank = isinstance(addr, tuple)
        bank = 0
        if is_bank:
            bank, addr = addr
            assert isinstance(bank, int), "Bank has to be integer. Slicing is not supported."
        is_single = isinstance(addr, int)
        if not is_single:
            start, stop, step = self._fix_slice(addr)
            assert start >= 0, "Start address required"
            assert stop >= 0, "End address required"
            self.__setitem(start, stop, step, v, bank, is_single, is_bank)
        else:
            self.__setitem(addr, 0, 0, v, bank, is_single, is_bank)

    def __setitem(self, start, stop, step, v, bank, is_single, is_bank):
        if is_bank:
            # Writing a specific bank
            if start < 0x8000:
                """
                Override one byte at a given memory address of the Game Boy's ROM.

                This will let you override data in the ROM at any given bank. This is the memory allocated at 0x0000 to 0x8000, where 0x4000 to 0x8000 can be changed from the MBC.

                __NOTE__: Any changes here are not saved or loaded to game states! Use this function with caution and reapply
                any overrides when reloading the ROM.

                If you need to change a RAM address, see `pyboy.PyBoy.memory`.

                Args:
                    rom_bank (int): ROM bank to do the overwrite in
                    addr (int): Address to write the byte inside the ROM bank
                    value (int): A byte of data
                """
                if start >= 0x4000:
                    start -= 0x4000
                    stop -= 0x4000
                # Cartridge ROM Banks
                assert stop < 0x4000, "Out of bounds for reading ROM bank"
                assert bank <= self.mb.cartridge.external_rom_count, "ROM Bank out of range"

                # TODO: If you change a RAM value outside of the ROM banks above, the memory value will stay the same no matter
                # what the game writes to the address. This can be used so freeze the value for health, cash etc.
                if bank == -1:
                    assert start <= 0xFF, "Start address out of range for bootrom"
                    assert stop <= 0xFF, "Start address out of range for bootrom"
                    if not is_single:
                        # Writing slice of memory space
                        if hasattr(v, "__iter__"):
                            assert (stop-start) // step == len(v), "slice does not match length of data"
                            _v = iter(v)
                            for x in range(start, stop, step):
                                self.mb.bootrom.bootrom[x] = next(_v)
                        else:
                            for x in range(start, stop, step):
                                self.mb.bootrom.bootrom[x] = v
                    else:
                        self.mb.bootrom.bootrom[start] = v
                else:
                    if not is_single:
                        # Writing slice of memory space
                        if hasattr(v, "__iter__"):
                            assert (stop-start) // step == len(v), "slice does not match length of data"
                            _v = iter(v)
                            for x in range(start, stop, step):
                                self.mb.cartridge.overrideitem(bank, x, next(_v))
                        else:
                            for x in range(start, stop, step):
                                self.mb.cartridge.overrideitem(bank, x, v)
                    else:
                        self.mb.cartridge.overrideitem(bank, start, v)

            elif start < 0xA000:
                start -= 0x8000
                stop -= 0x8000
                # CGB VRAM Banks
                assert self.mb.cgb, "Selecting bank of VRAM is only supported for CGB mode"
                assert stop < 0x2000, "Out of bounds for reading VRAM bank"
                assert bank <= 1, "VRAM Bank out of range"

                if bank == 0:
                    if not is_single:
                        # Writing slice of memory space
                        if hasattr(v, "__iter__"):
                            assert (stop-start) // step == len(v), "slice does not match length of data"
                            _v = iter(v)
                            for x in range(start, stop, step):
                                self.mb.lcd.VRAM0[x] = next(_v)
                        else:
                            for x in range(start, stop, step):
                                self.mb.lcd.VRAM0[x] = v
                    else:
                        self.mb.lcd.VRAM0[start] = v
                else:
                    if not is_single:
                        # Writing slice of memory space
                        if hasattr(v, "__iter__"):
                            assert (stop-start) // step == len(v), "slice does not match length of data"
                            _v = iter(v)
                            for x in range(start, stop, step):
                                self.mb.lcd.VRAM1[x] = next(_v)
                        else:
                            for x in range(start, stop, step):
                                self.mb.lcd.VRAM1[x] = v
                    else:
                        self.mb.lcd.VRAM1[start] = v
            elif start < 0xC000:
                start -= 0xA000
                stop -= 0xA000
                # Cartridge RAM banks
                assert stop < 0x2000, "Out of bounds for reading cartridge RAM bank"
                assert bank <= self.mb.cartridge.external_ram_count, "ROM Bank out of range"
                if not is_single:
                    # Writing slice of memory space
                    if hasattr(v, "__iter__"):
                        assert (stop-start) // step == len(v), "slice does not match length of data"
                        _v = iter(v)
                        for x in range(start, stop, step):
                            self.mb.cartridge.rambanks[bank, x] = next(_v)
                    else:
                        for x in range(start, stop, step):
                            self.mb.cartridge.rambanks[bank, x] = v
                else:
                    self.mb.cartridge.rambanks[bank, start] = v
            elif start < 0xE000:
                start -= 0xC000
                stop -= 0xC000
                if start >= 0x1000:
                    start -= 0x1000
                    stop -= 0x1000
                # CGB VRAM banks
                assert self.mb.cgb, "Selecting bank of WRAM is only supported for CGB mode"
                assert stop < 0x1000, "Out of bounds for reading VRAM bank"
                assert bank <= 7, "WRAM Bank out of range"
                if not is_single:
                    # Writing slice of memory space
                    if hasattr(v, "__iter__"):
                        assert (stop-start) // step == len(v), "slice does not match length of data"
                        _v = iter(v)
                        for x in range(start, stop, step):
                            self.mb.ram.internal_ram0[x + bank*0x1000] = next(_v)
                    else:
                        for x in range(start, stop, step):
                            self.mb.ram.internal_ram0[x + bank*0x1000] = v
                else:
                    self.mb.ram.internal_ram0[start + bank*0x1000] = v
            else:
                assert None, "Invalid memory address for bank"
        elif not is_single:
            # Writing slice of memory space
            if hasattr(v, "__iter__"):
                assert (stop-start) // step == len(v), "slice does not match length of data"
                _v = iter(v)
                for x in range(start, stop, step):
                    self.mb.setitem(x, next(_v))
            else:
                for x in range(start, stop, step):
                    self.mb.setitem(x, v)
        else:
            # Writing specific address of memory space
            self.mb.setitem(start, v)
