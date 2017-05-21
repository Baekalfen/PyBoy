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
* [Contribute](#contribute)
* [License](#license)


Abstract
========
This project is covering an emulation of the Nintendo Game Boy (DMG-01) from 1989. The Game Boy has been emulated many times before, but this project will emulate it in the programming language Python 2.7. The implementation is not based on any existing emulator, but is made from scratch. The emulation has proven to be fast enough, to run software from cartridge dumps, with the same speed as the Game Boy. Most essential components of the Game Boy, are part of the emulation, but sound and serial port are not included in this project. The implementation runs in almost pure Python, but with dependencies for drawing graphics and getting user interactions through SDL2 and NumPy.

Starting the Emulator
=====================
*It should be noted, that the emulator is still under development. Eventhough games might work flawlessly now, be prepared, that saved games may be lost without any further notice.*

CPython is no where fast enough to run the emulator (see [Report.pdf](https://github.com/Baekalfen/PyBoy/raw/master/PyBoy.pdf) about performance). It is therefore required to use PyPy.

The code has a few dependencies, but it should be fairly easy to get it up and running. The code is developed on macOS, but has been tested to run on Ubuntu 16.04 and Windows 10.

macOS
-----
The easiest way to get started, is to first install [brew](https://www.brew.sh).

When brew is installed, the depencencies can be installed with the following commands in the terminal:

    brew update
    brew install pypy sdl2
    brew link sdl2
    brew install sdl2 sdl2_gfx sdl2_image

    pip_pypy install git+https://bitbucket.org/pypy/numpy.git
    pip_pypy install hg+https://bitbucket.org/marcusva/py-sdl2


Ubuntu/Linux
------------
Ubuntu has some problems installing PyPy in parallel with the system version of CPython. Therefore, we will install the PyPy version of NumPy and PySDL2 in a virtualenv.

Git and Mercurial is not strictly needed for the emulator. You can choose not to install them, if you download and install PySDL2 and NumPy manually.

    sudo apt update
    sudo apt install git mercurial
    sudo apt install pypy pypy-dev virtualenv libsdl2-dev

Now move to the `PyBoy/Source` directory before creating the virtual environment:

    virtualenv . -p `which pypy`
    source ./bin/activate

    pip install git+https://bitbucket.org/pypy/numpy.git
    pip install hg+https://bitbucket.org/marcusva/py-sdl2

Windows
-------
First, install Git, Mercurial, vcredist and VCForPython27:

* https://git-scm.com/download/win
* https://www.mercurial-scm.org/wiki/Download#Windows
* https://www.microsoft.com/en-us/download/details.aspx?id=5582
* https://www.microsoft.com/en-us/download/details.aspx?id=44266

Then download the latest Pypy 32-bit (64-bit pre-built isn't available). At the time of writing the newest version is `pypy2-v5.7.1-win32.zip`:

* https://bitbucket.org/pypy/pypy/downloads/

Unzip it, and place the contents somewhere like: `C:\pypy2\`.

Search from "Edit the system environment varibles" from the start menu. Add `C:\pypy2;` at the beginning of the value of the `Path` variable.

Start a Command Prompt and run the following:

    pypy -m ensurepip
    pypy -m pip install -U pip wheel
    pypy -m pip install git+https://bitbucket.org/pypy/numpy.git
    pypy -m pip install hg+https://bitbucket.org/marcusva/py-sdl2

Download SDL2 Runtime Binaries for 32-bit Windows:

* https://www.libsdl.org/download-2.0.php

Place it somewhere you can locate it. I chose `C:\pypy2\SDL2.dll`. Then set the variable from the Command Prompt.

    set PYSDL2_DLL_PATH=C:\pypy2\SDL2.dll


Setup and Run
-------------
Now, create a directory at `Source/ROMs` and place your ROMs in this directory -- which you of course dumped yourself with [PyBoyCartridge](https://github.com/Baekalfen/PyBoyCartridge)

Then run `pypy main.py` from the `Source` directory and choose a ROM to start. You can choose to run as `pypy -OO main.py` to remove all the debugging windows.

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

