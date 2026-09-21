# Development

This page describes PyBoy's core structure, execution flow, plugins, and test
suites. For installing the build requirements, see [Getting
started](getting-started). For preparing a contribution, see
[Contributing](contributing).

## Running PyBoy during development

Run a ROM directly from the source tree with:

```sh
python3 -m pyboy path/to/rom.gb
```

The debug plugin can be enabled with:

```sh
python3 -m pyboy path/to/rom.gb --debug
```

Debug mode opens diagnostic views for inspecting emulator state and graphics.
Breakpoints can also be supplied at startup with the `--breakpoints` option.

Debug mode and debug logging are separate features. To enable verbose logging,
use:

```sh
python3 -m pyboy path/to/rom.gb --log-level DEBUG
```

A typical development loop is:

```text
change code -> make build -> run a ROM -> inspect the debugger or logs
```

See [Experimental and optional features](../experimental-and-optional-features)
for additional runtime options.

## Core architecture

The public `PyBoy` class drives the emulator, while the motherboard (`MB`) is
the center of the emulated hardware:

```text
PyBoy.tick()
    |
    v
Motherboard (MB)
    |
    +-- CPU
    +-- Cartridge and MBC
    +-- RAM
    +-- LCD and video
    +-- Timer
    +-- Sound
    +-- Serial
    +-- Input and interaction
    +-- Boot ROM
```

The motherboard is implemented in `pyboy/core/mb.py`. It creates and connects
the hardware components, routes memory accesses, coordinates interrupts and
DMA, and keeps the emulated hardware mode consistent between the components.

The main responsibilities of the core components are:

| Component | Responsibility |
| --- | --- |
| CPU | Executes instructions and advances the emulated cycle counter |
| Cartridge/MBC | Provides ROM and external RAM and handles bank switching |
| RAM | Stores work RAM, high RAM, and related memory state |
| LCD | Handles video timing, rendering, VRAM, and LCD interrupts |
| Timer | Updates the divider and timer registers and raises timer interrupts |
| Sound | Advances audio channels and produces sound samples |
| Serial | Handles serial transfers and serial interrupts |
| Interaction | Stores and processes Game Boy button input |
| Boot ROM | Provides startup behavior before cartridge execution |

## The tick-based execution model

PyBoy advances emulation through `PyBoy.tick()`. The motherboard performs the
lower-level emulation step, and the CPU runs until the required cycle target is
reached. Time-dependent hardware is then advanced through `tick(...)` methods
using the CPU cycle count.

The simplified flow is:

```text
PyBoy.tick()
  -> process input and plugin events
  -> MB.tick()
      -> CPU.tick(...)
      -> timer.tick(...)
      -> LCD.tick(...)
      -> sound.tick(...)
      -> handle interrupts and DMA
  -> run plugin post_tick() hooks
  -> render and limit the frame
```

The motherboard is the synchronization point. The CPU, timer, LCD, sound, and
other clocked components do not run independent frame loops; their `tick`
functions use the shared emulated time to stay synchronized. Components that
are primarily memory-mapped, such as cartridge banking and RAM, participate
through motherboard reads and writes as the CPU accesses them.

When debugging timing behavior, start at `MB.tick()` and then follow the
component tick method involved in the behavior being investigated.

## Plugin structure

Plugins live under `pyboy/plugins/`. The common interfaces are defined in
`base_plugin.py`, and `PluginManager` is responsible for creating enabled
plugins and dispatching their lifecycle methods.

Every plugin receives references to the `PyBoy` instance, the motherboard, and
the parsed command-line arguments. The base lifecycle methods are:

| Method | Purpose |
| --- | --- |
| `enabled()` | Determines whether the plugin is active |
| `handle_events(events)` | Consumes or transforms input and window events |
| `post_tick()` | Runs after the core has advanced |
| `window_title()` | Adds status text to the window title |
| `stop()` | Releases plugin resources |

The main plugin categories are:

- **Window plugins:** SDL2, OpenGL, GLFW, and null/headless windows
- **Feature plugins:** debugging, rewind, recording, screenshots, and
  auto-pause
- **Game wrappers:** game-specific helpers and state interpretation

A minimal plugin follows this shape:

```python
from pyboy.plugins.base_plugin import PyBoyPlugin


class ExamplePlugin(PyBoyPlugin):
    argv = []

    def enabled(self):
        return True

    def post_tick(self):
        pass
```

To add a real plugin:

1. Add the plugin module under `pyboy/plugins/`.
2. Define its configuration and `enabled()` behavior.
3. Register it through the plugin manager's registration points.
4. Add the required event and lifecycle dispatches.
5. Rebuild and test both enabled and disabled configurations.

Keep emulator hardware behavior in `pyboy/core/`. Use a plugin for optional
features, user interaction, rendering, recording, or game-specific behavior.
When investigating ordering issues, remember that plugins can process events
before emulation and receive `post_tick()` callbacks after the motherboard has
advanced.

## Running the test suites

PyBoy has separate tests for the compiled core and for the pure-Python source.
Run commands from the root of the repository.

### Compiled core tests: `tests/`

The tests in `tests/` exercise the compiled Cython implementation:

```sh
python3 -m pytest tests/ -n auto -v
```

Build PyBoy first with `make build`. The `-n auto` and `-v` options are
optional; the first uses all available CPU cores and the second enables
verbose output.

Some tests use test ROMs. ROMs placed in `test_roms/secrets/` are optional;
most permitted test ROMs are downloaded automatically. Commercial ROMs are not
distributed or downloaded.

### API and documentation doctests: `pyboy/`, `docs/`

The tests under `pyboy/` and the Markdown examples under `docs/` can run
together against the compiled extension:

```sh
make build
python3 -m pytest pyboy/ docs/ -n auto -v
```

The full local test workflow runs these doctests after building, followed by
the compiled emulator tests:

```text
make build
python3 -m pytest pyboy/ docs/ -n auto -v
python3 -m pytest tests/ -n auto -v
```

### Wiki Markdown examples

The test collector in `docs/conftest.py` collects Python examples from Wiki
Markdown pages under `docs/wiki/`. RST pages are not collected by this hook.
Run the examples after building PyBoy:

```sh
make build
python3 -m pytest docs/ -v
```
