#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import io

BUFFER_LENGTH = 3600


class RewindBuffer:

    def __init__(self):
        self.buffers = [SparseBuffer() for _ in range(BUFFER_LENGTH)]
        # self.buffers = [io.BytesIO() for _ in range(BUFFER_LENGTH)]
        self.tail_buffer = 0
        self.head_buffer = 0
        self.read_pointer = 0

    def commit(self):
        self.head_buffer = self.read_pointer

    def next_write_buffer(self):
        head = self.head_buffer
        self.read_pointer = head
        self.head_buffer += 1
        self.head_buffer %= BUFFER_LENGTH

        if self.tail_buffer == self.head_buffer:
            A = self.tail_buffer
            B = (self.tail_buffer+1) % BUFFER_LENGTH
            self.buffers[B] = self.buffers[A] | self.buffers[B]

        buf = self.buffers[head]
        buf.seek(0)
        return buf

    def seek_relative(self, frames):
        if frames < 0 and self.tail_buffer > self.read_pointer+frames:
            self.read_pointer = self.tail_buffer
        elif frames > 0 and self.head_buffer-1 < self.read_pointer+frames:
            self.read_pointer = self.head_buffer-1
        else:
            self.read_pointer += frames
            self.read_pointer %= BUFFER_LENGTH

    def read(self):
        buf = self.buffers[self.read_pointer]
        buf.seek(0)
        return buf


class SparseBuffer:
    def __init__(self):
        self.buffer = io.BytesIO()

    def __or__(self, B):
        return B

    def seek(self, *args):
        return self.buffer.seek(*args)

    def write(self, *args):
        return self.buffer.write(*args)

    def read(self, *args):
        return self.buffer.read(*args)
