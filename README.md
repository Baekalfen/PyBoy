<p align="center">
<img src="extras/README/pyboy.svg" width="480">
</p>

__If you have any questions, or just want to chat, [join us on Discord](https://discord.gg/Zrf2nyH).__


It is highly recommended to read the [report](https://github.com/Baekalfen/PyBoy/raw/master/extras/PyBoy.pdf) to get a light introduction to Game Boy emulation. _But do be aware, that the Python implementation has changed a lot_. The report is relevant, eventhough you want to contribute to another emulator, or create your own.

If you've read the report and want more explicit details, have a look at the [Pan Docs](http://bgb.bircd.org/pandocs.htm).

__If you are looking to make a bot or AI__, you can find all the external components in the [PyBoy Documentation](https://baekalfen.github.io/PyBoy/index.html). There is also a short example on our Wiki page [Scripts, AI and Bots](https://github.com/Baekalfen/PyBoy/wiki/Scripts,-AI-and-Bots) as well as in the [examples directory](https://github.com/Baekalfen/PyBoy/tree/master/extras/examples). If more features are needed, or if you find a bug, don't hesitate to make an issue here on GitHub, or post on our [Discord channel](https://discord.gg/Zrf2nyH).


<!---
Generate GIF with the layout and captions
-->
<table>
  <tbody>
    <tr>
      <td colspan="3">
<div align="center">
<img src="extras/README/1.gif" width="400"><br>
</div>
      </td>
    </tr>
    <tr>
      <td align="center">Rewind any game<br>
      </td>
      <td align="center"><a href=https://github.com/uiucanh/tetris>Beat world records</a><br>
      </td>
      <td align="center"><a href=https://github.com/lixado/PyBoy-RL>Train with Reinforcement Learning</a><br>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="extras/README/5.gif" width="200">
      </td>
      <td align="center">
        <img src="extras/README/7.gif" width="200">
      </td>
      <td align="center">
        <img src="extras/README/6.gif" width="200">
      </td>
    </tr>
  </tbody>
</table>


Installation
============
The instructions are simple if you already have a functioning Python environment on your machine.

 1. Install PyBoy using __`pip install pyboy`__ (add __` --user`__ if your system asks)
 2. If your system isn't supported by [pysdl2-dll](https://pypi.org/project/pysdl2-dll/), you'll need to install SDL2 from your package manager.

If you need more details, or if you need to compile from source, check out the detailed [installation instructions](https://github.com/Baekalfen/PyBoy/wiki/Installation). We support: macOS, Raspberry Pi (Raspbian), Linux (Ubuntu), and Windows 10.

Now you're ready! Either use PyBoy directly from the terminal __`$ pyboy file.rom`__ or use it in your Python scripts:
```python
from pyboy import PyBoy
pyboy = PyBoy('ROMs/gamerom.gb')
while pyboy.tick(1, True):
    pass
pyboy.stop()
```

<!-- Or using the context manager:
```python
from pyboy import PyBoy
with PyBoy('ROMs/gamerom.gb') as pyboy:
    while pyboy.tick(1, True):
        pass
``` -->

When the emulator is running, you can easily access [PyBoy's API](https://baekalfen.github.io/PyBoy/index.html):
```python
pyboy.button('down')
pyboy.button('a')
some_value = pyboy.memory[0xC345]

pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
pyboy.tick() # Process one frame to let the game register the input
pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)

pil_image = pyboy.screen_image()
pyboy.tick(1, True)
pil_image.save('screenshot.png')
```

The Wiki shows how to interface with PyBoy from your own project: [Wiki](https://github.com/Baekalfen/PyBoy/wiki).


Contributors
============

Thanks to all the people who have contributed to the project!

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
 * __Game Boy Color:__ Christian Marslev and Jonas Grønborg - [CKuke](https://github.com/CKuke) and [kaff3](https://github.com/kaff3)

Contribute
==========
Any contribution is appreciated. The currently known problems are tracked in the Issues tab. Feel free to take a swing at any one of them.

For the more major features, there are the following that you can give a try. They are also described in more detail in the [project list in the Wiki](https://github.com/Baekalfen/PyBoy/wiki/Student-Projects):
* Link Cable
* _(Experimental)_ AI - use the `botsupport` or game wrappers to train a neural network
* _(Experimental)_ Game Wrappers - make wrappers for popular games

If you want to implement something which is not on the list, feel free to do so anyway. If you want to merge it into our repo, then just send a pull request and we will have a look at it.
