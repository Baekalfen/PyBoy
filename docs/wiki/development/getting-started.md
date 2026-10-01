# Getting started

This page covers setting up the Python environment for developing and testing
PyBoy. For platform-specific installation, see
[Install and build](installation) for the per-platform install and source-build
instructions.

## Prerequisites

You need Python 3. Use a virtual environment to keep project dependencies
separate from system Python. The compiler and RGBDS requirements for source
builds are listed in [Install and build](installation).

Clone the repository, create and activate a virtual environment using the
instructions for your platform, then install the development and test
dependencies from the repository root:

```sh
python -m pip install -r requirements_tests.txt
```

This file includes the base requirements from `requirements.txt` as well as
pytest and the project's test dependencies. To build the Sphinx documentation,
also install its optional dependencies:

```sh
python -m pip install ".[docs]"
```

## Build PyBoy

Follow the source-build instructions for your platform in
[Install and build](installation) to compile the Cython extensions and ROM
artifacts.

## Running PyBoy

Point PyBoy at a ROM file you are entitled to use. For example:

```sh
python -m pyboy path/to/rom.gb
```

If PyBoy is installed as a package, you can run it from any directory:

```sh
pyboy path/to/rom.gb
```

Use `python -m pyboy --help` to see the available options. For example,
`python -m pyboy -w SDL2 path/to/rom.gb` selects the SDL2 window. See
[Plugins and game wrappers](../../plugins/index)
for more options.

| Keyboard key | Game Boy control |
| --- | --- |
| Up, Down, Left, Right | Directional pad |
| A | A |
| S | B |
| Return | Start |
| Backspace | Select |

| Keyboard key | Emulator function |
| --- | --- |
| Escape | Quit |
| D | Debug |
| Space | Unlimited FPS |
| Z | Save state |
| X | Load state |
| I | Toggle screen recording |
| , | Rewind backwards |
| . | Rewind forwards |

To enable rewind, see [Plugins and game wrappers](../../plugins/index).
