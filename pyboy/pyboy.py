#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
"""
The core module of the emulator
"""

import os
import time

import numpy as np

from pyboy import utils
from pyboy.logging import get_logger
from pyboy.openai_gym import PyBoyGymEnv
from pyboy.openai_gym import enabled as gym_enabled
from pyboy.plugins.manager import PluginManager
from pyboy.utils import IntIOWrapper, WindowEvent

from . import utils
from .api import Screen, Sprite, Tile, TileMap, constants
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
        bootrom_file=None,
        disable_renderer=False,
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

        This object, `pyboy.WindowEvent`, and the `pyboy.api` module, are the only official user-facing
        interfaces. All other parts of the emulator, are subject to change.

        A range of methods are exposed, which should allow for complete control of the emulator. Please open an issue on
        GitHub, if other methods are needed for your projects. Take a look at the files in `examples/` for a crude
        "bots", which interact with the game.

        Only the `gamerom_file` argument is required.

        Args:
            gamerom_file (str): Filepath to a game-ROM for Game Boy or Game Boy Color.

        Kwargs:
            bootrom_file (str): Filepath to a boot-ROM to use. If unsure, specify `None`.
            disable_renderer (bool): Can be used to optimize performance, by internally disable rendering of the screen.
            color_palette (tuple): Specify the color palette to use for rendering.
            cgb_color_palette (list of tuple): Specify the color palette to use for rendering in CGB-mode for non-color games.

        Other keyword arguments may exist for plugins that are not listed here. They can be viewed with the
        `parser_arguments()` method in the pyboy.plugins.manager module, or by running pyboy --help in the terminal.
        """

        self.initialized = False

        for k, v in defaults.items():
            if k not in kwargs:
                kwargs[k] = kwargs.get(k, defaults[k])

        if not os.path.isfile(gamerom_file):
            raise FileNotFoundError(f"ROM file {gamerom_file} was not found!")
        self.gamerom_file = gamerom_file

        self.mb = Motherboard(
            gamerom_file,
            bootrom_file or kwargs.get("bootrom"), # Our current way to provide cli arguments is broken
            kwargs["color_palette"],
            kwargs["cgb_color_palette"],
            disable_renderer,
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
        self.old_events = []
        self.quitting = False
        self.stopped = False
        self.window_title = "PyBoy"

        ###################
        # Plugins

        self.plugin_manager = PluginManager(self, self.mb, kwargs)
        self.initialized = True

    def _tick(self, render):
        if self.stopped:
            return False

        t_start = time.perf_counter_ns()
        self._handle_events(self.events)
        t_pre = time.perf_counter_ns()
        if not self.paused:
            self.__rendering(render)
            if self.mb.tick():
                # breakpoint reached
                self.plugin_manager.handle_breakpoint()
            else:
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
        Progresses the emulator ahead by one frame.

        To run the emulator in real-time, this will need to be called 60 times a second (for example in a while-loop).
        This function will block for roughly 16,67ms at a time, to not run faster than real-time, unless you specify
        otherwise with the `PyBoy.set_emulation_speed` method.

        _Open an issue on GitHub if you need finer control, and we will take a look at it._

        Setting `render` to `True` will make PyBoy render the screen for this tick. For AI training, it's adviced to use
        this sparingly, as it will reduce performance substantially. While setting `render` to `False`, you can still
        access the `PyBoy.game_area` to get a simpler representation of the game.

        If the screen was rendered, use `pyboy.api.screen.Screen` to get NumPy buffer or a raw memory buffer.

        Args:
            count (int): Number of ticks to process. -1 is infinite.
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
        events = self.plugin_manager.handle_events(events)
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
                self.plugin_manager._post_tick_windows()
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
        if self.frame_count % 60 == 0:
            self._update_window_title()
        self.plugin_manager.post_tick()
        self.plugin_manager.frame_limiter(self.target_emulationspeed)

        # Prepare an empty list, as the API might be used to send in events between ticks
        self.old_events = self.events
        self.events = self.queued_input
        self.queued_input = []

    def _update_window_title(self):
        avg_emu = self.avg_pre + self.avg_tick + self.avg_post
        self.window_title = f"CPU/frame: {(self.avg_pre + self.avg_tick) / SPF * 100:0.2f}%"
        self.window_title += f' Emulation: x{(round(SPF / avg_emu) if avg_emu > 0 else "INF")}'
        if self.paused:
            self.window_title += "[PAUSED]"
        self.window_title += self.plugin_manager.window_title()
        self.plugin_manager._set_title()

    def __del__(self):
        self.stop(save=False)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def stop(self, save=True):
        """
        Gently stops the emulator and all sub-modules.

        Args:
            save (bool): Specify whether to save the game upon stopping. It will always be saved in a file next to the
                provided game-ROM.
        """
        if self.initialized and not self.stopped:
            logger.info("###########################")
            logger.info("# Emulator is turning off #")
            logger.info("###########################")
            self.plugin_manager.stop()
            self.mb.stop(save)
            self.stopped = True

    ###################################################################
    # Scripts and bot methods
    #

    def openai_gym(self, observation_type="tiles", action_type="press", simultaneous_actions=False, **kwargs):
        """
        For Reinforcement learning, it is often easier to use the standard gym environment. This method will provide one.
        This function requires PyBoy to implement a Game Wrapper for the loaded ROM. You can find the supported games in pyboy.plugins.
        Additional kwargs are passed to the start_game method of the game_wrapper.

        Args:
            observation_type (str): Define what the agent will be able to see:
            * `"raw"`: Gives the raw pixels color
            * `"tiles"`:  Gives the id of the sprites in 8x8 pixel zones of the game_area defined by the game_wrapper.
            * `"compressed"`: Gives a more detailled but heavier representation than `"minimal"`.
            * `"minimal"`: Gives a minimal representation defined by the game_wrapper (recommended).

            action_type (str): Define how the agent will interact with button inputs
            * `"press"`: The agent will only press inputs for 1 frame an then release it.
            * `"toggle"`: The agent will toggle inputs, first time it press and second time it release.
            * `"all"`: The agent have access to all inputs, press and release are separated.

            simultaneous_actions (bool): Allow to inject multiple input at once. This dramatically increases the action_space: \\(n \\rightarrow 2^n\\)

        Returns
        -------
        `pyboy.openai_gym.PyBoyGymEnv`:
            A Gym environment based on the `Pyboy` object.
        """
        if gym_enabled:
            return PyBoyGymEnv(self, observation_type, action_type, simultaneous_actions, **kwargs)
        else:
            logger.error("%s: Missing dependency \"gym\". ", __name__)
            return None

    def game_wrapper(self):
        """
        Provides an instance of a game-specific wrapper. The game is detected by the cartridge's hard-coded game title
        (see `pyboy.PyBoy.cartridge_title`).

        If the game isn't supported, None will be returned.

        To get more information, find the wrapper for your game in `pyboy.plugins`.

        Returns
        -------
        `pyboy.plugins.base_plugin.PyBoyGameWrapper`:
            A game-specific wrapper object.
        """
        return self.plugin_manager.gamewrapper()

    def get_memory_value(self, addr):
        """
        Reads a given memory address of the Game Boy's current memory state. This will not directly give you access to
        all switchable memory banks. Open an issue on GitHub if that is needed, or use `PyBoy.set_memory_value` to send
        MBC commands to the virtual cartridge.

        Returns
        -------
        int:
            An integer with the value of the memory address
        """
        return self.mb.getitem(addr)

    def set_memory_value(self, addr, value):
        """
        Write one byte to a given memory address of the Game Boy's current memory state.

        This will not directly give you access to all switchable memory banks.

        __NOTE:__ This function will not let you change ROM addresses (0x0000 to 0x8000). If you write to these
        addresses, it will send commands to the "Memory Bank Controller" (MBC) of the virtual cartridge. You can read
        about the MBC at [Pan Docs](http://bgb.bircd.org/pandocs.htm).

        If you need to change ROM values, see `pyboy.PyBoy.override_memory_value`.

        Args:
            addr (int): Address to write the byte
            value (int): A byte of data
        """
        self.mb.setitem(addr, value)

    def override_memory_value(self, rom_bank, addr, value):
        """
        Override one byte at a given memory address of the Game Boy's ROM.

        This will let you override data in the ROM at any given bank. This is the memory allocated at 0x0000 to 0x8000, where 0x4000 to 0x8000 can be changed from the MBC.

        __NOTE__: Any changes here are not saved or loaded to game states! Use this function with caution and reapply
        any overrides when reloading the ROM.

        If you need to change a RAM address, see `pyboy.PyBoy.set_memory_value`.

        Args:
            rom_bank (int): ROM bank to do the overwrite in
            addr (int): Address to write the byte inside the ROM bank
            value (int): A byte of data
        """
        # TODO: If you change a RAM value outside of the ROM banks above, the memory value will stay the same no matter
        # what the game writes to the address. This can be used so freeze the value for health, cash etc.
        self.mb.cartridge.overrideitem(rom_bank, addr, value)

    def button(self, input):
        """
        Send input to PyBoy in the form of "a", "b", "start", "select", "left", "right", "up" and "down".

        The button will automatically be released at the following call to `PyBoy.tick`.

        Args:
            input (str): button to press
        """
        input = input.lower()
        if input == "left":
            self.send_input(WindowEvent.PRESS_ARROW_LEFT)
            self.queued_input.append(WindowEvent(WindowEvent.RELEASE_ARROW_LEFT))
        elif input == "right":
            self.send_input(WindowEvent.PRESS_ARROW_RIGHT)
            self.queued_input.append(WindowEvent(WindowEvent.RELEASE_ARROW_RIGHT))
        elif input == "up":
            self.send_input(WindowEvent.PRESS_ARROW_UP)
            self.queued_input.append(WindowEvent(WindowEvent.RELEASE_ARROW_UP))
        elif input == "down":
            self.send_input(WindowEvent.PRESS_ARROW_DOWN)
            self.queued_input.append(WindowEvent(WindowEvent.RELEASE_ARROW_DOWN))
        elif input == "a":
            self.send_input(WindowEvent.PRESS_BUTTON_A)
            self.queued_input.append(WindowEvent(WindowEvent.RELEASE_BUTTON_A))
        elif input == "b":
            self.send_input(WindowEvent.PRESS_BUTTON_B)
            self.queued_input.append(WindowEvent(WindowEvent.RELEASE_BUTTON_B))
        elif input == "start":
            self.send_input(WindowEvent.PRESS_BUTTON_START)
            self.queued_input.append(WindowEvent(WindowEvent.RELEASE_BUTTON_START))
        elif input == "select":
            self.send_input(WindowEvent.PRESS_BUTTON_SELECT)
            self.queued_input.append(WindowEvent(WindowEvent.RELEASE_BUTTON_SELECT))
        else:
            raise Exception("Unrecognized input:", input)

    def button_press(self, input):
        """
        Send input to PyBoy in the form of "a", "b", "start", "select", "left", "right", "up" and "down".

        The button will remain press until explicitly released with `PyBoy.button_release` or `PyBoy.send_input`.

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
        Send a single input to control the emulator. This is both Game Boy buttons and emulator controls.

        See `pyboy.WindowEvent` for which events to send.

        Args:
            event (pyboy.WindowEvent): The event to send
        """
        self.events.append(WindowEvent(event))

    def get_input(
        self,
        ignore=(
            WindowEvent.PASS, WindowEvent._INTERNAL_TOGGLE_DEBUG, WindowEvent._INTERNAL_RENDERER_FLUSH,
            WindowEvent._INTERNAL_MOUSE, WindowEvent._INTERNAL_MARK_TILE
        )
    ):
        """
        Get current inputs except the events specified in "ignore" tuple.
        This is both Game Boy buttons and emulator controls.

        See `pyboy.WindowEvent` for which events to get.

        Args:
            ignore (tuple): Events this function should ignore

        Returns
        -------
        list:
            List of the `pyboy.utils.WindowEvent`s processed for the last call to `pyboy.PyBoy.tick`
        """
        return [x for x in self.old_events if x not in ignore]

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

    def game_area(self):
        raise Exception("game_area not implemented")

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

        Args:
            target_speed (int): Target emulation speed as multiplier of real-time.
        """
        if self.initialized:
            unsupported_window_types_enabled = [
                self.plugin_manager.window_dummy_enabled, self.plugin_manager.window_headless_enabled,
                self.plugin_manager.window_open_gl_enabled
            ]
            if any(unsupported_window_types_enabled):
                logger.warning(
                    'This window type does not support frame-limiting. `pyboy.set_emulation_speed(...)` will have no effect, as it\'s always running at full speed.'
                )

        if target_speed > 5:
            logger.warning("The emulation speed might not be accurate when speed-target is higher than 5")
        self.target_emulationspeed = target_speed

    def cartridge_title(self):
        """
        Get the title stored on the currently loaded cartridge ROM. The title is all upper-case ASCII and may
        have been truncated to 11 characters.

        Returns
        -------
        str :
            Game title
        """
        return self.mb.cartridge.gamename

    def __rendering(self, value):
        """
        Disable or enable rendering
        """
        self.mb.lcd.disable_renderer = not value

    def _is_cpu_stuck(self):
        return self.mb.cpu.is_stuck

    @property
    def screen(self):
        """
        Use this method to get a `pyboy.api.screen.Screen` object. This can be used to get the screen buffer in
        a variety of formats.

        It's also here you can find the screen position (SCX, SCY, WX, WY) for each scan line in the screen buffer. See
        `pyboy.api.screen.Screen.tilemap_position` for more information.

        Returns
        -------
        `pyboy.api.screen.Screen`:
            A Screen object with helper functions for reading the screen buffer.
        """
        return Screen(self.mb)

    def get_sprite(self, sprite_index):
        """
        Provides a `pyboy.api.sprite.Sprite` object, which makes the OAM data more presentable. The given index
        corresponds to index of the sprite in the "Object Attribute Memory" (OAM).

        The Game Boy supports 40 sprites in total. Read more details about it, in the [Pan
        Docs](http://bgb.bircd.org/pandocs.htm).

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
        `pyboy.sprite` function to get a `pyboy.api.sprite.Sprite` object.

        Example:
        ```
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
        The Game Boy can have 384 tiles loaded in memory at once. Use this method to get a
        `pyboy.api.tile.Tile`-object for given identifier.

        The identifier is a PyBoy construct, which unifies two different scopes of indexes in the Game Boy hardware. See
        the `pyboy.api.tile.Tile` object for more information.

        Returns
        -------
        `pyboy.api.tile.Tile`:
            A Tile object for the given identifier.
        """
        return Tile(self.mb, identifier=identifier)

    @property
    def tilemap_background(self):
        """
        The Game Boy uses two tile maps at the same time to draw graphics on the screen. This method will provide one
        for the _background_ tiles. The game chooses whether it wants to use the low or the high tilemap.

        Read more details about it, in the [Pan Docs](http://bgb.bircd.org/pandocs.htm#vrambackgroundmaps).

        Returns
        -------
        `pyboy.api.tilemap.TileMap`:
            A TileMap object for the tile map.
        """
        return TileMap(self.mb, "BACKGROUND")

    @property
    def tilemap_window(self):
        """
        The Game Boy uses two tile maps at the same time to draw graphics on the screen. This method will provide one
        for the _window_ tiles. The game chooses whether it wants to use the low or the high tilemap.

        Read more details about it, in the [Pan Docs](http://bgb.bircd.org/pandocs.htm#vrambackgroundmaps).

        Returns
        -------
        `pyboy.api.tilemap.TileMap`:
            A TileMap object for the tile map.
        """
        return TileMap(self.mb, "WINDOW")


class PyBoyMemoryView:
    def __init__(self, mb):
        self.mb = mb

    def _fix_slice(self, addr):
        if addr.start is None:
            return (-1, 0, 0)
        if addr.stop is None:
            return (0, -1, 0)
        start = addr.start
        stop = addr.stop
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
            assert start >= 0, "Start address required"
            assert stop >= 0, "End address required"
            return self.__getitem(start, stop, step, bank, is_single, is_bank)
        else:
            return self.__getitem(addr, 0, 0, bank, is_single, is_bank)

    def __getitem(self, start, stop, step, bank, is_single, is_bank):
        if is_bank:
            # Reading a specific bank
            if start < 0x8000:
                if start >= 0x4000:
                    start -= 0x4000
                    stop -= 0x4000
                # Cartridge ROM Banks
                assert stop < 0x4000, "Out of bounds for reading ROM bank"
                assert bank <= self.mb.cartridge.external_rom_count, "ROM Bank out of range"
                if not is_single:
                    return [self.mb.cartridge.rombanks[bank][x] for x in range(start, stop, step)]
                else:
                    return self.mb.cartridge.rombanks[bank][start]
            elif start < 0xA000:
                start -= 0x8000
                stop -= 0x8000
                # CGB VRAM Banks
                assert self.mb.cgb, "Selecting bank of VRAM is only supported for CGB mode"
                assert stop < 0x2000, "Out of bounds for reading VRAM bank"
                assert bank <= 1, "VRAM Bank out of range"

                if bank == 0:
                    if not is_single:
                        return [self.mb.lcd.VRAM0[x] for x in range(start, stop, step)]
                    else:
                        return self.mb.lcd.VRAM0[start]
                else:
                    if not is_single:
                        return [self.mb.lcd.VRAM1[x] for x in range(start, stop, step)]
                    else:
                        return self.mb.lcd.VRAM1[start]
            elif start < 0xC000:
                start -= 0xA000
                stop -= 0xA000
                # Cartridge RAM banks
                assert stop < 0x2000, "Out of bounds for reading cartridge RAM bank"
                assert bank <= self.mb.cartridge.external_ram_count, "ROM Bank out of range"
                if not is_single:
                    return [self.mb.cartridge.rambanks[bank][x] for x in range(start, stop, step)]
                else:
                    return self.mb.cartridge.rambanks[bank][start]
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
                    return [self.mb.ram.internal_ram0[x + bank*0x1000] for x in range(start, stop, step)]
                else:
                    return self.mb.ram.internal_ram0[start + bank*0x1000]
            else:
                assert None, "Invalid memory address for bank"
        elif not is_single:
            # Reading slice of memory space
            return [self.mb.getitem(x) for x in range(start, stop, step)]
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
                assert None, "Cannot write to ROM banks"
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
                            self.mb.cartridge.rambanks[bank][x] = next(_v)
                    else:
                        for x in range(start, stop, step):
                            self.mb.cartridge.rambanks[bank][x] = v
                else:
                    self.mb.cartridge.rambanks[bank][start] = v
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
