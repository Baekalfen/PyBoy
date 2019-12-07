import sys

sys.path.append(".") # isort:skip
from pyboy.rewind import DeltaFixedAllocBuffers, CompressedFixedAllocBuffers, FixedAllocBuffers, FILL_VALUE # isort:skip


def write_bytes(buf, values):
    for v in values:
        buf.write(v % 0x100)

def test_buffer():
    for buf in [FixedAllocBuffers(), CompressedFixedAllocBuffers(), DeltaFixedAllocBuffers()]:
        A = [x % 0x100 for x in range(0, 4322)]
        B = [x % 0x100 for x in range(10, 232)]
        C = [x % 0x100 for x in range(5, 13)]
        D = [0 for _ in range(4322)]

        for E in [A, B, C, D]:
            write_bytes(buf, E)
            buf.new()

        for E in [D, C, B, A]:
            buf.seek_frame(-1)
            tests = [(x, buf.read()) for x in E]
            assert all(list(map(lambda x: x[0] == x[1], tests)))

        # breakpoint()
        for E in [A, B, C, D]:
            buf.seek_frame(1)
            tests = [(x, buf.read()) for x in E]
            assert all(list(map(lambda x: x[0] == x[1], tests)))


def test_compressed_buffer():
    buf = CompressedFixedAllocBuffers()

    write_bytes(buf, [0 for _ in range(10)])
    # Zeros are not written before a flush
    assert all(map(lambda x: x==FILL_VALUE, buf.buffer[:12]))

    # Now, we should see one pair of '0' and length
    buf.flush()
    assert all(map(lambda x: x==FILL_VALUE, buf.buffer[2:12]))
    assert buf.buffer[0] == 0
    assert buf.buffer[1] == 10

    # Second flush should do nothing
    buf.flush()
    assert all(map(lambda x: x==FILL_VALUE, buf.buffer[2:12]))
    assert buf.buffer[0] == 0
    assert buf.buffer[1] == 10

    # Overflow 8-bit counter and see two pairs
    write_bytes(buf, [0 for _ in range(256)])
    buf.flush()
    assert all(map(lambda x: x[0]==x[1], zip(buf.buffer[2:8], [0, 255, 0, 1] + [FILL_VALUE]*2)))

    # Fit exactly within 8-bit counter
    write_bytes(buf, [0 for _ in range(255)])
    buf.flush()
    assert all(map(lambda x: x[0]==x[1], zip(buf.buffer[6:10], [0, 255] + [FILL_VALUE]*4)))

def test_delta_buffer():
    buf = DeltaFixedAllocBuffers()
    assert all(map(lambda x: x == FILL_VALUE, buf.buffer[:60]))
    assert all(map(lambda x: x == 0, buf.internal_buffer[:60]))

    write_bytes(buf, range(20))
    assert all(map(lambda x: x[0]==x[1], zip(buf.buffer[:60], [0]*20 + [FILL_VALUE]*40)))
    assert all(map(lambda x: x[0]==x[1], zip(buf.internal_buffer[:60], list(range(20)) + [0]*40)))
    buf.new()

    # Write same range(20), but add 0x80 to set the 7th bit. This should result in a delta of 128
    write_bytes(buf, range(0x80,0x80+20))
    assert all(map(lambda x: x[0]==x[1], zip(buf.buffer[:60], [0]*20 + list(range(20)) + [FILL_VALUE]*20)))
    assert all(map(lambda x: x[0]==x[1], zip(buf.internal_buffer[:60], [0x80]*20 + [0]*40)))
    buf.new()

    write_bytes(buf, [0xFF]*20)
    assert all(map(lambda x: x[0]==x[1], zip(buf.buffer[:60], [0]*20 + list(range(20)) + [0x80]*20)))
    assert all(map(lambda x: x[0]==x[1], zip(buf.internal_buffer[:60], [0x7F]*20 + [0]*40)))
    buf.new()

def test_delta_buffer2():
    buf = DeltaFixedAllocBuffers()
    assert all(map(lambda x: x == FILL_VALUE, buf.buffer[:60]))
    assert all(map(lambda x: x == 0, buf.internal_buffer[:60]))

    write_bytes(buf, [0xAA]*20)
    assert all(map(lambda x: x[0]==x[1], zip(buf.buffer[:60], [0]*20 + [FILL_VALUE]*40)))
    assert all(map(lambda x: x[0]==x[1], zip(buf.internal_buffer[:60], [0xAA]*20 + [0]*40)))
    buf.new()

    write_bytes(buf, [0xAA]*20)
    assert all(map(lambda x: x[0]==x[1], zip(buf.buffer[:60], [0]*20 + list(range(20)) + [0x80]*20)))
    assert all(map(lambda x: x[0]==x[1], zip(buf.internal_buffer[:60], [0x7F]*20 + [0]*40)))
    buf.new()
    breakpoint()


if __name__ == "__main__":
    test_buffer()
