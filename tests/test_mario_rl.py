#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import platform
from pathlib import Path

import pytest

record_gif_py = """
# MIT License

# Copyright (c) 2022 Pedro Alves

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import datetime
from pathlib import Path
from pyboy.pyboy import *
from gym.wrappers import FrameStack, NormalizeObservation
from AISettings.AISettingsInterface import AISettingsInterface
from AISettings.MarioAISettings import MarioAI
from AISettings.KirbyAISettings import KirbyAI
from MetricLogger import MetricLogger
from agent import AIPlayer
from wrappers import SkipFrame, ResizeObservation
import sys
from CustomPyBoyGym import CustomPyBoyGym
from functions import alphanum_key


###
#  Variables
###
episodes = 40000
observation_types = ["raw", "tiles", "compressed", "minimal"]
observation_type = observation_types[1]
action_types = ["press", "toggle", "all"]
action_type = action_types[0]
gameDimentions = (20, 16)
frameStack = 4
quiet = False
train = False
playtest = False

###
#  Choose game
###

if len(sys.argv) < 3:
    print('Provide ROM and gamename as argv')
    exit(1)
game = sys.argv[1]
gameName = sys.argv[2]

###
#  Logger
###
now = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
save_dir = Path("checkpoints") / gameName / now
save_dir_eval = Path("checkpoints") / gameName / (now + "-eval")
save_dir_boss = Path("checkpoints") / gameName / (now + "-boss")
checkpoint_dir = Path("checkpoints") / gameName

###
#  Load emulator
###
pyboy = PyBoy(game, window="null", scale=3, debug=False)

###
#  Load enviroment
###
aiSettings = AISettingsInterface()
if pyboy.game_wrapper.cartridge_title == "SUPER MARIOLAN":
    aiSettings = MarioAI()
if pyboy.game_wrapper.cartridge_title == "KIRBY DREAM LA":
    aiSettings = KirbyAI()

env = CustomPyBoyGym(pyboy, observation_type=observation_type)
env.setAISettings(aiSettings)  # use this settings
filteredActions = aiSettings.GetActions()  # get possible actions
print("Possible actions: ", [[WindowEvent(i).__str__() for i in x] for x in filteredActions])

###
#  Apply wrappers to enviroment
###
env = SkipFrame(env, skip=4)
env = ResizeObservation(env, gameDimentions)  # transform MultiDiscreate to Box for framestack
env = NormalizeObservation(env)  # normalize the values
env = FrameStack(env, num_stack=frameStack)

###
#  Load AI players
###
aiPlayer = AIPlayer((frameStack,) + gameDimentions, len(filteredActions), save_dir, now, aiSettings.GetHyperParameters())
bossAiPlayer = AIPlayer((frameStack,) + gameDimentions, len(filteredActions), save_dir_boss, now, aiSettings.GetBossHyperParameters())

folder = 'default' #folderList[choice]

fileList = [f for f in os.listdir(checkpoint_dir / folder) if f.endswith(".chkpt")]
fileList.sort(key=alphanum_key)
if len(fileList) == 0:
    print("No models to load in path: ", folder)
    quit()

modelPath = checkpoint_dir / folder / fileList[-1]
aiPlayer.loadModel(modelPath)

# choice = int(input("Select folder with boss model[1-%s] (if not using boss model select same as previous): " % cnt)) - 1
folder = 'default' #folderList[choice]
print(folder)

fileList = [f for f in os.listdir(checkpoint_dir / folder) if f.endswith(".chkpt")]
fileList.sort(key=alphanum_key)
if len(fileList) == 0:
    print("No models to load in path: ", folder)
    quit()

bossModelPath = checkpoint_dir / folder / fileList[-1]
bossAiPlayer.loadModel(bossModelPath)

###
#  Main loop
###
print("Evaluation mode")
pyboy.set_emulation_speed(0)

save_dir_eval.mkdir(parents=True)
# logger = MetricLogger(save_dir_eval)

aiPlayer.exploration_rate = 0
aiPlayer.net.eval()

bossAiPlayer.exploration_rate = 0
bossAiPlayer.net.eval()

player = aiPlayer
# for e in range(episodes):
observation = env.reset()
pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
while True:
    if aiSettings.IsBossActive(pyboy):
        player = bossAiPlayer
    else:
        player = aiPlayer
    actionId = player.act(observation)
    action = filteredActions[actionId]
    next_observation, reward, done, info = env.step(action)

    aiSettings.PrintGameState(pyboy)

    observation = next_observation

    # print(reward)
    if pyboy.frame_count > 2395:
        break
    if done:
        break

pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
pyboy.tick(1, True)
env.close()
"""


@pytest.mark.skipif(
    os.path.isfile("extras/README/6.gif") or platform.system() == "Windows",
    reason="This test takes too long for regular use"
)
def test_mario_rl(git_pyboy_rl, supermarioland_rom):
    script_py = "record_gif.py"
    with open(Path(git_pyboy_rl) / script_py, "w") as f:
        f.write(record_gif_py)

    root_path = Path("../")
    assert os.system(f'rm -rf {Path(git_pyboy_rl) / "recordings"}') == 0
    assert os.system(
        f'cd {git_pyboy_rl} && . {Path(".venv") / "bin" / "activate"} && python {script_py} {root_path / supermarioland_rom} Super_Mario_Land'
    ) == 0
    assert os.system(f'mv {Path(git_pyboy_rl) / "recordings" / "SUPER*"} {Path("extras/README/6.gif")}') == 0
