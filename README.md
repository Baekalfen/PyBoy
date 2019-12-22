<p align="center">
<img src="README/pyboy.svg" width="480">
</p>

__If you have any questions, or just want to chat, [join us on Discord](https://discord.gg/Zrf2nyH).__


It is highly recommended to read the [report](https://github.com/Baekalfen/PyBoy/raw/master/PyBoy.pdf) to get a light introduction to Game Boy emulation. The report is relevant, eventhough you want to contribute to another emulator, or create your own.

If you've read the report and want more explicit details, have a look at the [Pan Docs](http://bgb.bircd.org/pandocs.htm).

__If you are looking to make a bot or AI__, you can find all the external components in the [PyBoy Documentation](https://baekalfen.github.io/PyBoy/index.html). There is also a short example or our Wiki page [Scripts, AI and Bots](https://github.com/Baekalfen/PyBoy/wiki/Scripts,-AI-and-Bots). If more features are needed, or if you find a bug, don't hesitate to make an issue here on GitHub, or write on our [Discord channel](https://discord.gg/Zrf2nyH).

<p align="center">
<img src="https://github.com/Baekalfen/PyBoy/raw/master/README/1.gif" width="320">
<img src="https://github.com/Baekalfen/PyBoy/raw/master/README/2.gif" width="320"><br>
<img src="https://github.com/Baekalfen/PyBoy/raw/master/README/3.gif" width="320">
<img src="https://github.com/Baekalfen/PyBoy/raw/master/README/4.gif" width="320">
</p>

Installation
============
We have now moved away from PyPy, and PyBoy fully supports CPython ("regular Python"), by the use of Cython (Python-to-C compiler). Performance has also increased dramatically.

The code base is still pure Python, which means it will still run in CPython and PyPy (although slowly). Cython is an addition, where we can compile the code to run 100-200 times faster.

**To get started, look at the [installation instructions](https://github.com/Baekalfen/PyBoy/wiki/Installation).** We support: macOS, Raspberry Pi (Raspbian) and Linux (Ubuntu).

At the Wiki page, you will also find out how to interface with PyBoy from your own project: [Wiki](https://github.com/Baekalfen/PyBoy/wiki).


Contibutors
===========

Thanks to all the people, who have contributed to the project!

Original Developers
-------------------

 * Asger Anders Lund Hansen - [AsgerLundHansen](https://github.com/AsgerLundHansen)
 * Mads Ynddal - [baekalfen](https://github.com/Baekalfen)
 * Troels Ynddal - [troelsy](https://github.com/troelsy)

GitHub Contributors
-------------------

 * Kristian Sims - [krs013](https://github.com/krs013)
 * Thomas Li Fredriksen - [thomafred](https://github.com/thomafred)
 * Florian Katenbrink - [FKatenbrink](https://github.com/FKatenbrink)
 * Liz - [stillinbeta](https://github.com/stillinbeta)

Student Projects
----------------

 * __Rewind Time:__ Jonas Flach-Jensen - [thejomas](https://github.com/thejomas)
 * __Link Cable:__ Jacob Olsen - [JacobO1](https://github.com/JacobO1)

Contribute
==========
Any contribution is appreciated. The currently known errors are registered in the Issues tab. Feel free to take a swing at any one of them.

For the more major features, there are the following that you can give a try. They are also described in more detail in the [project list](https://github.com/Baekalfen/PyBoy/raw/master/Projects/Projects.pdf):
* Sound
* Color
* Link Cable
* _(Experimental)_ AI - use the `botsupport` to train a neural network
* _(Experimental)_ Bot Support - make wrappers for popular games

If you want to implement something which is not on the list, feel free to do so anyway. If you want to merge it into our repo, then just send a pull request and we will have a look at it.

License
=======
Creative Commons BY-NC-SA 4.0
http://creativecommons.org/licenses/by-nc-sa/4.0/

