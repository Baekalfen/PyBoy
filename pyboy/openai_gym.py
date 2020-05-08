#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np

from .botsupport.constants import TILES
from .utils import WindowEvent

try:
    from gym import Env
    from gym.spaces import Discrete, MultiDiscrete, Box
    enabled = True
except ImportError:

    class Env:
        pass

    enabled = False


class PyBoyGymEnv(Env):
    """ A gym environement built from a `pyboy.PyBoy`

    This function requires PyBoy to implement a Game Wrapper for the loaded ROM. You can find the supported games in pyboy.plugins.
    Additional kwargs are passed to the start_game method of the game_wrapper.

    Args:
        observation_type (str): Define what the agent will be able to see:
        * `"raw"`: Gives the raw pixels color
        * `"tiles"`:  Gives the id of the sprites and tiles in 8x8 pixel zones of the game_area.
        * `"compressed"`: Like `"tiles"` but with slightly simplified id's (i.e. each type of enemy has a unique id).
        * `"minimal"`: Like `"compressed"` but gives a minimal representation (recommended; i.e. all enemies have the same id).

        action_type (str): Define how the agent will interact with button inputs
        * `"press"`: The agent will only press inputs for 1 frame an then release it.
        * `"toggle"`: The agent will toggle inputs, first time it press and second time it release.
        * `"all"`: The agent have acces to all inputs, press and release are separated.

        simultaneous_actions (bool): Allow to inject multiple input at once. This dramatically increases the action_space: \\(n \\rightarrow 2^n\\)

    Attributes:
        game_wrapper (`pyboy.plugins.base_plugin.PyBoyGameWrapper`): The game_wrapper of the PyBoy game instance over which the environment is built.
        action_space (Gym space): The action space of the environment.
        observation_space (Gym space): The observation space of the environment (depends of observation_type).
        actions (list): The list of input IDs of allowed input for the agent (depends of action_type).

    """
    def __init__(self, pyboy, observation_type="tiles", action_type="toggle", simultaneous_actions=False, **kwargs):
        # Build pyboy game
        self.pyboy = pyboy
        if str(type(pyboy)) != "<class 'pyboy.pyboy.PyBoy'>":
            raise TypeError("pyboy must be a Pyboy object")

        # Build game_wrapper
        self.game_wrapper = pyboy.game_wrapper()
        if self.game_wrapper is None:
            raise ValueError(
                "You need to build a game_wrapper to use this function. Otherwise there is no way to build a reward function automaticaly."
            )
        self.last_fitness = self.game_wrapper.fitness

        # Building the action_space
        self._DO_NOTHING = WindowEvent.PASS
        self._buttons = [
            WindowEvent.PRESS_ARROW_UP, WindowEvent.PRESS_ARROW_DOWN, WindowEvent.PRESS_ARROW_RIGHT,
            WindowEvent.PRESS_ARROW_LEFT, WindowEvent.PRESS_BUTTON_A, WindowEvent.PRESS_BUTTON_B,
            WindowEvent.PRESS_BUTTON_SELECT, WindowEvent.PRESS_BUTTON_START
        ]
        self._button_is_pressed = {button: False for button in self._buttons}

        self._buttons_release = [
            WindowEvent.RELEASE_ARROW_UP, WindowEvent.RELEASE_ARROW_DOWN, WindowEvent.RELEASE_ARROW_RIGHT,
            WindowEvent.RELEASE_ARROW_LEFT, WindowEvent.RELEASE_BUTTON_A, WindowEvent.RELEASE_BUTTON_B,
            WindowEvent.RELEASE_BUTTON_SELECT, WindowEvent.RELEASE_BUTTON_START
        ]
        self._release_button = {button: r_button for button, r_button in zip(self._buttons, self._buttons_release)}

        self.actions = [self._DO_NOTHING] + self._buttons
        if action_type == "all":
            self.actions += self._buttons_release
        elif action_type not in ["press", "toggle"]:
            raise ValueError(f"action_type {action_type} is invalid")
        self.action_type = action_type

        if simultaneous_actions:
            raise NotImplementedError("Not implemented yet, raise an issue on GitHub if needed")
        else:
            self.action_space = Discrete(len(self.actions))

        # Building the observation_space
        if observation_type == "raw":
            screen = np.asarray(self.pyboy.botsupport_manager().screen().screen_ndarray())
            self.observation_space = Box(low=0, high=255, shape=screen.shape, dtype=np.uint8)
        elif observation_type in ["tiles", "compressed", "minimal"]:
            size_ids = TILES
            if observation_type == "compressed":
                try:
                    size_ids = np.max(self.game_wrapper.tiles_compressed) + 1
                except AttributeError:
                    raise AttributeError(
                        "You need to add the tiles_compressed attibute to the game_wrapper to use the compressed observation_type"
                    )
            elif observation_type == "minimal":
                try:
                    size_ids = np.max(self.game_wrapper.tiles_minimal) + 1
                except AttributeError:
                    raise AttributeError(
                        "You need to add the tiles_minimal attibute to the game_wrapper to use the minimal observation_type"
                    )
            nvec = size_ids * np.ones(self.game_wrapper.shape)
            self.observation_space = MultiDiscrete(nvec)
        else:
            raise NotImplementedError(f"observation_type {observation_type} is invalid")
        self.observation_type = observation_type

        self._started = False
        self._kwargs = kwargs

    def _get_observation(self):
        if self.observation_type == "raw":
            observation = np.asarray(self.pyboy.botsupport_manager().screen().screen_ndarray(), dtype=np.uint8)
        elif self.observation_type in ["tiles", "compressed", "minimal"]:
            observation = self.game_wrapper._game_area_np(self.observation_type)
        else:
            raise NotImplementedError(f"observation_type {self.observation_type} is invalid")
        return observation

    def step(self, action_id):
        info = {}

        action = self.actions[action_id]
        if action == self._DO_NOTHING:
            pyboy_done = self.pyboy.tick()
        else:
            if self.action_type == "toggle":
                if self._button_is_pressed[action]:
                    self._button_is_pressed[action] = False
                    action = self._release_button[action]
                else:
                    self._button_is_pressed[action] = True

            self.pyboy.send_input(action)
            pyboy_done = self.pyboy.tick()

            if self.action_type == "press":
                self.pyboy.send_input(self._release_button[action])

        new_fitness = self.game_wrapper.fitness
        reward = new_fitness - self.last_fitness
        self.last_fitness = new_fitness

        observation = self._get_observation()
        done = pyboy_done or self.game_wrapper.game_over()

        return observation, reward, done, info

    def reset(self):
        """ Reset (or start) the gym environment throught the game_wrapper """
        if not self._started:
            self.game_wrapper.start_game(**self._kwargs)
            self._started = True
        else:
            self.game_wrapper.reset_game()
        self.last_fitness = self.game_wrapper.fitness
        self.button_is_pressed = {button: False for button in self._buttons}
        return self._get_observation()

    def render(self):
        pass

    def close(self):
        self.pyboy.stop(save=False)
