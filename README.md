# PyBoy

It is highly recommended to read the [report](https://github.com/Baekalfen/PyBoy/raw/master/PyBoy.pdf) to get a light introduction to Game Boy emulation. The report is relevant, eventhough you want to contribute to another emulator, or create your own.

If you've read the report and want more explicit details, have a look at the [Pan Docs](http://bgb.bircd.org/pandocs.htm).

<p align="center">
<img src="https://github.com/Baekalfen/PyBoy/raw/master/README/1.gif" width="320">
<img src="https://github.com/Baekalfen/PyBoy/raw/master/README/2.gif" width="316"><br>
<img src="https://github.com/Baekalfen/PyBoy/raw/master/README/3.gif" width="316">
<img src="https://github.com/Baekalfen/PyBoy/raw/master/README/4.gif" width="320">
</p>

Table of Contents
=================
* [Abstract](#abstract)
* [Starting the Emulator](#starting-the-emulator)
    * [macOS](#macos)
    * [Ubuntu/Linux](#ubuntulinux)
    * [Windows](#windows)
    * [Setup and Run](#setup-and-run)
    * [Experimental Game Windows](#experimental-game-windows)
* [Scripts/Bots](#scriptsbots)
* [Compatibility](#compatibility)
* [Contribute](#contribute)
* [License](#license)


Abstract
========
This project is covering an emulation of the Nintendo Game Boy (DMG-01) from 1989. The Game Boy has been emulated many times before, but this project will emulate it in the programming language Python 2.7. The implementation is not based on any existing emulator, but is made from scratch. The emulation has proven to be fast enough, to run software from cartridge dumps, with the same speed as the Game Boy. Most essential components of the Game Boy, are part of the emulation, but sound and serial port are not included in this project. The implementation runs in almost pure Python, but with dependencies for drawing graphics and getting user interactions through SDL2 and NumPy.

Starting the Emulator
=====================
*It should be noted, that the emulator is still under development. Eventhough games might work flawlessly now, be prepared, that saved games may be lost without any further notice.*

CPython is no where fast enough to run the emulator (see [PyBoy.pdf](https://github.com/Baekalfen/PyBoy/raw/master/PyBoy.pdf) about performance). It is therefore required to use PyPy.

The code has a few dependencies, but it should be fairly easy to get it up and running. The code is developed on macOS, but has been tested to run on Ubuntu 16.04 and Windows 10.

macOS
-----
The easiest way to get started, is to first install [brew](https://brew.sh).

When brew is installed, the depencencies can be installed with the following commands in the terminal:

    brew update
    brew install git pypy sdl2 sdl2_gfx sdl2_image
    brew link sdl2

    pip_pypy install -r requirements.txt


Ubuntu/Linux
------------
Ubuntu has some problems installing PyPy in parallel with the system version of CPython. Therefore, we will install the PyPy version of NumPy and PySDL2 in a virtualenv. First, however, we need to install some dependencies.

    sudo apt update
    sudo apt install git pypy pypy-dev virtualenv libsdl2-dev libtiff5-dev libjpeg8-dev zlib1g-dev

Now move to the project directory `PyBoy/` (or wherever you keep your virtual environments) and create the virtual environment:

    virtualenv . -p $(which pypy)
    source bin/activate

    pip install -r Source/requirements.txt


Windows
-------
First, install Git, vcredist and VCForPython27:

* https://git-scm.com/download/win
* https://www.microsoft.com/en-us/download/details.aspx?id=5582
* https://www.microsoft.com/en-us/download/details.aspx?id=44266

Then download the latest Pypy 32-bit (64-bit pre-built isn't available). At the time of writing the newest version is `pypy2-v5.7.1-win32.zip`:

* https://bitbucket.org/pypy/pypy/downloads/

Unzip it, and place the contents somewhere like: `C:\pypy2\`.

Search from "Edit the system environment varibles" from the start menu. Add `C:\pypy2;` at the beginning of the value of the `Path` variable.

Start a Command Prompt and run the following:

    pypy -m ensurepip
    pypy -m pip install -U pip wheel
    pypy -m pip install -r requirements.txt

Download SDL2 Runtime Binaries for 32-bit Windows:

* https://www.libsdl.org/download-2.0.php

Place it somewhere you can locate it. I chose `C:\pypy2\SDL2.dll`. Then set the variable from the Command Prompt.

    set PYSDL2_DLL_PATH=C:\pypy2\SDL2.dll


Setup and Run
-------------
Now, create a directory at `Source/ROMs` and place your ROMs in this directory -- which you of course dumped yourself with [PyBoyCartridge](https://github.com/Baekalfen/PyBoyCartridge)

Then run `pypy main.py` from the `Source` directory and choose a ROM to start.

For more advanced use, you can use `pypy main.py [GameWindow] [ROM path]`. For example: `pypy main.py SDL2 ROMs/game.rom`. Currently, the GameWindows `SDL2` and `dummy` are supported. Use `SDL2` if you want to see the screen, and `dummy` if you want to run PyBoy headless.

The Game Boy controls are as follows:

| Keyboard key | GameBoy equivalant |
| ---          | ---                |
| Up           | Up                 |
| Down         | Down               |
| Left         | Left               |
| Right        | Right              |
| A            | A                  |
| S            | B                  |
| Return       | Start              |
| Backspace    | Select             |

The other controls for the emulator:

| Keyboard key | Emulator function       |
| ---          | ---                     |
| Escape       | Quit                    |
| D            | Debug                   |
| Space        | Unlimited FPS           |
| Z            | Save state              |
| X            | Load state              |
| I            | Toggle screen recording |

Note, that debug and save/load state might not be perfectly stable.


Experimental Game Windows
-------------------------

PyBoy is bundled with several renderers, called "Game Windows". The recommended is `SDL2`, and its installation is described in the installation instructions above.

The installations instructions here, will be sparse, as they are mostly for the technically interested.

1. `SDL2` : Instructions are found above.
2. `scanline` : Instructions are the same as `SDL2`.
3. `OpenGL` : Install OpenGL and FreeGLUT through the system's package manager. Install `pyopengl` and optionally `pyopengl-accelerate` through pip.
4. `dummy` : No installation required.
5. `SDL2Process` : Instructions are the same as `SDL2`. Stability and performance is uncertain.


Scripts/Bots
============
PyBoy is loadable as an object in Python. This means, it can be initialized from another script, and be controlled and probed by the script. Take a look at `tetris_bot.py` for a crude "bot", which interacts with the game.

Currently, 8 methods are exposed, which should allow for complete control of the Game Boy. Please open an issue here on GitHub, if other methods are needed.

The Methods are:
1. __tick()__ Progresses the Game Boy ahead by one frame. _Open an issue if you need finer control._
2. __getScreenBuffer()__ Returns a reference to the NumPy matrix of the current image displayed on the screen. The format is 32-bit ARGB.
3. __getMemoryValue(address)__ Returns the 8-bit value found at the address on the Game Boy.
4. __setMemoryValue(address, value)__ Sets the 8-bit value at the address on the Game Boy.
5. __sendInput(event_list)__ Sends a list of `WindowEvent`s to the Game Boy.
6. __getMotherBoard()__ Returns a reference to the motherboard instance. This should be a last resort to get access to everything. _If you use this heavily, then open an issue, so it can be better supported._
7. __getSprite(index)__ Returns a sprite object, which makes the OAM data more presentable. See the available methods in `Source/PyBoy/BotSupport/Sprite.py`.
8. __getTileView(high)__ Returns a TileView object. If given the parameter `True` it will return a TileView for the 0x9C00-0x9FFF range, if the parameter is `False` it will provide a TileView for the 0x9800-0x9BFF range. The TileView has one method: get_tile(x, y), which returns the index of the tile.
9. __getScreenPosition()__ Returns a tuple of (SCX, SCY). These coordinates define the offset in the TileView from where the top-left corner of the screen is place. Note that the TileView defines 256x256 pixels, but the screen can only show 160x144 pixels. When the offset is closer to the edge than 160x144 pixels, the screen will wrap around and render from the opposite site of the TileView (see 7.4 Viewport in the [report](https://github.com/Baekalfen/PyBoy/raw/master/PyBoy.pdf)).

I can recommend to use the TileView instead of the screenbuffer, as they contain the index of the tiles on the screen. It is much simpler to look at the 8-bit value instead of recognizing the equivalent 8x8 pixels on the screen. Same goes for the sprite memory between 0xFE00 and 0xFEA0.

To see more details about this the display and the Game boy, have a look at the "Display" part of the [report](https://github.com/Baekalfen/PyBoy/raw/master/PyBoy.pdf), or refer to the [Pan Docs](http://bgb.bircd.org/pandocs.htm), which has clear-cut details about every conceivable topic.

For inspiration, here is a short demonstration of fetching the screen buffer:

    >>>> import PyBoy
    >>>> from PyBoy.GameWindow import SdlGameWindow as Window
    >>>> pyboy = PyBoy.PyBoy(Window(), "ROMs/TestRom.gb")
    324714   DEBUG    SDL GameWindow initialization
    324807   DEBUG    Scale: x1 (160, 144)
    325017   INFO     Cartridge type: 0x13 - MBC3, SRAM, Battery
    325017   INFO     Cartridge size: 64 ROM banks of 16KB, 16 RAM banks of 8KB
    325021   INFO     RAM loaded.

    >>>> pyboy.window.getScreenBuffer()
    array([[4207173, 4207173, 4207173, ..., 4207173, 4207173, 4207173],
           [4207173, 4207173, 4207173, ..., 4207173, 4207173, 4207173],
           [4207173, 4207173, 4207173, ..., 4207173, 4207173, 4207173],
           ...,
           [4207173, 4207173, 4207173, ..., 4207173, 4207173, 4207173],
           [4207173, 4207173, 4207173, ..., 4207173, 4207173, 4207173],
           [4207173, 4207173, 4207173, ..., 4207173, 4207173, 4207173]], dtype=uint32)
    >>>> for n in range(1000): # Move ahead the desired number of frames.
    ....     pyboy.tick()
    >>>> tv = pyboy.getTileView(True) # Get the TileView object for the window. Set False for the background.
    >>>> # The following prints out the indices of each tile in the window -- excluding sprites and the background!
    >>>> print "\n".join(["".join([str(tv.get_tile(x,y)).ljust(4) for x in range(32)]) for y in range(32)])
    1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1
    1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1
    1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1
    1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1
    0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
    0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
    0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
    0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
    0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   25  0   0   0   0   0   0   0   0   0   0   0   0   0
    0   0   0   0   0   0   0   0   0   0   0   0   0   2   6   11  16  20  26  0   0   0   0   0   0   0   0   0   0   0   0   0
    0   0   0   0   0   0   0   0   0   0   0   0   0   0   7   12  17  21  27  0   0   0   0   0   0   0   0   0   0   0   0   0
    0   0   0   0   0   0   0   0   0   0   0   0   0   3   8   13  18  22  28  0   0   0   0   0   0   0   0   0   0   0   0   0
    0   0   0   0   0   0   0   0   0   0   0   0   0   4   9   14  19  23  29  31  0   0   0   0   0   0   0   0   0   0   0   0
    0   0   0   0   0   0   0   0   0   0   0   0   0   5   10  15  1   24  30  32  0   0   0   0   0   0   0   0   0   0   0   0
    1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1
    1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1
    1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1
    1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1   1
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127
    127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127 127

If you ran the above code with the Pokemon Blue ROM loaded, you'll get something like the picture below. Notice the shape of Snorlax presented in the indices printed out above.

<p align="center">
<img src="https://github.com/Baekalfen/PyBoy/raw/master/README/DebugExample.png" width="640">
</p>

Compatibility
=============
See [results](Source/blargg.md) on Blargg's test ROMs. The list isn't complete, as the features in the missing tests, hasn't been implemented.

Contribute
==========
Any contribution is appreciated. The currently known errors are registered in the Issues tab. Feel free to take a swing at any one of them.

For the more major features, there are four that you can give a try:
* Sound
* Color
* Link Cable
* Unit tests and/or test ROM

If you want to implement something which is not on the list, feel free to do so anyway. If you want to merge it into our repo, then just send a pull request and we will have a look at it.

License
=======
Creative Commons BY-NC-SA 4.0
http://creativecommons.org/licenses/by-nc-sa/4.0/

