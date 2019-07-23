import gym
from gym import spaces
import numpy as np

SC_HEIGHT, SC_WIDTH = 160, 144

# class MyWrapper(gym.Wrapper):
class MyWrapper:
    """ Wrapper for Pokemon """

    def __init__(self, env):
        # gym.Wrapper.__init__(self, env)
        self.env = env
        # TODO: think the appropriate number of actions: https://github.com/Baekalfen/PyBoy/wiki/Installation#setup-and-run
        self.action_space = spaces.Discrete(27)
        self.observation_space = spaces.Box(low=0, high=255, shape=(SC_HEIGHT, SC_WIDTH, 3), dtype=np.uint8)
        self.reward_range = (-1, 1)  # TODO: temp reward strategy

    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
        observation, reward, done, info = self.env.step(action)  # TODO: think the reward design
        return observation, reward, done, info

    def reset(self, **kwargs):
        # TODO: think how to reset Pokemon....
        # what's the meaning of reset in Pokemon??
        return self.env.reset()

    def close(self):
        return self.env.stop()  # original stop() is implemented in pyboy.py


def make_env(env):
    """ Convert a game into OpenAI Env """
    openai_env = MyWrapper(env=env)
    return openai_env
