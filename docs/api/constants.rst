Constants
=========

**Technical overview.** The graphics and memory hardware uses fixed addresses,
dimensions, and limits: VRAM, tile maps, OAM, the LCD frame, and the number of
available tiles or sprites. These values describe the layout and capacity of
the emulated hardware.

**Using the API.** The :mod:`pyboy.api.constants` module exposes those values as
named Python constants. Use them when interpreting addresses or sizing data
structures instead of duplicating hardware-specific numbers in an
application.

.. automodule:: pyboy.api.constants
   :members:
