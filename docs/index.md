# PyBoy

PyBoy is a Game Boy emulator written in Python and Cython. It can be used
directly from the command line or embedded in Python programs for automation,
testing, and AI experiments.

```{toctree}
:maxdepth: 2
:hidden:

api/index
plugins/index
wiki/development/index
wiki/examples/index
wiki/test-results
```

## Installation

Install PyBoy from PyPI with:

```sh
pip install pyboy
```

See the [platform-specific installation instructions](wiki/development/index)
for macOS, Linux, and Windows.

## Command line

Run a ROM directly from the command line:

```sh
pyboy game_rom.gb
```

## Python usage

PyBoy can be embedded in a Python program to send input, inspect memory, and
capture screenshots:

```python
from pyboy import PyBoy

pyboy = PyBoy("game_rom.gb")
pyboy.set_emulation_speed(0)
pyboy.button("down")
pyboy.button("a")
pyboy.tick() # Progress emulation

value = pyboy.memory[0xC345]
pyboy.screen.image.save("screenshot.png")
pyboy.stop()
```

## Performance

Rendering is optional. If a script does not need every frame, pass a larger
frame count to {meth}``pyboy.PyBoy.tick`` or disable rendering for the fastest
emulation:

```python
# Render every frame
for _ in range(target):
    pyboy.tick()

# Render only the last of 'target' frames
pyboy.tick(target, False)
```

Skipping rendering and running multiple emulator instances in parallel can
substantially improve emulation throughput.

Use the [API reference](api/index) for the supported Python interface.

## Further resources

- [PyBoy on GitHub](https://github.com/Baekalfen/PyBoy)
- [Community Discord](https://discord.gg/wUbag3KNqQ)
- [Pan Docs](https://gbdev.io/pandocs/)