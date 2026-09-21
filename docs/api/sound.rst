Sound
=====

**Technical overview.** The Game Boy audio processing unit produces digital
audio while the CPU and LCD advance. PyBoy collects those samples in a stereo
buffer for each frame; the number of valid samples can vary when frame timing
changes.

**Using the API.** :class:`Sound <pyboy.api.sound.Sound>` exposes the sample
rate, raw buffer format, valid buffer length, and the current samples as either
a memory view or a NumPy array. Read the buffer head each frame so consumers
process only the samples generated for that frame.

.. automodule:: pyboy.api.sound
   :members:
   :show-inheritance:
