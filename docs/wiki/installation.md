# Installation

## Introduction
*It should be noted that the emulator is still under development. Even though games might work flawlessly now, be warned that saved games may be lost without any notice.*

**Note:** If you have any problems, please feel free to let us know or [ask for help on Discord](https://discord.gg/wUbag3KNqQ)! We try our best to keep the instructions up-to-date, but if something seems wrong or outdated please let us know.


## macOS
The easiest way to get started is to first install [brew](https://brew.sh).

When brew is installed, install Python 3 with the following commands in the terminal. Open a terminal and type in the following, line by line:

    > brew update
    > brew install python3

Now, you can simply install from PyPi:

    > python3 -m pip install --upgrade pip
    > python3 -m pip install pyboy

Note: If `pip` tries to build Pillow from source, you may get an error. `brew install jpeg` seems to fix this.

You're now ready to play some games! Continue to {ref}`Starting PyBoy <starting-pyboy>`.


## Linux (Ubuntu/Raspberry Pi OS)
Ubuntu's system version of Python is Python 2.7, so you can install the requirements for Python 3 without messing anything up. Open a terminal and type in the following, line by line:

    > sudo apt update
    > sudo apt install python3 python3-pip

Thanks to the **piwheels** project, ARM-compatible wheels of PyBoy are available at https://www.piwheels.org/project/pyboy/, and by default `pip3` will use these wheels on Raspberry Pi OS (if not, check `/etc/pip.conf` or see https://www.piwheels.org/faq.html).

Now, you can simply install from PyPi:

    > python3 -m pip install --upgrade pip
    > python3 -m pip install pyboy

You're now ready to play some games! Continue to {ref}`Starting PyBoy <starting-pyboy>`.


## Windows (64-bit)

First of you need to install Python 3. Follow the link "Latest Python 3 Release - Python 3.x.x", and install it: [Python 3](https://www.python.org/downloads/windows/). At the time of writing, this is 3.14.3.

Open a PowerShell and simply install from PyPi:

    > py -m pip install --upgrade pip
    > py -m pip install wheel setuptools
    > py -m pip install pyboy

You're now ready to play some games! Continue to {ref}`Starting PyBoy <starting-pyboy>`.

### Building from Source on Windows

If you want to build PyBoy from source, you will need to install the "Build Tools for Visual Studio" from [Microsoft](https://visualstudio.microsoft.com/downloads). The downloaded `.exe` will run a program called "Visual Studio Installer" that allows you to install or uninstall various components of Visual Studio. Run it and make sure to check the box for "Desktop development with C++."

After this is done, install the requirements and build as usual (`python setup.py build_ext [-i]`).

### Windows Subsystem for Linux

With an updated WSL 2, PyBoy can run on compatible Linux subsystems. The minimal steps to do this are as follows:

 * Update WSL to the latest version: `wsl --update`. There may be an extra step to upgrade from WSL 1 to WSL 2 if you have used WSL 1 before.
 * If you haven't already, create the distribution, e.g. `wsl --install Ubuntu-22.04` and follow the prompts to create a user account.
 * Update Linux packages, e.g. `sudo apt update && sudo apt upgrade`
 * Install support libraries for video and sound: `sudo apt install libgl1 libpulse0`
 * Optionally, install `sudo apt python3.10-venv` and create and activate a virtual environment: `python3 -m venv pyboy-venv` and `source pyboy-venv/bin/activate`
 * Install pyboy: `pip install pyboy`

#### X forwarding for WSL 1

It has been shown that a WSL 1 environment is sufficient when used with a X display server program like Xming or VcXsrv. Some notes from this process:

 * You will need to indicate that an X server is available by defining the `DISPLAY` environment variable. On WSL 1 `export DISPLAY=:0` seems to be sufficient, while on WSL 2 it seems the value must either be `export DISPLAY=$(hostname).local:0.0` or `export DISPLAY=<windows-host-local-IP-address>:0.0`.
 * `sudo apt install freeglut3` is still a requirement
 * When using Xming or VcXsrv it is necessary to `export LIBGL_ALWAYS_INDIRECT=1`

(starting-pyboy)=
## Starting PyBoy
Now, find your ROM dumps, which you of course dumped yourself with [PyBoyCartridge](https://github.com/Baekalfen/PyBoyCartridge).

Then run `python3 -m pyboy path/to/rom.gb` from the root directory of the PyBoy Git repo. If you chose to install PyBoy on your system, you can do `pyboy path/to/rom.gb` from any directory.

For more advanced use, you can use `python3 -m pyboy --help` to find available options. For example: `python3 -m pyboy -w SDL2 ROMs/game.rom`. See more in the section [experimental features](experimental-and-optional-features).

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

To enable rewind, see more in the section [experimental features](experimental-and-optional-features).


## Building from Source
If you want to build from source, follow the instructions above for your platform, but don't do `pip install pyboy`. If PyBoy is already installed, make sure to uninstall it with `pip uninstall pyboy`. Run the uninstall more than once, to make sure you don't have multiple versions installed.

A part of the build process will create the custom boot ROM and default example ROM. For this, you'll need to [install RGBDS]( https://rgbds.gbdev.io/install)

Cython will also require a compiler on your system. See [Installing Cython](https://cython.readthedocs.io/en/stable/src/quickstart/install.html).

Then type the following lines in your terminal.

    > python3 -m pip install -r requirements.txt
    > make build

You can also install PyBoy as a package on your system, so you can include it in other projects using:

    > python3 -m pip install .

If pyboy is running slowly after the line above, make sure to navigate to a different directory than the PyBoy source code. Your system might select the non-compiled version of `pyboy` in the directory over the compiled version installed on the system.

When you change the code, you'll have to run `make build` or `python3 -m pip install .` again. Sometimes, it's necessary run `make clean` to clear any files compiled on older code.
