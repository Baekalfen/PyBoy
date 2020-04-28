import os, sys
os.environ["PYSDL2_DLL_PATH"] = r"PyBoy\pyboy\plugins"

import numpy as np

from gym import Env
from gym.spaces import Discrete, MultiDiscrete, Box

from pyboy import PyBoy

if __name__ == "__main__":
    filename = 'ROMs/Tetris.GB'
    game = PyBoy(filename, window_type="SDL2", window_scale=3, game_wrapper=True, debug=False)
    game.set_emulation_speed(0)
    
    env = game.openai_gymboy(observation_type='tiles', action_type='press', simultaneous_actions=False)

    observation = env.reset()
    done = False
    step = 0
    print(observation)
    while not done:
        action = np.random.randint(1, 7)
        observation, reward, done, info = env.step(action)
        if step%200==0 or done: print(step, observation, reward, done, info)
        step += 1
