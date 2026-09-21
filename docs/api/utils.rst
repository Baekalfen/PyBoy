Utilities
=========

**Technical overview.** Game Boy integrations need values that cross the
boundary between the emulated hardware and the host application, such as
button events, BCD-encoded numbers, and errors describing invalid hardware
access.

**Using the API.** :mod:`pyboy.utils` provides :class:`WindowEvent
<pyboy.utils.WindowEvent>` values for :meth:`PyBoy.send_input
<pyboy.PyBoy.send_input>`, BCD conversion helpers, and the exception classes
raised by the public API. The complete set of event names is listed below; use
the high-level button methods when they are sufficient.

.. automodule:: pyboy.utils
   :members:
   :show-inheritance:

.. _window-event-options:

WindowEvent options
-------------------

The internal events are included for completeness, but applications should
use the public events when sending input.

.. hlist::
   :columns: 3

   * :class:`QUIT <pyboy.utils.WindowEvent>`
   * :class:`PRESS_ARROW_UP <pyboy.utils.WindowEvent>`
   * :class:`PRESS_ARROW_DOWN <pyboy.utils.WindowEvent>`
   * :class:`PRESS_ARROW_RIGHT <pyboy.utils.WindowEvent>`
   * :class:`PRESS_ARROW_LEFT <pyboy.utils.WindowEvent>`
   * :class:`PRESS_BUTTON_A <pyboy.utils.WindowEvent>`
   * :class:`PRESS_BUTTON_B <pyboy.utils.WindowEvent>`
   * :class:`PRESS_BUTTON_SELECT <pyboy.utils.WindowEvent>`
   * :class:`PRESS_BUTTON_START <pyboy.utils.WindowEvent>`
   * :class:`RELEASE_ARROW_UP <pyboy.utils.WindowEvent>`
   * :class:`RELEASE_ARROW_DOWN <pyboy.utils.WindowEvent>`
   * :class:`RELEASE_ARROW_RIGHT <pyboy.utils.WindowEvent>`
   * :class:`RELEASE_ARROW_LEFT <pyboy.utils.WindowEvent>`
   * :class:`RELEASE_BUTTON_A <pyboy.utils.WindowEvent>`
   * :class:`RELEASE_BUTTON_B <pyboy.utils.WindowEvent>`
   * :class:`RELEASE_BUTTON_SELECT <pyboy.utils.WindowEvent>`
   * :class:`RELEASE_BUTTON_START <pyboy.utils.WindowEvent>`
   * :class:`_INTERNAL_TOGGLE_DEBUG <pyboy.utils.WindowEvent>`
   * :class:`PRESS_SPEED_UP <pyboy.utils.WindowEvent>`
   * :class:`RELEASE_SPEED_UP <pyboy.utils.WindowEvent>`
   * :class:`STATE_SAVE <pyboy.utils.WindowEvent>`
   * :class:`STATE_LOAD <pyboy.utils.WindowEvent>`
   * :class:`PASS <pyboy.utils.WindowEvent>`
   * :class:`SCREEN_RECORDING_TOGGLE <pyboy.utils.WindowEvent>`
   * :class:`PAUSE <pyboy.utils.WindowEvent>`
   * :class:`UNPAUSE <pyboy.utils.WindowEvent>`
   * :class:`PAUSE_TOGGLE <pyboy.utils.WindowEvent>`
   * :class:`PRESS_REWIND_BACK <pyboy.utils.WindowEvent>`
   * :class:`PRESS_REWIND_FORWARD <pyboy.utils.WindowEvent>`
   * :class:`RELEASE_REWIND_BACK <pyboy.utils.WindowEvent>`
   * :class:`RELEASE_REWIND_FORWARD <pyboy.utils.WindowEvent>`
   * :class:`WINDOW_FOCUS <pyboy.utils.WindowEvent>`
   * :class:`WINDOW_UNFOCUS <pyboy.utils.WindowEvent>`
   * :class:`_INTERNAL_RENDERER_FLUSH <pyboy.utils.WindowEvent>`
   * :class:`_INTERNAL_MOUSE <pyboy.utils.WindowEvent>`
   * :class:`_INTERNAL_MARK_TILE <pyboy.utils.WindowEvent>`
   * :class:`SCREENSHOT_RECORD <pyboy.utils.WindowEvent>`
   * :class:`DEBUG_MEMORY_SCROLL_DOWN <pyboy.utils.WindowEvent>`
   * :class:`DEBUG_MEMORY_SCROLL_UP <pyboy.utils.WindowEvent>`
   * :class:`MOD_SHIFT_ON <pyboy.utils.WindowEvent>`
   * :class:`MOD_SHIFT_OFF <pyboy.utils.WindowEvent>`
   * :class:`FULL_SCREEN_TOGGLE <pyboy.utils.WindowEvent>`
   * :class:`CYCLE_PALETTE <pyboy.utils.WindowEvent>`
   * :class:`SCREEN_RECORDING_TOGGLE_MP4 <pyboy.utils.WindowEvent>`
   * :class:`DEBUG_GAME_AREA_TOGGLE <pyboy.utils.WindowEvent>`
