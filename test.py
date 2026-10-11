import time

from pyboy import PyBoy

ROM = "pacman.gb"

known_addresses = (0xD637, 0xD638, 0xD639, 0xD643, 0xD616, 0xD641, 0xD64C, 0xD634, 0xD635)


def read_memory_range(pyboy, start_addr, end_addr):
    """
    Reads a range of memory and returns a dictionary
    mapping the address to its current value.
    """
    memory_dump = {}
    for addr in range(start_addr, end_addr):
        memory_dump[addr] = pyboy.memory[addr]
    return memory_dump


pyboy = PyBoy(ROM)
pyboy.set_emulation_speed(1.8)

ticks = 0
while pyboy.tick():
    # Press P in the game window to pause/unpause; tick() keeps polling input but the emulation is frozen
    if pyboy.paused:
        continue

    ticks += 1

    if ticks % 1 == 0:
        print(f"\n--- Memory Dump at Tick {ticks} ---")

        # full range 0xC000, 0xE000
        mem_data = read_memory_range(pyboy, 0xD634, 0xD636)
        if mem_data[0xD635] == 152:
            y = mem_data[0xD634] // 32
        elif mem_data[0xD635] == 153:
            y = mem_data[0xD634] // 32 + 8
        elif mem_data[0xD635] == 154:
            y = mem_data[0xD634] // 32 + 16
        else:
            y = mem_data[0xD634] // 32 + 32
        x = mem_data[0xD634] % 32
        print(x, y)
        # Iterate and print each address and its value
        for addr, val in mem_data.items():
            if val != 0 and not (addr in known_addresses):
                # Printing the address in Hex, and the value in both Hex and Decimal
                print(f"Addr: {hex(addr)} | Val: {hex(val)}")

        print("-" * 35)
    if ticks >= 380:
        time.sleep(0.02)
