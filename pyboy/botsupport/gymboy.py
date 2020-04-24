import numpy as np

from gym import Env
from gym.spaces import Discrete, MultiDiscrete

from pyboy.plugins.base_plugin import PyBoyGameWrapper
from pyboy import PyBoy, WindowEvent

class GymBoy(Env):

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
                - 'raw' gives the raw pixels color
                - 'tiles' gives the id of the sprites in 8x8 pixel zones of the game_area defined by the game_wrapper (Only useful in grid-based games).

        buttons_press_mode: str
            Define how the agent will interact with button inputs:
                - 'press' the agent will only press inputs for 1 frame an then release it.
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

        button_is_pressed: dict
            The dictionary of state 0/1 or released/press for every button (only used if buttons_press_mode=='toggle' or 'all').

        release_button: dict
            The dictionary of input IDs for releasing a button.
    
    """

    def __init__(self, game, observation_type='tiles', buttons_press_mode='toggle', simultaneous_actions=False):
        # Build game
        self.game = game
        if not isinstance(game, PyBoy):
            raise TypeError("game must be a Pyboy object")
        
        # Build game_wrapper
        self.game_wrapper = game.game_wrapper()
        if self.game_wrapper is None:
            raise ValueError("You need to build a game_wrapper to use this function. Otherwise there is no way to build a reward function automaticaly.")
        self.last_fitness = self.game_wrapper.fitness

        # Building the action_space
        self._DO_NOTHING = -1
        buttons = [WindowEvent.PRESS_ARROW_UP, WindowEvent.PRESS_ARROW_DOWN,
                    WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.PRESS_ARROW_LEFT,
                    WindowEvent.PRESS_BUTTON_A, WindowEvent.PRESS_BUTTON_B,
                    WindowEvent.PRESS_BUTTON_SELECT, WindowEvent.PRESS_BUTTON_START]
        self.button_is_pressed = {button:False for button in buttons}
        
        buttons_release = [WindowEvent.RELEASE_ARROW_UP, WindowEvent.RELEASE_ARROW_DOWN,
                    WindowEvent.RELEASE_ARROW_RIGHT, WindowEvent.RELEASE_ARROW_LEFT,
                    WindowEvent.RELEASE_BUTTON_A, WindowEvent.RELEASE_BUTTON_B,
                    WindowEvent.RELEASE_BUTTON_SELECT, WindowEvent.RELEASE_BUTTON_START]
        self.release_button = {button:r_button for button, r_button in zip(buttons, buttons_release)}
        
        self.actions = [self._DO_NOTHING] + buttons
        if buttons_press_mode == 'all':
            self.actions += buttons_release
        elif not (buttons_press_mode == 'press' or buttons_press_mode == 'toggle'):
            raise ValueError(f'buttons_press_mode {buttons_press_mode} is unknowed')
        self.buttons_press_mode = buttons_press_mode

        if simultaneous_actions:
            raise NotImplementedError("Not yet implemented, raise an issue if needed")
        else:
            self.action_space = Discrete(len(self.actions))

        # Building the observation_space
        if observation_type == 'raw' or observation_type != 'tiles':
            raise NotImplementedError(f"observation_type {observation_type} is not implemented yet raise an issue if needed")         
        if observation_type == 'tiles':
            nvec = np.ones(self.game_wrapper.shape)
        self.observation_type = observation_type
        self.observation_space = MultiDiscrete(nvec)
    
    def step(self, action_id):
        observation = 0
        info = {}

        action = self.actions[action_id]
        if action == self._DO_NOTHING:
            done = self.game.tick()
        else:
            if self.buttons_press_mode == 'toggle':
                if self.button_is_pressed[action]:
                    self.button_is_pressed[action] = False
                    action = self.release_button[action]
                else:
                    self.button_is_pressed[action] = True

            self.game.send_input(action)
            done = self.game.tick()
        
            if self.buttons_press_mode == 'press':
                self.game.send_input(self.release_button[action])

        new_fitness = self.game_wrapper.fitness
        reward = new_fitness - self.last_fitness
        self.last_fitness = new_fitness

        return observation, reward, done, info

    def reset(self):
        # self.game.reset()
        if self.game_wrapper is not None: self.game_wrapper.start_game()
        return 0

    def render(self):
        raise NotImplementedError
