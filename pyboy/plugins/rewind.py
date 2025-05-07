#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pyboy
from pyboy.plugins.base_plugin import PyBoyPlugin
from pyboy.utils import IntIOInterface, PyBoyException, WindowEvent, cython_compiled

if not cython_compiled:
    exec("from pyboy.utils import malloc, free")

logger = pyboy.logging.get_logger(__name__)

FIXED_BUFFER_SIZE = 256 * 1024 * 1024
FIXED_BUFFER_MIN_ALLOC = 256 * 1024
FILL_VALUE = 123


class Rewind(PyBoyPlugin):
    argv = [("--rewind", {"action": "store_true", "help": "Enable rewind function"})]

    def __init__(self, *args):
        super().__init__(*args)

        self.rewind_speed = 1.0
        if self.enabled():
            self.rewind_buffer = DeltaFixedAllocBuffers()
        else:
            self.rewind_buffer = None

    def post_tick(self):
        if not self.pyboy.paused:
            self.mb.save_state(self.rewind_buffer)
            self.rewind_buffer.new()

    def window_title(self):
        return " Rewind: %0.2fKB/s" % ((self.rewind_buffer.avg_section_size * 60) / 1024)

    def handle_events(self, events):
        old_rewind_speed = self.rewind_speed
        for event in events:
            if event == WindowEvent.UNPAUSE:
                self.rewind_buffer.commit()
            elif event == WindowEvent.PAUSE_TOGGLE:
                if self.pyboy.paused:
                    self.rewind_buffer.commit()
            elif event == WindowEvent.RELEASE_REWIND_FORWARD:
                self.rewind_speed = 1
            elif event == WindowEvent.PRESS_REWIND_FORWARD:
                self.pyboy._pause()
                if self.rewind_buffer.seek_frame(1):
                    self.mb.load_state(self.rewind_buffer)
                    events.append(WindowEvent(WindowEvent._INTERNAL_RENDERER_FLUSH))
                    self.rewind_speed = min(self.rewind_speed * 1.1, 5)
                else:
                    logger.info("Rewind limit reached")
            elif event == WindowEvent.RELEASE_REWIND_BACK:
                self.rewind_speed = 1
            elif event == WindowEvent.PRESS_REWIND_BACK:
                self.pyboy._pause()
                if self.rewind_buffer.seek_frame(-1):
                    self.mb.load_state(self.rewind_buffer)
                    events.append(WindowEvent(WindowEvent._INTERNAL_RENDERER_FLUSH))
                    self.rewind_speed = min(self.rewind_speed * 1.1, 5)
                else:
                    logger.info("Rewind limit reached")

        if old_rewind_speed != self.rewind_speed:
            # NOTE: Disable this line, if recording for .replay files
            self.pyboy.set_emulation_speed(int(self.rewind_speed))
        return events

    def enabled(self):
        return self.pyboy_argv.get("rewind")

    def stop(self):
        self.rewind_buffer.stop()


##############################################################
# Homogeneous cyclic buffer
##############################################################


class FixedAllocBuffers(IntIOInterface):
    def __init__(self):
        self.buffer = malloc(FIXED_BUFFER_SIZE)
        for n in range(FIXED_BUFFER_SIZE):
            self.buffer[n] = FILL_VALUE
        self.sections = [0]
        self.current_section = 0
        self.tail_pointer = 0
        # self.head_pointer = 0
        self.section_head = 0
        self.section_tail = 0
        self.section_pointer = 0
        self.avg_section_size = 0.0

    def stop(self):
        free(self.buffer)

    def flush(self):
        pass

    def new(self):
        self.flush()
        # print(self.section_pointer-self.sections[-1]) # Find the actual length of the state in memory
        self.sections.append(self.section_pointer)
        self.current_section += 1
        section_size = (self.section_head - self.section_tail + FIXED_BUFFER_SIZE) % FIXED_BUFFER_SIZE
        # Exponentially decaying moving average
        self.avg_section_size = (0.9 * self.avg_section_size) + (0.1 * section_size)
        self.section_tail = self.section_pointer

    def write(self, val):
        assert val < 0x100
        if (self.section_pointer + 1) % FIXED_BUFFER_SIZE == self.tail_pointer:
            # We have reached the back of the buffer. We remove the first section to make room.
            self.sections = self.sections[1:]
            self.tail_pointer = self.sections[0]
            self.current_section -= 1
        self.buffer[self.section_pointer] = val
        self.section_pointer = (self.section_pointer + 1) % FIXED_BUFFER_SIZE
        self.section_head = self.section_pointer
        return 1

    def read(self):
        if self.section_pointer == self.section_head:
            raise PyBoyException("Read beyond section")
        data = self.buffer[self.section_pointer]
        self.section_pointer = (self.section_pointer + 1) % FIXED_BUFFER_SIZE
        return data

    def commit(self):
        if not self.section_head == self.section_pointer:
            raise PyBoyException("Section wasn't read to finish. This would likely be unintentional")
        self.sections = self.sections[: self.current_section + 1]

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
                if self.current_section == len(self.sections) - 1:
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
        FixedAllocBuffers.__init__(self)
        self.zeros = 0

    def flush(self):
        if self.zeros > 0:
            chunks = self.zeros // 0xFF
            rest = self.zeros % 0xFF

            for i in range(chunks):
                FixedAllocBuffers.write(self, 0)
                FixedAllocBuffers.write(self, 0xFF)

            if rest != 0:
                FixedAllocBuffers.write(self, 0)
                FixedAllocBuffers.write(self, rest)

        self.zeros = 0
        FixedAllocBuffers.flush(self)

    def write(self, data):
        if data == 0:
            self.zeros += 1
            return 1
        else:
            self.flush()
            return FixedAllocBuffers.write(self, data)

    def read(self):
        if self.zeros > 0:
            self.zeros -= 1
            return 0
        else:
            byte = FixedAllocBuffers.read(self)
            if byte == 0:
                # If the bytes is zero, it means that the next byte will be the counter
                self.zeros = FixedAllocBuffers.read(self)
                self.zeros -= 1
            return byte

    def new(self):
        FixedAllocBuffers.new(self)

    def commit(self):
        FixedAllocBuffers.commit(self)

    def seek_frame(self, v):
        return FixedAllocBuffers.seek_frame(self, v)


class DeltaFixedAllocBuffers(CompressedFixedAllocBuffers):
    """
    I chose to keep the code simple at the expense of some edge cases acting different from the other buffers.
    When seeking, the last frame will be lost. This has no practical effect, and is only noticeble in unittesting.
    """

    def __init__(self):
        CompressedFixedAllocBuffers.__init__(self)
        self.internal_pointer = 0
        self.prev_internal_pointer = 0
        # The initial values needs to be 0 to act as the "null-frame" and make the first frame a one-to-one copy
        # TODO: It would work with any values, but it makes it easier to debug
        self.internal_buffer = malloc(FIXED_BUFFER_MIN_ALLOC)
        self.internal_buffer_dirty = False

        # A side effect of the implementation will create a zero-frame in the beginning. Keep track of this,
        # as we don't want to use the section until we rollover the circular buffer.
        self.base_frame = 0
        # The frame we inject in the end to flush the last frame out
        self.injected_zero_frame = 0

    def stop(self):
        super().stop()
        free(self.internal_buffer)

    def write(self, data):
        self.internal_buffer_dirty = True
        old_val = self.internal_buffer[self.internal_pointer]
        xor_val = data ^ old_val
        self.internal_buffer[self.internal_pointer] = data
        self.internal_pointer += 1
        return CompressedFixedAllocBuffers.write(self, xor_val)

    def read(self):
        old_val = CompressedFixedAllocBuffers.read(self)
        data = old_val ^ self.internal_buffer[self.internal_pointer]
        self.internal_buffer[self.internal_pointer] = data
        self.internal_pointer += 1
        return data

    def commit(self):
        self.internal_pointer = 0
        self.injected_zero_frame = 0
        CompressedFixedAllocBuffers.commit(self)

    def new(self):
        self.prev_internal_pointer = self.internal_pointer
        self.internal_pointer = 0
        CompressedFixedAllocBuffers.new(self)

    def flush_internal_buffer(self):
        # self.current_section += 1
        for n in range(self.prev_internal_pointer):
            CompressedFixedAllocBuffers.write(self, self.internal_buffer[n])
            # Make a null-frame so we can XOR the newest frame back in
            self.internal_buffer[n] = 0
        self.internal_buffer_dirty = False
        CompressedFixedAllocBuffers.new(self)
        self.injected_zero_frame = self.current_section

    def seek_frame(self, frames):
        # for _ in range(abs(frames)):
        # TODO: Can only seek one frame
        if frames < 0:
            frames = -1
        else:
            frames = 1

        # Flush internal buffer to underlying memory. Otherwise, the newest frame, won't be seekable.
        if self.internal_buffer_dirty:
            self.flush_internal_buffer()
        self.internal_pointer = 0

        if frames > 0 and self.injected_zero_frame - 1 == self.current_section:
            return False
        elif frames < 0 and self.current_section - 1 == self.base_frame:
            return False

        return CompressedFixedAllocBuffers.seek_frame(self, frames)
