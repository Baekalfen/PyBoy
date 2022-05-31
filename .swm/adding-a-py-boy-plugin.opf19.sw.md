---
id: opf19
name: Adding a Py Boy Plugin
file_version: 1.0.2
app_version: 0.8.7-0
file_blobs:
  pyboy/plugins/manager.py: 20ec1b8e99c3d650beb1127c6f1e4b62d005cbd5
  pyboy/plugins/auto_pause.pxd: c2d27a79fb0b03b86b5581bbcce43c3135521e17
  pyboy/plugins/manager.pxd: 8ad52307117ac167f4bbb307f430306e81f04918
  pyboy/plugins/manager_gen.py: 4710abdf4dc32a318b1b4a508d35d3415ccb800c
  pyboy/plugins/base_plugin.pxd: 851a5818127642bdf3222316720ef5c5b5c3049c
  pyboy/plugins/game_wrapper_tetris.pxd: de4d315fea936f0d1c1ee135fea8eb6e3ca98d64
  pyboy/plugins/game_wrapper_tetris.py: fb8f83731c76b06f5dfab8ec7cf4089ade2ada90
  pyboy/plugins/game_wrapper_super_mario_land.pxd: d77d3e999baf94353d6f8bc6b8b5220c5bf23f10
  pyboy/plugins/game_wrapper_super_mario_land.py: b97be5664c9a7c42c0e4599bdf36a4f6b42c04a4
  pyboy/plugins/debug.pxd: 8b470ee75b64b55f30d1ca61de6f64eac8586d98
  pyboy/plugins/debug.py: 519ed87a8ec670b2cf473d6f2d83906fddbfa7d7
---

Understanding Py Boy Plugins, how they work, and how to add new ones, is important - and this document will describe just that.

A Py Boy Plugin is a way to add a plugin to our emulator

Some examples of `PyBoyPlugin`[<sup id="Z12255h">↓</sup>](#f-Z12255h)s are `GameWrapperTetris`[<sup id="1MSrdj">↓</sup>](#f-1MSrdj), `GameWrapperTetris`[<sup id="3Wzwc">↓</sup>](#f-3Wzwc), `GameWrapperSuperMarioLand`[<sup id="1l8il3">↓</sup>](#f-1l8il3), and `GameWrapperSuperMarioLand`[<sup id="ZUAYk4">↓</sup>](#f-ZUAYk4). Note: some of these examples inherit indirectly from `PyBoyPlugin`[<sup id="Z12255h">↓</sup>](#f-Z12255h).

<br/>

## Other base classes to consider
Most instances of `PyBoyPlugin`[<sup id="Z12255h">↓</sup>](#f-Z12255h) inherit directly from `PyBoyPlugin`[<sup id="Z12255h">↓</sup>](#f-Z12255h), but you might want to consider the following base classes as well:

- `PyBoyWindowPlugin`[<sup id="ZGfdrw">↓</sup>](#f-ZGfdrw): Base class of all {Explain this base class}
    - e.g. `Debug`[<sup id="ZcEerc">↓</sup>](#f-ZcEerc).
- `PyBoyGameWrapper`[<sup id="2ncaJG">↓</sup>](#f-2ncaJG): Inherit from this when {Explain this base class}
    - e.g. `GameWrapperTetris`[<sup id="1MSrdj">↓</sup>](#f-1MSrdj).
- `BaseDebugWindow`[<sup id="3qaNn">↓</sup>](#f-3qaNn): Suitable base for {Explain this base class}
    - e.g. `TileViewWindow`[<sup id="ZoqyY2">↓</sup>](#f-ZoqyY2).
- `BaseDebugWindow`[<sup id="Z1Xxa8r">↓</sup>](#f-Z1Xxa8r): Base class of all {Explain this base class}
    - e.g. `TileViewWindow`[<sup id="halMj">↓</sup>](#f-halMj).

In this document we demonstrate inheriting from `PyBoyPlugin`[<sup id="Z12255h">↓</sup>](#f-Z12255h) as it is the most common.

<br/>

## TL;DR - How to Add a `PyBoyPlugin`[<sup id="Z12255h">↓</sup>](#f-Z12255h)

1. Create a new class inheriting from `PyBoyPlugin`[<sup id="Z12255h">↓</sup>](#f-Z12255h)&nbsp;
   - Place the file under [[sym:./pyboy/plugins({"type":"path","text":"pyboy/plugins","path":"pyboy/plugins"})]],
     e.g. `AutoPause`[<sup id="29Dn9T">↓</sup>](#f-29Dn9T) is defined in [[sym:./pyboy/plugins/auto_pause.pxd({"type":"path","text":"pyboy/plugins/auto_pause.pxd","path":"pyboy/plugins/auto_pause.pxd"})]].
3. Update [[sym:./pyboy/plugins/manager.pxd({"type":"path","text":"pyboy/plugins/manager.pxd","path":"pyboy/plugins/manager.pxd"})]].
3. Update [[sym:./pyboy/plugins/manager.py({"type":"path","text":"pyboy/plugins/manager.py","path":"pyboy/plugins/manager.py"})]].
3. Update [[sym:./pyboy/plugins/manager_gen.py({"type":"path","text":"pyboy/plugins/manager_gen.py","path":"pyboy/plugins/manager_gen.py"})]].
4. **Profit** 💰

<br/>

## Example Walkthrough - `AutoPause`[<sup id="29Dn9T">↓</sup>](#f-29Dn9T)
We'll follow the implementation of `AutoPause`[<sup id="29Dn9T">↓</sup>](#f-29Dn9T) for this example.

An `AutoPause`[<sup id="29Dn9T">↓</sup>](#f-29Dn9T) is {Explain what AutoPause is and how it works with the Py Boy Plugin interface}

<br/>

### `AutoPause`[<sup id="29Dn9T">↓</sup>](#f-29Dn9T) Usage Example
For example, this is how `AutoPause`[<sup id="29Dn9T">↓</sup>](#f-29Dn9T) can be used:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 pyboy/plugins/manager.py
```python
⬜ 58             self.debug_enabled = self.debug.enabled()
⬜ 59             self.disable_input = DisableInput(pyboy, mb, pyboy_argv)
⬜ 60             self.disable_input_enabled = self.disable_input.enabled()
🟩 61             self.auto_pause = AutoPause(pyboy, mb, pyboy_argv)
⬜ 62             self.auto_pause_enabled = self.auto_pause.enabled()
⬜ 63             self.record_replay = RecordReplay(pyboy, mb, pyboy_argv)
⬜ 64             self.record_replay_enabled = self.record_replay.enabled()
```

<br/>

## Steps to Adding a new `PyBoyPlugin`[<sup id="Z12255h">↓</sup>](#f-Z12255h)

<br/>

### 1\. Inherit from `PyBoyPlugin`[<sup id="Z12255h">↓</sup>](#f-Z12255h).
All `PyBoyPlugin`[<sup id="Z12255h">↓</sup>](#f-Z12255h)s are defined in files under [[sym:./pyboy/plugins({"type":"path","text":"pyboy/plugins","path":"pyboy/plugins"})]].

<br/>

We first need to define our class in the relevant file, and inherit from `PyBoyPlugin`[<sup id="Z12255h">↓</sup>](#f-Z12255h):
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 pyboy/plugins/auto_pause.pxd
```cython
⬜ 6      from pyboy.plugins.base_plugin cimport PyBoyPlugin
⬜ 7      
⬜ 8      
🟩 9      cdef class AutoPause(PyBoyPlugin):
⬜ 10         pass
⬜ 11     
⬜ 12     
```

<br/>

## Update additional files with the new class
Every time we add a new `PyBoyPlugin`[<sup id="Z12255h">↓</sup>](#f-Z12255h), we reference it in a few locations.
We will still look at `AutoPause`[<sup id="29Dn9T">↓</sup>](#f-29Dn9T) as our example.

<br/>

2\. Don't forget to add the new class to [[sym:./pyboy/plugins/manager.pxd({"type":"path","text":"pyboy/plugins/manager.pxd","path":"pyboy/plugins/manager.pxd"})]], for example:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 pyboy/plugins/manager.pxd
```cython
⬜ 11     from pyboy.plugins.window_dummy cimport WindowDummy
⬜ 12     from pyboy.plugins.debug cimport Debug
⬜ 13     from pyboy.plugins.disable_input cimport DisableInput
🟩 14     from pyboy.plugins.auto_pause cimport AutoPause
⬜ 15     from pyboy.plugins.record_replay cimport RecordReplay
⬜ 16     from pyboy.plugins.rewind cimport Rewind
⬜ 17     from pyboy.plugins.screen_recorder cimport ScreenRecorder
```

<br/>

Also notice in the same file:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 pyboy/plugins/manager.pxd
```cython
⬜ 34         cdef public WindowDummy window_dummy
⬜ 35         cdef public Debug debug
⬜ 36         cdef public DisableInput disable_input
🟩 37         cdef public AutoPause auto_pause
⬜ 38         cdef public RecordReplay record_replay
⬜ 39         cdef public Rewind rewind
⬜ 40         cdef public ScreenRecorder screen_recorder
```

<br/>

3\. Add the new class to [[sym:./pyboy/plugins/manager.py({"type":"path","text":"pyboy/plugins/manager.py","path":"pyboy/plugins/manager.py"})]], for instance:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 pyboy/plugins/manager.py
```python
⬜ 29         yield WindowDummy.argv
⬜ 30         yield Debug.argv
⬜ 31         yield DisableInput.argv
🟩 32         yield AutoPause.argv
⬜ 33         yield RecordReplay.argv
⬜ 34         yield Rewind.argv
⬜ 35         yield ScreenRecorder.argv
```

<br/>

Additionally in the same file:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 pyboy/plugins/manager.py
```python
⬜ 58             self.debug_enabled = self.debug.enabled()
⬜ 59             self.disable_input = DisableInput(pyboy, mb, pyboy_argv)
⬜ 60             self.disable_input_enabled = self.disable_input.enabled()
🟩 61             self.auto_pause = AutoPause(pyboy, mb, pyboy_argv)
⬜ 62             self.auto_pause_enabled = self.auto_pause.enabled()
⬜ 63             self.record_replay = RecordReplay(pyboy, mb, pyboy_argv)
⬜ 64             self.record_replay_enabled = self.record_replay.enabled()
```

<br/>

4\. We modify  [[sym:./pyboy/plugins/manager_gen.py({"type":"path","text":"pyboy/plugins/manager_gen.py","path":"pyboy/plugins/manager_gen.py"})]], as seen here:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 pyboy/plugins/manager_gen.py
```python
⬜ 9      windows = ["WindowSDL2", "WindowOpenGL", "WindowHeadless", "WindowDummy", "Debug"]
⬜ 10     game_wrappers = ["GameWrapperSuperMarioLand", "GameWrapperTetris", "GameWrapperKirbyDreamLand"]
⬜ 11     plugins = [
🟩 12         "DisableInput", "AutoPause", "RecordReplay", "Rewind", "ScreenRecorder", "ScreenshotRecorder"
⬜ 13     ] + game_wrappers
⬜ 14     all_plugins = windows + plugins
⬜ 15     
```

<br/>

<!-- THIS IS AN AUTOGENERATED SECTION. DO NOT EDIT THIS SECTION DIRECTLY -->
### Swimm Note

<span id="f-29Dn9T">AutoPause</span>[^](#29Dn9T) - "pyboy/plugins/auto_pause.pxd" L9
```cython
cdef class AutoPause(PyBoyPlugin):
```

<span id="f-Z1Xxa8r">BaseDebugWindow</span>[^](#Z1Xxa8r) - "pyboy/plugins/debug.py" L339
```python
class BaseDebugWindow(PyBoyWindowPlugin):
```

<span id="f-3qaNn">BaseDebugWindow</span>[^](#3qaNn) - "pyboy/plugins/debug.pxd" L45
```cython
cdef class BaseDebugWindow(PyBoyWindowPlugin):
```

<span id="f-ZcEerc">Debug</span>[^](#ZcEerc) - "pyboy/plugins/debug.pxd" L33
```cython
cdef class Debug(PyBoyWindowPlugin):
```

<span id="f-ZUAYk4">GameWrapperSuperMarioLand</span>[^](#ZUAYk4) - "pyboy/plugins/game_wrapper_super_mario_land.py" L105
```python
class GameWrapperSuperMarioLand(PyBoyGameWrapper):
```

<span id="f-1l8il3">GameWrapperSuperMarioLand</span>[^](#1l8il3) - "pyboy/plugins/game_wrapper_super_mario_land.pxd" L12
```cython
cdef class GameWrapperSuperMarioLand(PyBoyGameWrapper):
```

<span id="f-3Wzwc">GameWrapperTetris</span>[^](#3Wzwc) - "pyboy/plugins/game_wrapper_tetris.py" L57
```python
class GameWrapperTetris(PyBoyGameWrapper):
```

<span id="f-1MSrdj">GameWrapperTetris</span>[^](#1MSrdj) - "pyboy/plugins/game_wrapper_tetris.pxd" L12
```cython
cdef class GameWrapperTetris(PyBoyGameWrapper):
```

<span id="f-2ncaJG">PyBoyGameWrapper</span>[^](#2ncaJG) - "pyboy/plugins/base_plugin.pxd" L40
```cython
cdef class PyBoyGameWrapper(PyBoyPlugin):
```

<span id="f-Z12255h">PyBoyPlugin</span>[^](#Z12255h) - "pyboy/plugins/base_plugin.pxd" L17
```cython
cdef class PyBoyPlugin:
```

<span id="f-ZGfdrw">PyBoyWindowPlugin</span>[^](#ZGfdrw) - "pyboy/plugins/base_plugin.pxd" L29
```cython
cdef class PyBoyWindowPlugin(PyBoyPlugin):
```

<span id="f-halMj">TileViewWindow</span>[^](#halMj) - "pyboy/plugins/debug.py" L414
```python
class TileViewWindow(BaseDebugWindow):
```

<span id="f-ZoqyY2">TileViewWindow</span>[^](#ZoqyY2) - "pyboy/plugins/debug.pxd" L74
```cython
cdef class TileViewWindow(BaseDebugWindow):
```

<br/>

This file was generated by Swimm. [Click here to view it in the app](https://swimm-web-app.web.app/repos/Z2l0aHViJTNBJTNBUHlCb3klM0ElM0FnaWxhZG5hdm90/docs/opf19).