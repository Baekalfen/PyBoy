import numpy as np
from abc import abstractmethod


class FrameBuffer(object):
    """
    """

    def __init__(self, array, scaleFactor=1):
        """
        """
        if not hasattr(array, '__getitem__') or not hasattr(array, '__setitem__'):
            raise AttributeError('Input array is missing attributes __getitem__'\
                    'and __setitem__')
        if not isinstance(scaleFactor, int):
            raise TypeError('ScaleFactor must be an integer')
        self._array = array
        self._scaleFactor = scaleFactor

        self._cache = np.zeros(tuple(x / scaleFactor for x in array.shape), dtype=np.uint32)

    def fill(self, val):
        self._cache.fill(val)

    @abstractmethod
    def update(self):
        """
        """
        raise NotImplementedError()

    def __getitem__(self, key):
        """Get FrameBuffer item at index"""
        return self._cache[key]

    def __setitem__(self, key, item):
        """Set FrameBuffer item at index"""
        self._cache[key] = item

    def get_buffer(self):
        return self._array.copy()

class ScaledFrameBuffer(FrameBuffer):

    def update(self):
        for (x, y),_ in np.ndenumerate(self._array):
            self._array[x, y] = self._cache[x/self._scaleFactor,
                    y/self._scaleFactor]

class SimpleFrameBuffer(FrameBuffer):

    SCALE = 1

    def __init__(self, array):
        """
        """
        super(self.__class__, self).__init__(array, self.SCALE)
        self._cache = None

    def fill(self, val):
        self._array.fill(val)

    def update(self):
        pass
        # for (x, y),_ in np.ndenumerate(self._array):
        #     self._array[x, y] = self._cache[x, y]

    def __getitem__(self, key):
        """Get FrameBuffer item at index"""
        return self._array[key]

    def __setitem__(self, key, item):
        """Set FrameBuffer item at index"""
        self._array[key] = item
