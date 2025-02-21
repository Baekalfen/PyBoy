#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
"""
This class gives access to the sound buffer of PyBoy.
"""

import numpy as np

from pyboy import utils
from pyboy.logging import get_logger

logger = get_logger(__name__)


class Sound:
    """
    As part of the emulation, we generate a sound buffer for each frame on the screen. This class has several helper
    methods to make it possible to read this buffer out.

    When the game enables/disables the LCD, the timing will be shorter than 70224 emulated cycles. Therefore the sound
    buffer will also be shorter than 16.667ms (60 FPS).

    Because the number of samples and the timing of frames don't match exactly, you can expect a little fluctuation in
    the number of samples per frame. Normally at a sample rate of 24,000Hz, it'll be 400 samples/second. But some times,
    it might become 401. As described above, when the LCD enables/disables, it might be even less -- maybe 30, 143,
    or 200 samples. This timespan represent what the real hardware would have shown.

    If you're working with encoding the screen and sound in a video stream, you could drop these shorter frames, if they
    cause problems. They usually only happen in transitions from menu to game or similar.
    """

    def __init__(self, mb):
        self.mb = mb

        self.sample_rate = self.mb.sound.sample_rate
        """
        Read-only. Changing this, will not change the sample rate. See `PyBoy` constructor instead.

        The sample rate is reported per second, while the frame rate of the Game Boy is ~60 frame per second.
        So expect the sound buffer to have 1/60 of this value in the buffer after every frame. Although it will
        fluctuate. See top of the page.

        ```python
        >>> pyboy.sound.sample_rate # in Hz
        48000
        >>> pyboy.sound.sample_rate // 60 # Expected samples per frame
        800
        >>> (800+1) * 2 # Minimum buffer size for you to prepare (2 channels, +1 for fluctuating lengths)
        1602
        >>> 1602 == pyboy.sound.raw_buffer_length # This is how the length is calculated at the moment
        True
        ```

        Returns
        -------
        int:
            The sample rate in Hz (samples per second)
        """

        self.raw_buffer_format = self.mb.sound.buffer_format
        """
        Returns the color format of the raw sound buffer. **This format is subject to change.**

        See how to interpret the format on: https://docs.python.org/3/library/struct.html#format-characters

        Example:
        ```python
        >>> pyboy.sound.raw_buffer_format
        'b'
        ```

        Returns
        -------
        str:
            Struct format of the raw sound buffer. E.g. 'b' for signed 8-bit
        """

        self.raw_buffer_length = self.mb.sound.audiobuffer_length
        """
        Read-only. Changing this, will not change the buffer length.

        This is the total length of the allocated raw buffer. Use this only to allocate an appropriate buffer in your
        script. The length of the valid data in the buffer is found using `Sound.raw_buffer_head`.

        Returns
        -------
        int:
            Total raw buffer length
        """

        self.raw_buffer = memoryview(self.mb.sound.audiobuffer).cast(
            self.raw_buffer_format, shape=(self.mb.sound.audiobuffer_length,)
        )
        """
        Provides a raw, unfiltered `memoryview` object with the data from sound buffer. Check
        `Sound.raw_buffer_format` to see which dataformat is used. **The returned type and dataformat are
        subject to change.** The sound buffer is in stereo format, so the odd indexes are the left channel,
        and even indexes are the right channel.

        Use this, only if you need to bypass the overhead of `Sound.ndarray`.

        Be aware to use the `Sound.raw_buffer_head`, as not all 'frames' are of equal length.

        Example:
        ```python
        >>> from array import array
        >>> sound_buffer = array(pyboy.sound.raw_buffer_format, pyboy.sound.raw_buffer[:pyboy.sound.raw_buffer_head])
        >>> sound_buffer
        array('b', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...])
        ```

        Returns
        -------
        memoryview:
            memoryview of sound data.
        """

        self.raw_ndarray = None
        if self.mb.sound.emulate:
            self.raw_ndarray = np.frombuffer(
                self.mb.sound.audiobuffer,
                dtype=np.int8,
            ).reshape(self.mb.sound.audiobuffer_length // 2, 2)
        else:
            self.raw_ndarray = utils.SoundEnabledError()

    @property
    def raw_buffer_head(self):
        """
        This returns the

        See the explanation at the top of the page.
        """
        return self.mb.sound.audiobuffer_head

    @property
    def ndarray(self):
        """
        References the sound data in NumPy format. **Remember to copy this object** if you intend to store it.
        The backing buffer will update, but it will be the same `ndarray` object.

        The format is given by `pyboy.api.sound.Sound.raw_buffer_format`. The sound buffer is in stereo format,
        so the first index is the left channel, and the second index is the right channel.

        This property returns an `ndarray` that is already accounting for the changing length of the sound buffer.
        See the explanation at the top of the page.

        Example:
        ```python
        >>> pyboy.sound.ndarray.shape # 401 samples, 2 channels (stereo)
        (801, 2)
        >>> pyboy.sound.ndarray
        array([[0, 0],
               [0, 0],
               ...
               [0, 0],
               [0, 0]], dtype=int8)

        ```

        Returns
        -------
        numpy.ndarray:
            Sound data in `ndarray` of bytes with shape given by sample rate
        """
        if self.mb.sound.emulate:
            return self.raw_ndarray[: self.mb.sound.audiobuffer_head]
        else:
            raise utils.PyBoyFeatureDisabledError("Sound is not enabled!")
