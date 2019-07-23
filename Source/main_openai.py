import sys
from Source.pyboy import PyBoy
from Source.pyboy.logger import addconsolehandler
from Source.openai_env import make_env

addconsolehandler()

def main(env_name):
    pyboy = PyBoy(sys.argv[1] if len(sys.argv) > 1 else None, env_name)
    env = make_env(env=pyboy)
    for _ in range(5000):
        observation, reward, done, info = env.step(9)
        # print(observation.shape)
    env.close()

if __name__ == "__main__":
    env_name = "ROMs/POKEMON BLUE.gb"
    main(env_name=env_name)
