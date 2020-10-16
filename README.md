<p align="center">
<img src="README/pyboy.svg" width="480">
</p>

__If you have any questions, or just want to chat, [join us on Discord](https://discord.gg/Zrf2nyH).__


It is highly recommended to read the [report](https://github.com/Baekalfen/PyBoy/raw/master/PyBoy.pdf) to get a light introduction to Game Boy emulation. _But do be aware, that the Python implementation has changed a lot_. The report is relevant, eventhough you want to contribute to another emulator, or create your own.

If you've read the report and want more explicit details, have a look at the [Pan Docs](http://bgb.bircd.org/pandocs.htm).

__If you are looking to make a bot or AI__, you can find all the external components in the [PyBoy Documentation](https://baekalfen.github.io/PyBoy/index.html). There is also a short example on our Wiki page [Scripts, AI and Bots](https://github.com/Baekalfen/PyBoy/wiki/Scripts,-AI-and-Bots) as well as in the [examples directory](https://github.com/Baekalfen/PyBoy/tree/master/examples). If more features are needed, or if you find a bug, don't hesitate to make an issue here on GitHub, or write on our [Discord channel](https://discord.gg/Zrf2nyH).

<p align="center">
<img src="https://github.com/Baekalfen/PyBoy/raw/master/README/1.gif" width="320">
<img src="https://github.com/Baekalfen/PyBoy/raw/master/README/2.gif" width="320"><br>
<img src="https://github.com/Baekalfen/PyBoy/raw/master/README/3.gif" width="320">
<img src="https://github.com/Baekalfen/PyBoy/raw/master/README/4.gif" width="320">
</p>

Installation
============
The instructions are simple, if you already have a functioning Python environment on your machine.

 1. Install SDL2 through your package manager:
    - Ubuntu: __`sudo apt install libsdl2-dev`__
    - Fedora: __`sudo dnf install SDL2-devel`__
    - macOS: __`brew install sdl2`__

 2. Install PyBoy using __`pip install pyboy`__ (add __` --user`__ if your system asks)

Now you're ready! Either use PyBoy directly from the terminal __`$ pyboy file.rom`__ or use it in your Python scripts:
```python
from pyboy import PyBoy
pyboy = PyBoy('ROMs/gamerom.gb')
while not pyboy.tick():
    pass
```

If you need more details, or if you need to compile from source, check out the detailed [installation instructions](https://github.com/Baekalfen/PyBoy/wiki/Installation). We support: macOS, Raspberry Pi (Raspbian), Linux (Ubuntu), and Windows 10.

At the Wiki page, you will also find out how to interface with PyBoy from your own project: [Wiki](https://github.com/Baekalfen/PyBoy/wiki).


Contributors
============

Thanks to all the people, who have contributed to the project!

Original Developers
-------------------

 * Asger Anders Lund Hansen - [AsgerLundHansen](https://github.com/AsgerLundHansen)
 * Mads Ynddal - [baekalfen](https://github.com/Baekalfen)
 * Troels Ynddal - [troelsy](https://github.com/troelsy)

GitHub Collaborators
--------------------

 * Kristian Sims - [krs013](https://github.com/krs013)

Student Projects
----------------

 * __Rewind Time:__ Jacob Olsen - [JacobO1](https://github.com/JacobO1)
 * __Link Cable:__ Jonas Flach-Jensen - [thejomas](https://github.com/thejomas)

Contribute
==========
Any contribution is appreciated. The currently known errors are registered in the Issues tab. Feel free to take a swing at any one of them.

For the more major features, there are the following that you can give a try. They are also described in more detail in the [project list](https://github.com/Baekalfen/PyBoy/raw/master/Projects/Projects.pdf):
* Color
* Link Cable
* _(Experimental)_ AI - use the `botsupport` or game wrappers to train a neural network
* _(Experimental)_ Game Wrappers - make wrappers for popular games

If you want to implement something which is not on the list, feel free to do so anyway. If you want to merge it into our repo, then just send a pull request and we will have a look at it.
