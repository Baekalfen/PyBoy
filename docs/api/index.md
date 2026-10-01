(api-reference)=
# API reference

The API reference documents the supported Python-facing interface. Internal
emulation components and platform-specific window implementations are
intentionally excluded.

Technically, the API mirrors the main parts of the Game Boy hardware: the
CPU and address space, graphics, audio, cartridge hardware, and input.
Each page explains the hardware concept before listing the corresponding
Python objects and methods.

Use the {class}`PyBoy <pyboy.PyBoy>` page to start and advance an emulation,
then use the memory, register, graphics, sound, and utility APIs to inspect or
control it.

```{toctree}
:maxdepth: 2

pyboy
memory_view
register_file
memory_scanner
gameshark
rumble
screen
sound
sprite
tile
tilemap
constants
utils
../wiki/migrating-from-v1-to-v2
```
