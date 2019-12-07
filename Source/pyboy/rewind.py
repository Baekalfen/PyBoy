#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import array
import io

TIME_BUFFER_LENGTH = 3600
FIXED_BUFFER_SIZE = 64*1024*128
FIXED_BUFFER_MIN_ALLOC = 64*1024
FILL_VALUE = 123

# TODO: To improve performance, change all writes to int
# TODO: Use lists instead of BytesIO when using ints
# TODO: Use fixed allocation, unified storage. Manage pointers for saved states manually


# self.buffers = FixedAllocBuffers()
# self.buffers = TimeBuffers(TIME_BUFFER_LENGTH)
# self.buffers = [CompressedBuffer(IntIOWrapper(io.BytesIO())) for _ in range(TIME_BUFFER_LENGTH)]
# self.buffers = [IntIOWrapper(io.BytesIO()) for _ in range(TIME_BUFFER_LENGTH)]
# def get_rewind_buffer():
#     return FixedAllocBuffers()

# class RewindBuffer:
#     def commit(self):
#         raise Exception("Not implemented!")

#     def next(self):
#         raise Exception("Not implemented!")

#     def seek_frame(self, frames):
#         raise Exception("Not implemented!")

#     def read(self):
#         raise Exception("Not implemented!")

class IntIOInterface:
    def __init__(self, buf):
        pass

    def write(self, byte):
        raise Exception("Not implemented!")

    def read(self):
        raise Exception("Not implemented!")

    def seek(self, pos):
        raise Exception("Not implemented!")

    def flush(self):
        raise Exception("Not implemented!")

##############################################################
# Homogeneous cyclic buffer
##############################################################


class FixedAllocBuffers(IntIOInterface):
    def __init__(self):
        self.buffer = array.array('B', [FILL_VALUE]*(FIXED_BUFFER_SIZE))
        self.sections = [0]
        self.current_section = 0
        self.tail_pointer = 0
        # self.head_pointer = 0
        self.section_head = 0
        self.section_tail = 0
        self.section_pointer = 0

    def flush(self):
        pass

    def new(self):
        self.flush()
        # print(self.section_pointer-self.sections[-1]) # Find the actual length of the state in memory
        self.sections.append(self.section_pointer)
        self.current_section += 1
        self.section_tail = self.section_pointer

    def write(self, val):
        assert val < 0x100
        if self.section_pointer+1 == self.tail_pointer:
            raise Exception("Combine states!")
        self.buffer[self.section_pointer] = val
        self.section_pointer = (self.section_pointer + 1) % FIXED_BUFFER_SIZE
        self.section_head = self.section_pointer
        return 1

    def read(self):
        if self.section_pointer == self.section_head:
            raise Exception("Read beyond section")
        data = self.buffer[self.section_pointer]
        self.section_pointer = (self.section_pointer + 1) % FIXED_BUFFER_SIZE
        return data

    def commit(self):
        if not self.section_head == self.section_pointer:
            raise Exception("Section wasn't read to finish. This would likely be unintentional")
        self.sections = self.sections[:self.current_section+1]

    def seek_frame(self, frames):
        # TODO: Move for loop to Delta version
        for _ in range(abs(frames)):
            if frames < 0:
                if self.current_section < 1:
                    return False

                # Decrement the active section and fetch its pointer position
                head = self.sections[self.current_section]
                self.current_section -= 1
                tail = self.sections[self.current_section]
            else:
                if self.current_section == len(self.sections)-1:
                    return False

                # Increment the active section and fetch its pointer position
                tail = self.sections[self.current_section]
                self.current_section += 1
                head = self.sections[self.current_section]

        # Refine the new head and tail
        self.section_tail, self.section_head = tail, head

        # Seeks the section to 0, ready for reading
        self.section_pointer = self.section_tail
        return True


class CompressedFixedAllocBuffers(FixedAllocBuffers):
    def __init__(self):
        super().__init__()
        self.zeros = 0

    def flush(self):
        if self.zeros > 0:
            chunks, rest = divmod(self.zeros, 0xFF)

            for i in range(chunks):
                super().write(0)
                super().write(0xFF)

            if (rest != 0):
                super().write(0)
                super().write(rest)

        self.zeros = 0
        super().flush()

    def write(self, data):
        if data == 0:
            self.zeros += 1
            return 1
        else:
            self.flush()
            return super().write(data)

    def read(self):
        if self.zeros > 0:
            self.zeros -= 1
            return 0
        else:
            byte = super().read()
            if byte == 0:
                # If the bytes is zero, it means that the next byte will be the counter
                self.zeros = super().read()
                self.zeros -= 1
            return byte


class DeltaFixedAllocBuffers(CompressedFixedAllocBuffers):
    def __init__(self):
        super().__init__()
        self.internal_pointer = 0
        self.prev_internal_pointer = 0
        # The initial values needs to be 0 to act as the "null-frame" and make the first frame a one-to-one copy
        self.internal_buffer = array.array('B', [0]*FIXED_BUFFER_MIN_ALLOC)
        self.internal_buffer_dirty = False

    def write(self, data):
        self.internal_buffer_dirty = True
        old_val = self.internal_buffer[self.internal_pointer]
        xor_val = data ^ old_val
        self.internal_buffer[self.internal_pointer] = data
        self.internal_pointer += 1
        return super().write(xor_val)

    def read(self):
        old_val = super().read()
        data = old_val ^ self.internal_buffer[self.internal_pointer]
        self.internal_buffer[self.internal_pointer] = data
        self.internal_pointer += 1
        return data

    def commit(self):
        self.internal_pointer = 0
        super().commit()

    def new(self):
        self.prev_internal_pointer = self.internal_pointer
        self.internal_pointer = 0
        super().new()

    def seek_frame(self, frames):
        # for _ in range(abs(frames)):
        # TODO: Can only seek one frame
        if frames < 0:
            frames = -1
        else:
            frames = 1

        # Flush internal buffer to underlying memory. Otherwise, the newest frame, won't be seekable.
        if self.internal_buffer_dirty:
            # self.current_section += 1
            for n in range(self.prev_internal_pointer):
                super().write(self.internal_buffer[n])
                # Make a null-frame so we can XOR the newest frame back in
                self.internal_buffer[n] = 0
            self.internal_buffer_dirty = False
            super().new()
        self.internal_pointer = 0

        return super().seek_frame(frames)


##############################################################
# List-based cyclic buffer
##############################################################


class TimeBuffers:
    def __init__(self):
        self.buffers = [CompressedBuffer(IntIOWrapper(io.BytesIO())) for _ in range(TIME_BUFFER_LENGTH)]
        self.tail_buffer = 0
        self.head_buffer = 0
        self.read_pointer = 0

    def new(self):
        head = self.head_buffer
        self.read_pointer = head
        self.head_buffer += 1
        self.head_buffer %= TIME_BUFFER_LENGTH

        if self.tail_buffer == self.head_buffer:
            A = self.tail_buffer
            B = (self.tail_buffer+1) % TIME_BUFFER_LENGTH
            self.buffers[B] = self.buffers[A] # | self.buffers[B]

        buf = self.buffers[head]
        buf.seek(0)
        return buf

    def commit(self):
        self.head_buffer = self.read_pointer

    def seek_frame(self, frames):
        if frames < 0 and self.tail_buffer > self.read_pointer+frames:
            self.read_pointer = self.tail_buffer
            return False
        elif frames > 0 and self.head_buffer-1 < self.read_pointer+frames:
            self.read_pointer = self.head_buffer-1
            return False
        else:
            self.read_pointer += frames
            self.read_pointer %= TIME_BUFFER_LENGTH
            return True

    def read(self):
        buf = self.buffers[self.read_pointer]
        buf.seek(0)
        return buf

##############################################################
# Buffer wrappers
##############################################################


class IntIOWrapper(IntIOInterface):
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


class CompressedBuffer(IntIOInterface):
    def __init__(self, buf):
        self.buffer = buf
        self.zeros = 0

    def __or__(self, B):
        return B
    #     return io.BytesIO([a ^ b for a,b in zip(self.getvalue(), B.getvalue())])

    def seek(self, position):
        assert position == 0, "Only seeking to 0 is supported"
        self.buffer.seek(position)

    def flush(self):
        if self.zeros > 0:
            chunks, rest = divmod(self.zeros, 0xFF)

            for i in range(chunks):
                self.buffer.write(0)
                self.buffer.write(0xFF)

            if (rest != 0):
                self.buffer.write(0)
                self.buffer.write(rest)

        self.zeros = 0
        self.buffer.flush()

    def write(self, data):
        if data == 0:
            self.zeros += 1
            return 1
        else:
            self.flush()
            return self.buffer.write(data)

    def read(self):
        if self.zeros > 0:
            self.zeros -= 1
            return 0
        else:
            byte = self.buffer.read()
            if byte == 0:
                # If the bytes is zero, it means that the next byte will be the counter
                self.zeros = self.buffer.read()
                self.zeros -= 1
            return byte
