#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import io

BUFFER_LENGTH = 3600

# TODO: To improve performance, change all writes to int
# TODO: Use lists instead of BytesIO when using ints
# TODO: Use fixed allocation, unified storage. Manage pointers for saved states manually


class IntIOWrapper:
    """
    Wraps a file-like object to allow writing integers to it.
    This allows for higher performance, when writing to a memory map in rewind.
    """
    def __init__(self, buf):
        self.buffer = buf

    def write(self, byte):
        assert isinstance(byte, int)
        assert 0 <= byte <= 0xFF
        return self.buffer.write(byte.to_bytes(1, 'little'))

    def read(self):
        # assert count == 1, "Only a count of 1 is supported"
        data = self.buffer.read(1)
        assert len(data) == 1, "No data"
        return ord(data)

    def seek(self, pos):
        self.buffer.seek(pos)

    def flush(self):
        self.buffer.flush()


class RewindBuffer:

    def __init__(self):
        # self.buffers = [CompressedBuffer() for _ in range(BUFFER_LENGTH)]
        self.buffers = [IntIOWrapper(io.BytesIO()) for _ in range(BUFFER_LENGTH)]
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
            self.buffers[B] = self.buffers[A] # | self.buffers[B]

        buf = self.buffers[head]
        buf.seek(0)
        return buf

    def seek_relative(self, frames):
        if frames < 0 and self.tail_buffer > self.read_pointer+frames:
            self.read_pointer = self.tail_buffer
            return False
        elif frames > 0 and self.head_buffer-1 < self.read_pointer+frames:
            self.read_pointer = self.head_buffer-1
            return False
        else:
            self.read_pointer += frames
            self.read_pointer %= BUFFER_LENGTH
            return True

    def read(self):
        buf = self.buffers[self.read_pointer]
        buf.seek(0)
        return buf


# class CompressedBuffer:
#     def __init__(self):
#         self.buffer = io.BytesIO()
#         self.zeros = 0

#     def __or__(self, B):
#         return B
#     #     return io.BytesIO([a ^ b for a,b in zip(self.getvalue(), B.getvalue())])

#     def seek(self, position):
#         assert position == 0, "Only seeking to 0 is supported"
#         return self.buffer.seek(position)

#     def flush(self):
#         if self.zeros > 0:
#             chunks, rest = divmod(self.zeros, 0xFF)

#             for i in range(chunks):
#                 self.buffer.write(b'\x00')
#                 self.buffer.write(b'\xFF')

#             if (rest != 0):
#                 self.buffer.write(b'\x00')
#                 self.buffer.write(rest.to_bytes(1, "little"))

#         self.zeros = 0
#         # self.buffer.flush()

#     def write(self, data):
#         if len(data) > 1:
#             return sum([self.write(b.to_bytes(1, 'little')) for b in data])
#         elif data == b'\x00':
#             self.zeros += 1
#             return 1
#         else:
#             self.flush()
#             return self.buffer.write(data)

#     def read(self, n_bytes):
#         if n_bytes > 1:
#             # Concatenate bytes read with sum
#             return sum([self.read(1) for _ in range(n_bytes)])
#         elif self.zeros > 0:
#             self.zeros -= 1
#             return b'\x00'
#         else:
#             byte = self.buffer.read(n_bytes)
#             if byte == b'\x00':
#                 # If the bytes is zero, it means that the next byte will be the counter
#                 self.zeros = int.from_bytes(self.buffer.read(n_bytes), "little")
#                 self.zeros -= 1
#             assert byte != b'', "EOF reached!"
#             return byte


# class DeltaBuffer:
#     pass
