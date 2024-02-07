#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
"""
The core module of the emulator
"""

import os
import time

from pyboy import utils
from pyboy.logging import get_logger
from pyboy.openai_gym import PyBoyGymEnv
from pyboy.openai_gym import enabled as gym_enabled
from pyboy.plugins.manager import PluginManager
from pyboy.utils import IntIOWrapper, WindowEvent

from . import botsupport
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

        This object, `pyboy.WindowEvent`, and the `pyboy.botsupport` module, are the only official user-facing
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
        self.old_events = []
        self.quitting = False
        self.stopped = False
        self.window_title = "PyBoy"

        ###################
        # Plugins

        self.plugin_manager = PluginManager(self, self.mb, kwargs)
        self.initialized = True

    def tick(self):
        """
        Progresses the emulator ahead by one frame.

        To run the emulator in real-time, this will need to be called 60 times a second (for example in a while-loop).
        This function will block for roughly 16,67ms at a time, to not run faster than real-time, unless you specify
        otherwise with the `PyBoy.set_emulation_speed` method.

        _Open an issue on GitHub if you need finer control, and we will take a look at it._
        """
        if self.stopped:
            return True

        t_start = time.perf_counter_ns()
        self._handle_events(self.events)
        t_pre = time.perf_counter_ns()
        if not self.paused:
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

                    self.plugin_manager.handle_breakpoint()
                else:
                    if self.mb.breakpoint_singlestep_latch:
                        self.plugin_manager.handle_breakpoint()
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

        return self.quitting

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
        self.events = []

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

    def botsupport_manager(self):
        """

        Returns
        -------
        `pyboy.botsupport.BotSupportManager`:
            The manager, which gives easier access to the emulated game through the classes in `pyboy.botsupport`.
        """
        return botsupport.BotSupportManager(self, self.mb)

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

    def screen_image(self):
        """
        Shortcut for `pyboy.botsupport_manager.screen.screen_image`.

        Generates a PIL Image from the screen buffer.

        Convenient for screen captures, but might be a bottleneck, if you use it to train a neural network. In which
        case, read up on the `pyboy.botsupport` features, [Pan Docs](http://bgb.bircd.org/pandocs.htm) on tiles/sprites,
        and join our Discord channel for more help.

        Returns
        -------
        PIL.Image:
            RGB image of (160, 144) pixels
        """
        return self.botsupport_manager().screen().screen_image()

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
                self.plugin_manager.window_dummy_enabled,
                self.plugin_manager.window_headless_enabled,
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

    def _rendering(self, value):
        """
        Disable or enable rendering
        """
        self.mb.lcd.disable_renderer = not value

    def _is_cpu_stuck(self):
        return self.mb.cpu.is_stuck
