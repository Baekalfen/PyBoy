Table of Contents
=================

 * [Introduction](#introduction)
 * [macOS](#macos)
 * [Linux (Ubuntu)](#linux-ubuntu)
 * [Raspberry Pi (Raspbian)](#raspberry-pi-raspbian)
 * [Windows 10 (64-bit)](#windows-10-64-bit)
 * [Windows on MSYS2 and mingw-w64](#windows-on-msys2-and-mingw-w64)
 * [Starting PyBoy](#starting-pyboy)
 * [Building from Source](#building-from-source-1)

Introduction
============
*It should be noted that the emulator is still under development. Even though games might work flawlessly now, be warned that saved games may be lost without any notice.*

**Note:** If you have any problems, please feel free to let us know or [ask for help on Discord](https://discord.gg/Zrf2nyH)! We try our best to keep the instructions up-to-date, but if something seems wrong or outdated please let us know.

macOS
=====
The easiest way to get started is to first install [brew](https://brew.sh).

When brew is installed, the dependencies can be installed with the following commands in the terminal. Assuming that you have cloned the git repo and navigated to the root-dir:

    brew update
    brew install python3 sdl2

Now, you can simply install from PyPi:

    python3 -m pip install --upgrade pip
    python3 -m pip install pyboy

You're now ready to play some games! Continue to [Starting PyBoy](#starting-pyboy).


Linux (Ubuntu)
============
Ubuntu's system version of Python is Python 2.7, so you can install the requirements for Python 3 without messing anything up. If you want to make a virtual environment, you will also need to install the `python3-venv` package.

    sudo apt update
    sudo apt install python3 python3-pip python3-dev libsdl2-dev build-essential

Now, you can simply install from PyPi:

    python3 -m pip install --upgrade pip
    python3 -m pip install pyboy

You're now ready to play some games! Continue to [Starting PyBoy](#starting-pyboy).


Raspberry Pi (Raspbian)
=====================
*We assume that you have downloaded the repository already.*

The instructions for Raspbian are almost the same as the Ubuntu/Linux instructions above. The only difference, is the need to build SDL2 from source, and modify the CFLAGS accordingly.

The instructions has been tested on a Raspberry Pi 3 model B+, running a default configuration of Raspbian Stretch Lite.

To download, build and install the newest version of SDL2 (2.0.9 at the time of writing), run the following commands:

    wget https://www.libsdl.org/release/SDL2-2.0.9.tar.gz
    tar zxvf SDL2-2.0.9.tar.gz
    cd SDL2-2.0.9 && mkdir build && cd build

    ../configure --disable-pulseaudio --disable-esd --disable-video-mir --disable-video-wayland --disable-video-x11 --disable-video-opengl
    make -j 4
    sudo make install

If everything went well, we are ready to build PyBoy. We can compile PyBoy with the following:

    sudo apt update
    sudo apt install python3 python3-pip python3-dev build-essential

    python3 -m pip install --upgrade pip
    python3 -m pip install cython pysdl2 numpy Pillow
    export CFLAGS=$(sdl2-config --cflags --libs)
    python3 setup.py build_ext --inplace -I$(python3 -c 'import numpy; print(numpy.get_include())')

You're now ready to play some games! Continue to [Starting PyBoy](#starting-pyboy).

Windows 10 (64-bit)
===================================================

First of you need to install Python 3. Press Start and find "Windows PowerShell", then press enter. In the PowerShell, type the following:

    (New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.7.6/python-3.7.6-amd64.exe', 'python-3.7.6-amd64.exe')
    python-3.7.6-amd64.exe /passive InstallAllUsers=1 PrependPath=1

You may need to restart the PowerShell before the `python` command becomes available.

Then you need to install SDL2. There is no canonical place for it in Windows 10 but you will need the location for the next step. For this tutorial we will place it in `C:\SDL2\`.

    (New-Object Net.WebClient).DownloadFile('https://www.libsdl.org/release/SDL2-devel-2.0.10-VC.zip', 'SDL2-devel-2.0.10-VC.zip')
    Expand-Archive -Force 'SDL2-devel-2.0.10-VC.zip' C:\SDL2\
    setx PYSDL2_DLL_PATH C:\SDL2\SDL2-2.0.10\lib\x64
    setx PATH "%PATH%;C:\SDL2\SDL2-2.0.10\lib\x64"

Now, you can simply install from PyPi:

    python -m pip install --upgrade --user pip
    python -m pip install --user pyboy

You're now ready to play some games! Continue to [Starting PyBoy](#starting-pyboy).


Building from Source
--------------------

If you have to build from source, you will need to install the "Visual Studio Build Tools" with the "C++ build tools".

The installer can be found at https://visualstudio.microsoft.com/downloads/ under "Tools for Visual Studio 2019." When run, it will install a program onto your computer called "Visual Studio Installer" that allows you to install or uninstall various components of Visual Studio. Run it and make sure to check the box for "C++ build tools."


Windows on MSYS2 and mingw-w64
==========================================

Press Start and find "Windows PowerShell", then press enter. Then install `msys2-x86_64` from https://www.msys2.org or type the lines below into the PowerShell:

    (New-Object Net.WebClient).DownloadFile('http://repo.msys2.org/distrib/x86_64/msys2-x86_64-20190524.exe', 'msys2-x86_64-20190524.exe')
    msys2-x86_64-20190524.exe

Close the MSYS2 terminal, if it opens automatically after installing.

Press Start and search for "MSYS2 MinGW 64-bit". Type the following to install the needed packages. You can close the window if prompted to, and continue with the next command.

    pacman -Syu
    pacman -S make mingw-w64-x86_64-gcc mingw-w64-x86_64-SDL2 mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-pip mingw-w64-x86_64-python3-numpy mingw-w64-x86_64-python3-pillow git

Now, you can simply install from PyPi:

    python3 -m pip install --upgrade pip
    python3 -m pip install pyboy

You're now ready to play some games! Continue to [Starting PyBoy](#starting-pyboy).

**Note 1:** MSYS2 creates a fake home folder at `C:\msys64\home\USERNAME` and will open new terminals in that directory. If you wish to navigate to your Windows filesystem, it can be found in the terminal as `/c/`, so `/c/Users/USERNAME/` is your Windows home folder. You can also just do everything in the MSYS2 home folder.

**Note 2:** If you wish to use a virtual environment, be sure to use the `--system-site-packages` flag when creating the virtual environment, e.g.: `python -m venv --system-site-packages pyboy-venv`. Activate the environment with `source pyboy-venv/bin/activate`. Also, `pip` will encourage you to update `pip`, which you can do with `pip install -U pip`, but this may report an error. The error can be ignored and the upgrade does succeed, but the old version of `pip` is left in `pyboy-venv/lib/python3.7/site-packages/` as two files renamed to `~ip` and `~ip-19.0.3.dist-info`, which can be deleted to prevent `pip` from warning you whenever it tries to parse them.


Starting PyBoy
==============
Now, find your ROM dumps, which you of course dumped yourself with [PyBoyCartridge](https://github.com/Baekalfen/PyBoyCartridge).

Then run `python3 -m pyboy path/to/rom.gb` from the root directory of the PyBoy Git repo. If you chose to install PyBoy on your system, you can do `pyboy path/to/rom.gb` from any directory.

For more advanced use, you can use `python3 -m pyboy -w [Window] [ROM path]`. For example: `python3 -m pyboy -w SDL2 ROMs/game.rom`. See more in the section [experimental features](https://github.com/Baekalfen/PyBoy/wiki/Experimental-and-optional-features).

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
| ,            | Rewind backwards        |
| .            | Rewind forward          |

To enable rewind, see more in the section [experimental features](https://github.com/Baekalfen/PyBoy/wiki/Experimental-and-optional-features).


Building from Source
====================
If you want to build from source, follow the instructions above for your platform, but don't do `pip install pyboy`. If PyBoy is already installed, make sure to uninstall it with `pip uninstall pyboy`. Run the uninstall more than once, to make sure you don't have multiple versions installed.

Then type the following lines in your terminal.

    python3 -m pip install -r requirements.txt
    python3 setup.py build_ext --inplace

You can also install PyBoy as a package on your system, so you can include it in other projects using:

    python3 -m pip install .

If pyboy is running slowly after the line above, make sure to navigate to a different directory than the PyBoy source code. Your system might select the non-compiled version of `pyboy` in the directory over the compiled version installed on the system.
