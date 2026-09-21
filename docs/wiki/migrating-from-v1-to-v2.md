# Migrating from v1.x.x to v2.0.0

This page tries to show the common changes from the v1 API to the v2 API. PyBoy generally uses [Semantic Versioning](https://semver.org), which means that all subversions of v1.X.X versions should follow the same API, and increasing versions should only add functionality and fix bugs, and not break existing programs.

v2.0.0 is the first time since 2019, that we are introducing breaking changes to the API. We hope the new changes will make it easier to use PyBoy going forward. If you don't want to upgrade, you can simply pin your PyBoy version in your requirements file (`pyboy<2.0.0`).

The newest documentation can always be found at the [documentation home](../index).

## Changelog

* A lot of general fixes
* Improved documentation with examples
* {meth}`pyboy.PyBoy.tick` returns **`True`** on success.
* {meth}`pyboy.PyBoy.tick` now takes two optional parameters:
    * `n` number of frames to progress
    * `render` whether to render the screen on the last processed frame
* `pyboy.screen_image()` moved to `pyboy.screen.image`
* The "botsupport" module has been removed, and most of API is moved to the PyBoy object
* {meth}`pyboy.PyBoy.button` can be used to send input, and will automatically release after 1 frame
* {meth}`pyboy.PyBoy.button_press` allows for manual control of input
* {meth}`pyboy.PyBoy.button_release` allows for manual control of input
* `pyboy.memory[0x100:0x150] = 123` replaces all three `pyboy.get/set/override_memory_value` and extends it with an option to specify bank
* {meth}`pyboy.PyBoy.hook_register` registers a callback at a specific point in your game. Used for fine-grained tracking of events and control of the game
* {meth}`pyboy.PyBoy.symbol_lookup` looks up an address for a symbol to use with memory read/write
* “dummy” and “headless” windows have been merged into “null” window because of the new `pyboy.tick`
* Game wrappers are now automatically loaded and accessible through the `pyboy.game_wrapper` property; see the [plugin and wrapper reference](../plugins/index)
* Remove fitness scores from game wrappers
* `pyboy.game_area()` is a shortcut for `pyboy.game_wrapper.game_area()`
* `pyboy.game_area_collision()` is a shortcut for `pyboy.game_wrapper.game_area_collision()`
* `pyboy.game_area_dimensions(…)` can be used to configure game_area
* `pyboy.game_area_mapping(…)` can apply a mapping to all game area tiles. I.e. simplify the tiles, or zero-out uninteresting tiles
* OpenAI Gym/Gymnasium has been removed from PyBoy. It has been [replaced by an example](using-pyboy-with-gym) instead
* The [memory scanner API](../api/memory_scanner) allows you to isolate memory addresses of interest
* Support for 768 CGB tiles vs. 384 in DMG mode


## Common Issues


### Inverted pyboy.tick()

`pyboy.tick()` now returns `True` until the emulation stops. This used to be inverted!

```python
>>> pyboy.tick()
1
```

### No attribute 'readonly'

**This has been fixed since v2.0.1!**

Because of a bug in v2.0.0, it was required to `pip install pillow` too.
```
AttributeError: 'NoneType' object has no attribute 'readonly'
AttributeError: 'NoneType' object has no attribute 'readonly'
Exception ignored in: 'pyboy.pyboy.PyBoy._post_tick'
Traceback (most recent call last):
  File ".../pyboy/__main__.py", line 167, in main
    while pyboy._tick(render):
```

### openai_gym

```python
>>> pyboy.openai_gym()
Traceback (most recent call last):
...
AttributeError: ...PyBoy... object has no attribute 'openai_gym'

```

[OpenAI Gym](https://github.com/openai/gym) and now [Gymnasium](https://github.com/Farama-Foundation/Gymnasium) has been removed from PyBoy to avoid maintaining it, and because most users want to modify it anyway. See [Using PyBoy with Gymnasium](using-pyboy-with-gym) for the needed boilerplate code and how to get started.

### window_type, bootrom_file

`window_type` is now `window`:
```python
>>> pyboy = PyBoy(..., window_type='null')
pyboy.pyboy                    ERROR    Deprecated use of 'window_type'. Use 'window' keyword argument instead. https://github.com/Baekalfen/PyBoy/wiki/Migrating-from-v1.x.x-to-v2.0.0
```

`bootrom_file` is now `bootrom`
```python
>>> pyboy = PyBoy(..., bootrom_file=...)
pyboy.pyboy                    ERROR    Deprecated use of 'bootrom_file'. Use 'bootrom' keyword argument instead. https://github.com/Baekalfen/PyBoy/wiki/Migrating-from-v1.x.x-to-v2.0.0
```


### dummy, headless

Because of the changes to `pyboy.tick()`, a dummy and headless window type is no longer needed. The effects can be controlled by changing the parameters:
```python
>>> pyboy = PyBoy(..., window='dummy')
pyboy.plugins.window_null      ERROR    Deprecated use of "headless" or "dummy" window. Change to "null" window instead. https://github.com/Baekalfen/PyBoy/wiki/Migrating-from-v1.x.x-to-v2.0.0
>>> pyboy = PyBoy(..., window='null')
>>> pyboy.tick(1, True) # Renders 1 frame like "headless" would
1
>>> pyboy.tick(1, False) # Render 1 frame like "dummy" would
1
```

### screen_image

```python
>>> pyboy.screen_image()
Traceback (most recent call last):
...
AttributeError: ...PyBoy... object has no attribute 'screen_image'

```

This is now a property instead of a function. This will make it faster for most usecases, as no new object is created. But this also means you should copy, convert or resize the image to keep it:
```python
>>> pyboy.screen.image # Long-lived reference
<PIL.Image.Image image mode=RGBA size=160x144 at ...>
>>> pyboy.screen.image.copy() # New copy
<PIL.Image.Image image mode=RGBA size=160x144 at ...>
>>> pyboy.screen.image.convert('RGB') # New copy
<PIL.Image.Image image mode=RGB size=160x144 at ...>
>>> pyboy.screen.image.resize((80,72)) # New copy
<PIL.Image.Image image mode=RGBA size=80x72 at ...>
```


### get_memory_value, set_memory_value, override_memory_value

```python
>>> pyboy.get_memory_value(0x1000)
Traceback (most recent call last):
...
AttributeError: ...PyBoy... object has no attribute 'get_memory_value'
>>> pyboy.set_memory_value(0xA000, 3)
Traceback (most recent call last):
...
AttributeError: ...PyBoy... object has no attribute 'set_memory_value'
>>> pyboy.override_memory_value(1, 0x1000, 123)
Traceback (most recent call last):
...
AttributeError: ...PyBoy... object has no attribute 'override_memory_value'

```

This is now:
```python
>>> pyboy.memory[0x00FC] # Get
14
>>> pyboy.memory[0xA000] = 3 # Set
>>> pyboy.memory[1, 0x1000] = 123 # Override ROM bank 1
```


### botsupport_manager, tilemap_background, tilemap_window

```python
>>> pyboy.botsupport_manager().tilemap_background()
Traceback (most recent call last):
...
AttributeError: ...PyBoy... object has no attribute 'botsupport_manager'
>>> pyboy.botsupport_manager().tilemap_window()
Traceback (most recent call last):
...
AttributeError: ...PyBoy... object has no attribute 'botsupport_manager'
>>> pyboy.botsupport_manager().screen().screen_ndarray()
Traceback (most recent call last):
...
AttributeError: ...PyBoy... object has no attribute 'botsupport_manager'

```

`botsupport_manager` has been removed. You can now find the API calls directly on the PyBoy object. And in case of `tilemap_background`, `tilemap_window` and `screen`, they are all properties instead of functions:
```python
>>> type(pyboy.tilemap_background)
<class 'pyboy.api.tilemap.TileMap'>
>>> type(pyboy.tilemap_window)
<class 'pyboy.api.tilemap.TileMap'>
>>> type(pyboy.screen.ndarray)
<class 'numpy.ndarray'>
```
