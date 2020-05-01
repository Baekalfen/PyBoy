import platform

import pytest

is_pypy = platform.python_implementation() == "PyPy"

if is_pypy:
    from pyboy.plugins.rewind import DeltaFixedAllocBuffers, CompressedFixedAllocBuffers, FixedAllocBuffers, \
                                    FILL_VALUE, FIXED_BUFFER_SIZE


def write_bytes(buf, values):
    for v in values:
        buf.write(v % 0x100)


@pytest.mark.skipif(not is_pypy, reason="This test doesn't work in Cython")
class TestRewind:
    def test_all(self):
        for buf in [FixedAllocBuffers(), CompressedFixedAllocBuffers(), DeltaFixedAllocBuffers()]:
            A = [1] * 16
            B = [2] * 16
            C = [4] * 16
            # A = [x % 0x100 for x in range(0, 20)]
            # B = [x % 0x100 for x in range(10, 40)]
            # C = [x % 0x100 for x in range(5, 13)]
            D = [8] * 16

            for E in [A, B, C, D]:
                write_bytes(buf, E)
                buf.new()

            for E in [D, C, B, A]:
                assert buf.seek_frame(-1)
                tests = [(x, buf.read()) for x in E]
                assert all(list(map(lambda x: x[0] == x[1], tests)))

            order = [A, B, C, D]
            # DeltaFixedAllocBuffers doesn't repeat the first section
            if isinstance(buf, DeltaFixedAllocBuffers):
                order.pop(0)
            for E in order:
                assert buf.seek_frame(1)
                tests = [(x, buf.read()) for x in E]
                assert all(list(map(lambda x: x[0] == x[1], tests)))

    def test_delta_seek(self):
        buf = DeltaFixedAllocBuffers()
        A = [1] * 16
        B = [2] * 16
        C = [3] * 16

        write_bytes(buf, A)
        buf.new()
        write_bytes(buf, B)
        buf.new()
        write_bytes(buf, C)
        buf.new()

        assert buf.seek_frame(-1)
        tests = [(x, buf.read()) for x in C]
        assert all(list(map(lambda x: x[0] == x[1], tests)))

        assert buf.seek_frame(-1)
        tests = [(x, buf.read()) for x in B]
        assert all(list(map(lambda x: x[0] == x[1], tests)))

        assert buf.seek_frame(-1)
        tests = [(x, buf.read()) for x in A]
        assert all(list(map(lambda x: x[0] == x[1], tests)))

        # Hit buffer boundary
        assert not buf.seek_frame(-1)

        assert buf.seek_frame(1)
        tests = [(x, buf.read()) for x in B]
        assert all(list(map(lambda x: x[0] == x[1], tests)))

        assert buf.seek_frame(1)
        tests = [(x, buf.read()) for x in C]
        assert all(list(map(lambda x: x[0] == x[1], tests)))

        assert not buf.seek_frame(1)

    def test_compressed_buffer(self):
        buf = CompressedFixedAllocBuffers()

        write_bytes(buf, [0 for _ in range(10)])
        # Zeros are not written before a flush
        assert all(map(lambda x: x == FILL_VALUE, buf.buffer[:12]))

        # Now, we should see one pair of '0' and length
        buf.flush()
        assert all(map(lambda x: x == FILL_VALUE, buf.buffer[2:12]))
        assert buf.buffer[0] == 0
        assert buf.buffer[1] == 10

        # Second flush should do nothing
        buf.flush()
        assert all(map(lambda x: x == FILL_VALUE, buf.buffer[2:12]))
        assert buf.buffer[0] == 0
        assert buf.buffer[1] == 10

        # Overflow 8-bit counter and see two pairs
        write_bytes(buf, [0 for _ in range(256)])
        buf.flush()
        assert all(map(lambda x: x[0] == x[1], zip(buf.buffer[2:8], [0, 255, 0, 1] + [FILL_VALUE] * 2)))

        # Fit exactly within 8-bit counter
        write_bytes(buf, [0 for _ in range(255)])
        buf.flush()
        assert all(map(lambda x: x[0] == x[1], zip(buf.buffer[6:10], [0, 255] + [FILL_VALUE] * 4)))

    def test_delta_buffer(self):
        buf = DeltaFixedAllocBuffers()
        assert all(map(lambda x: x == FILL_VALUE, buf.buffer[:60]))
        assert all(map(lambda x: x == 0, buf.internal_buffer[:60]))

        write_bytes(buf, range(20))
        # The compression adds a [0, 1] prefix, as there is a zero, repeated once
        assert all(map(lambda x: x[0] == x[1], zip(buf.buffer[:60], [0, 1] + list(range(1, 20)) + [FILL_VALUE] * 40)))
        # The compression doesn't exist in the internal buffer
        assert all(map(lambda x: x[0] == x[1], zip(buf.internal_buffer[:60], list(range(20)) + [0] * 40)))
        buf.new()

        # Write same range(20), but add 0x80 to set the 7th bit.
        # This should result in a delta with 20 values of 128 as only
        # the 7th bit is the xor-difference from the frame above.
        write_bytes(buf, range(0x80, 0x80 + 20))
        assert all(
            map(
                lambda x: x[0] == x[1],
                zip(buf.buffer[:60], [0, 1] + list(range(1, 20)) + [0x80] * 20 + [FILL_VALUE] * 20)
            )
        )
        assert all(map(lambda x: x[0] == x[1], zip(buf.internal_buffer[:60], list(range(0x80, 0x80 + 20)) + [0] * 40)))
        buf.new()

        write_bytes(buf, [0xFF] * 20)
        assert all(
            map(
                lambda x: x[0] == x[1],
                zip(
                    buf.buffer[:61],
                    [0, 1] + list(range(1, 20)) + [0x80] * 20 + [x ^ 0xFF for x in list(range(0x80, 0x80 + 20))]
                )
            )
        )
        assert all(map(lambda x: x[0] == x[1], zip(buf.internal_buffer[:60], [0xFF] * 20 + [0] * 40)))
        buf.new()

    def test_delta_buffer_repeat_pattern(self):
        buf = DeltaFixedAllocBuffers()
        assert all(map(lambda x: x == FILL_VALUE, buf.buffer[:60]))
        assert all(map(lambda x: x == 0, buf.internal_buffer[:60]))

        # Initial frame will just show up directly in the underlying buffer
        write_bytes(buf, [0xAA] * 20)
        assert all(map(lambda x: x[0] == x[1], zip(buf.buffer[:60], [0xAA] * 20 + [FILL_VALUE] * 40)))
        assert all(map(lambda x: x[0] == x[1], zip(buf.internal_buffer[:60], [0xAA] * 20 + [0] * 40)))
        buf.new()

        write_bytes(buf, [0xAA] * 20)
        # The written data should be zeros and only get written on a call to new (flush)
        assert all(map(lambda x: x[0] == x[1], zip(buf.buffer[:60], [0xAA] * 20 + [FILL_VALUE] * 40)))
        assert all(map(lambda x: x[0] == x[1], zip(buf.internal_buffer[:60], [0xAA] * 20 + [0] * 40)))
        buf.new()
        # Test that we see a zero-prefix with a count of 20
        assert all(map(lambda x: x[0] == x[1], zip(buf.buffer[:60], [0xAA] * 20 + [0, 20] + [FILL_VALUE] * 38)))
        # The internal buffer always reflect the current image, so nothing has changed.
        assert all(map(lambda x: x[0] == x[1], zip(buf.internal_buffer[:60], [0xAA] * 20 + [0] * 40)))

        write_bytes(buf, [0xAA] * 20)
        buf.new()
        # Same as above, with an additional zero-prefix
        assert all(map(lambda x: x[0] == x[1], zip(buf.buffer[:60], [0xAA] * 20 + [0, 20, 0, 20] + [FILL_VALUE] * 36)))
        assert all(map(lambda x: x[0] == x[1], zip(buf.internal_buffer[:60], [0xAA] * 20 + [0] * 40)))

    def test_buffer_overrun(self):
        buf = FixedAllocBuffers()
        # Fill almost entire buffer, as we want this section to be removed when we write more than the buffer can
        # contain.
        write_bytes(buf, [0xAA] * (FIXED_BUFFER_SIZE-10))
        buf.new()
        # We should have the first [0] section plus the one above.
        assert len(buf.sections) == 2
        # Writing 20 bytes, should overrun the buffer, and remove the section above to make room.
        write_bytes(buf, [0xAA] * 20)
        # We can verify this already, that one section is available.
        assert len(buf.sections) == 1
        # When call .new(), we are back to 2 sections.
        buf.new()
        assert len(buf.sections) == 2
