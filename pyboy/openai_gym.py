#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np

from gym import Env
from gym.spaces import Discrete, MultiDiscrete, Box

from pyboy.botsupport.constants import TILES

class PyBoyGymEnv(Env):

    """ A gym environement built from a `pyboy.PyBoy`
    
    Arguments
    ---------

        game: `pyboy.PyBoy`
            A PyBoy game instance

        observation_type: str
            Define what the agent will be able to see :
                - 'raw' gives the raw pixels color
                - 'tiles' gives the id of the sprites in 8x8 pixel zones of the game_area defined by the game_wrapper (Only useful in grid-based games).

        buttons_press_mode: str
            Define how the agent will interact with button inputs:
                - 'press' the agent will only press inputs for 1 frame an then release it.
                - 'toggle' the agent will toggle inputs, first time it press and second time it release.
                - 'all' the agent have acces to all inputs, press and release are separated.

        simultaneous_actions: bool
            If true, the agent is allowed to inject multiple inputs at the same time. Caution, this also means that the action_space is way bigger (n -> 2^n)!

    Attributes
    ----------

        game: `pyboy.PyBoy`
            The PyBoy game instance over which the environment is built.
        
        observation_type: str
            Define what the agent will be able to see :
                - 'raw' gives the raw RGB pixels color
                - 'tiles' gives the id of the sprites and tiles in 8x8 pixel zones of the game_area defined by the game_wrapper.

        buttons_press_mode: str
            Define how the agent will interact with button inputs:
                - 'press' the agent will only press inputs for 1 frame and then release it.
                - 'toggle' the agent will toggle inputs, first time it press and second time it release.
                - 'all' the agent have acces to all inputs, press and release are separated.
        
        game_wrapper: `pyboy.plugins.base_plugin.PyBoyGameWrapper`
            The game_wrapper of the PyBoy game instance over which the environment is built.

        action_space: Gym space
            The action space of the environment.

        observation_space: Gym space
            The observation space of the environment (depends of observation_type).
        
        last_fitness: float or int
            The last observed fitness, used to compute the reward at each step

        actions: list
            The list of input IDs of allowed input for the agent (depends of buttons_press_mode).
    
    """

    def __init__(self, game, observation_type='tiles', buttons_press_mode='toggle', simultaneous_actions=False):
        # Build game
        self.game = game
        if str(type(game)) != "<class 'pyboy.pyboy.PyBoy'>":
            raise TypeError("game must be a Pyboy object")
        
        # Build game_wrapper
        self.game_wrapper = game.game_wrapper()
        if self.game_wrapper is None:
            raise ValueError("You need to build a game_wrapper to use this function. Otherwise there is no way to build a reward function automaticaly (for now).")
        self.last_fitness = self.game_wrapper.fitness

        # Building the action_space
        self._DO_NOTHING = -1
        self._buttons = list(range(1, 9)) # UP DOWN RIGHT LEFT A B SELECT START
        self._button_is_pressed = {button:False for button in self._buttons}
        
        self._buttons_release = list(range(9, 17)) # UP DOWN RIGHT LEFT A B SELECT START
        self._release_button = {button:r_button for button, r_button in zip(self._buttons, self._buttons_release)}
        
        self.actions = [self._DO_NOTHING] + self._buttons
        if buttons_press_mode == 'all':
            self.actions += self._buttons_release
        elif buttons_press_mode not in ['press', 'toggle']:
            raise ValueError(f'buttons_press_mode {buttons_press_mode} is unknowed')
        self.buttons_press_mode = buttons_press_mode

        if simultaneous_actions:
            raise NotImplementedError("Not implemented yet, raise an issue on GitHub if needed")
        else:
            self.action_space = Discrete(len(self.actions))

        # Building the observation_space
        if observation_type == 'raw':
            screen = np.asarray(self.game.botsupport_manager().screen().screen_ndarray())
            self.observation_space = Box(low=0, high=255, shape=screen.shape, dtype=np.uint32)
        elif observation_type == 'tiles':
            nvec = TILES * np.ones(self.game_wrapper.shape)
            self.observation_space = MultiDiscrete(nvec)
        else:
            raise NotImplementedError(f"observation_type {observation_type} is unknowed")
        self.observation_type = observation_type

        self._started = False
    
    def get_observation(self):
        if self.observation_type == 'raw':
            observation = np.asarray(self.game.botsupport_manager().screen().screen_ndarray(), dtype=np.uint32)
        elif self.observation_type == 'tiles':
            observation = np.asarray(self.game_wrapper.game_area(), dtype=np.uint32)
        else:
            raise NotImplementedError(f"observation_type {self.observation_type} is unknowed")
        return observation
    
    def step(self, action_id):
        info = {}

        action = self.actions[action_id]
        if action == self._DO_NOTHING:
            pyboy_done = self.game.tick()
        else:
            if self.buttons_press_mode == 'toggle':
                if self._button_is_pressed[action]:
                    self._button_is_pressed[action] = False
                    action = self._release_button[action]
                else:
                    self._button_is_pressed[action] = True

            self.game.send_input(action)
            pyboy_done = self.game.tick()
        
            if self.buttons_press_mode == 'press':
                self.game.send_input(self._release_button[action])

        new_fitness = self.game_wrapper.fitness
        reward = new_fitness - self.last_fitness
        self.last_fitness = new_fitness

        observation = self.get_observation()
        done = pyboy_done or self.game_wrapper.game_over()

        return observation, reward, done, info

    def reset(self):
        """ Reset (or start) the gym environment throught the game_wrapper """
        if not self._started: 
            self.game_wrapper.start_game()
            self._started = True
        else:
            self.game_wrapper.reset_game()
        self.last_fitness = self.game_wrapper.fitness
        self.button_is_pressed = {button:False for button in self._buttons}
        return self.get_observation()

    def render(self):
        pass
