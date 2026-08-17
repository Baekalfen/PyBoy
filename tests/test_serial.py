#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy import PyBoy
from pyboy.utils import PyBoyInvalidOperationException
import pytest
import time
import multiprocessing
import os
import numpy as np
from pyboy.core.serial import SerialSharedMemoryBuffer

SERIAL_TEST_TIMEOUT = 60
SERIAL_TEST_TIMEOUT_TOTAL = 120
RENDER_SCREEN = False


def test_serial_transfer_clears_busy_flag(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(60, False)

    # Start a transfer using the internal clock. Bit 7 (transfer in
    # progress) reads back as set until the transfer completes.
    pyboy.memory[0xFF02] = 0x81
    assert pyboy.memory[0xFF02] & 0x80

    # 8 bits at 8192Hz take about 1ms -- well within one frame. Games
    # poll bit 7 to detect completion, so it has to read back as cleared.
    pyboy.tick(1, False)
    assert not pyboy.memory[0xFF02] & 0x80

    # Disconnected link cable always reads 0xFF
    assert pyboy.memory[0xFF01] == 0xFF

    pyboy.stop(save=False)


def test_serial_off(default_rom):
    pyboy = PyBoy(default_rom, window="null")

    assert pyboy.memory[0xFF01] == 0xFF, "Disconnected serial expects all high"
    pyboy.memory[0xFF01] = 0x00
    assert pyboy.memory[0xFF01] == 0xFF, "Disconnected serial cannot be set"

    pyboy.stop(save=False)


# @pytest.mark.parametrize("interrupt", [True, False])
# def test_serial_simultaneous_internal_handshake(default_rom, interrupt):
#     port = str(random.randint(1024, 65535))
#     barrier = threading.Barrier(2)
#     results = {}
#     errors = []

#     def handler(bind):
#         pyboy = None
#         try:
#             pyboy = PyBoy(
#                 default_rom,
#                 window="null",
#                 serial_address="127.0.0.1:" + port,
#                 serial_bind=bind,
#                 serial_interrupt_based=interrupt,
#             )
#             pyboy.tick(120, False, False)
#             barrier.wait()

#             # Both games use the internal-clock request during pokered's
#             # handshake. The transport must still assign opposite roles.
#             pyboy.memory[0xFF01] = 0x01
#             pyboy.memory[0xFF02] = 0x81
#             for _ in range(10000):
#                 pyboy.tick(1, False, False)
#                 if not pyboy.memory[0xFF02] & 0x80:
#                     break
#                 time.sleep(0.001)
#             else:
#                 raise AssertionError("Serial handshake timed out")
#             assert pyboy.memory[0xFF01] == (0x02 if bind else 0x01)

#             barrier.wait()
#             pyboy.memory[0xFF01] = 0xA5 if bind else 0x5A
#             pyboy.memory[0xFF02] = 0x81 if bind else 0x80
#             for _ in range(10000):
#                 pyboy.tick(1, False, False)
#                 if not pyboy.memory[0xFF02] & 0x80:
#                     break
#                 time.sleep(0.001)
#             else:
#                 raise AssertionError("Second serial transfer timed out")
#             results[bind] = pyboy.memory[0xFF01]
#         except BaseException as error:
#             errors.append(error)
#         finally:
#             if pyboy is not None:
#                 pyboy.stop(save=False)

#     server = threading.Thread(target=handler, args=(True,), daemon=True)
#     client = threading.Thread(target=handler, args=(False,), daemon=True)
#     server.start()
#     client.start()
#     deadline = time.monotonic() + SERIAL_TEST_TIMEOUT
#     server.join(max(0, deadline - time.monotonic()))
#     client.join(max(0, deadline - time.monotonic()))

#     assert not server.is_alive() and not client.is_alive(), "Serial handshake timed out"
#     assert not errors, errors
#     assert results[True] == 0x5A
#     assert results[False] == 0xA5


def _slow_tick(pyboy, ticks):
    for _ in range(ticks):
        pyboy.tick(1, RENDER_SCREEN, False)


def _skip_dialogue(pyboy):
    while pyboy.tilemap_window[18, 16] != 238:  # The text dialog 'arrow'
        pyboy.tick(1, RENDER_SCREEN, False)

    pyboy.button("a")
    _slow_tick(pyboy, 60)


def pyboy_bootstrap_pokemon_trade(ROM, kwargs):
    pyboy = PyBoy(ROM, window="SDL2" if RENDER_SCREEN else "null", sound_emulated=False, log_level="DEBUG", **kwargs)
    pyboy.set_emulation_speed(0)
    pokemon = pyboy.game_wrapper
    try:
        pokemon.start_game()
    except PyBoyInvalidOperationException:  # Raised on save_state when using serial.
        pass

    # pokemon.remove_pokemon(5)
    # pokemon.remove_pokemon(4)
    pokemon.add_pokemon("CHARIZARD", level=10, moves=("WATERFALL",))  # Charizard + Tackle
    pokemon.add_pokemon("MEW", level=10)  # Squirtle

    print(pokemon.party)

    # party = pokemon.party
    # party[0]["level"] = 55
    # pokemon.party = party

    pokemon.set_event_flag("got_pokedex")  # To enable trading
    pokemon.warp("viridian_pokecenter")
    pyboy.tick(50, False, False)  # Do warp

    # Navigate from door to NPC for Cable Club
    for d in "uuurrrrrruurru":
        if d == "u":
            pyboy.button("up", 10)
        elif d == "r":
            pyboy.button("right", 10)
        pyboy.tick(25, False, False)

    return pyboy, pokemon


def pokemon_trade(pokemon_blue_rom, primary, interrupt, shared_memory=None):
    pyboy = None
    try:
        pyboy, pokemon = pyboy_bootstrap_pokemon_trade(
            pokemon_blue_rom, {"serial_shared_memory": shared_memory, "serial_interrupt_based": interrupt}
        )
        _run_pokemon_trade(pyboy, pokemon, primary)
    finally:
        if pyboy is not None:
            pyboy.stop(save=False)


def _run_pokemon_trade(pyboy, pokemon, primary):
    _encode = pyboy.game_wrapper._encode_text
    _decode = lambda x: pyboy.game_wrapper._decode_text(x, skip_invalid=True)
    pyboy.set_emulation_speed(0)

    _slow_tick(pyboy, 30)
    # Cable Club introduction
    for _ in range(2):
        pyboy.button("a", 10)
        _slow_tick(pyboy, 60)

    deadline = time.monotonic() + SERIAL_TEST_TIMEOUT
    while _decode(pyboy.tilemap_window[7:19, 7]) != "TRADE CENTER":
        if time.monotonic() >= deadline:
            raise AssertionError(
                "Pokemon trade did not reach the Trade Center: "
                f"map={pyboy.memory[0xD35E]:#x}, "
                f"status={pyboy.memory[0xFFAA]:#x}, "
                f"sc={pyboy.memory[0xFF02]:#x}"
            )
        pyboy.button("a", 10)
        _slow_tick(pyboy, 30)

    # Enter trade
    pyboy.button("a", 10)
    _slow_tick(pyboy, 60 * 8)

    if primary:  # What side?
        _slow_tick(pyboy, 10)
        pyboy.button("right", 10)
        _slow_tick(pyboy, 30)
        pyboy.button("a", 10)
    else:
        pyboy.button("right", 10)
        _slow_tick(pyboy, 30)
        pyboy.button("a", 10)

    _slow_tick(pyboy, 30)

    deadline = time.monotonic() + SERIAL_TEST_TIMEOUT
    while _decode(pyboy.tilemap_window[4:15, 10]) == "PLEASE WAIT":
        if time.monotonic() >= deadline:
            raise AssertionError(
                "Pokemon trade remained on the Please Wait screen: "
                f"map={pyboy.memory[0xD35E]:#x}, "
                f"status={pyboy.memory[0xFFAA]:#x}, "
                f"sc={pyboy.memory[0xFF02]:#x}"
            )
        pyboy.tick(1, RENDER_SCREEN, False)

    # Trading menu
    blue = _encode("BLUE")
    deadline = time.monotonic() + SERIAL_TEST_TIMEOUT
    while pyboy.tilemap_window[5:9, 0] != blue or pyboy.tilemap_window[5:9, 8] != blue:
        if time.monotonic() >= deadline:
            raise AssertionError("Pokemon trade did not reach the trading menu: ")
        pyboy.tick(1, RENDER_SCREEN, False)

    assert pyboy.tilemap_window[5:9, 0] == blue, "Expected our title 'BLUE'"
    assert pyboy.tilemap_window[5:9, 8] == blue, "Expected opponent title 'BLUE'"

    charizard = _encode("CHARIZARD")
    assert pyboy.tilemap_window[2:11, 1] == charizard, "Expected our first Pokemon to be 'CHARIZARD'"
    assert pyboy.tilemap_window[2:11, 9] == charizard, "Expected opponent first Pokemon to be 'CHARIZARD'"

    mew = _encode("MEW")
    assert pyboy.tilemap_window[2:5, 2] == mew, "Expected our first Pokemon to be 'MEW'"
    assert pyboy.tilemap_window[2:5, 10] == mew, "Expected opponent first Pokemon to be 'MEW'"

    assert np.all(np.asarray(pyboy.tilemap_window[2:11, 3:7]) == 383), "Expected no other Pokemon"
    assert np.all(np.asarray(pyboy.tilemap_window[2:11, 11:15]) == 383), "Expected no other Pokemon"

    if primary:  # What side?
        # Go down one pokemon
        pyboy.button("down", 10)
    _slow_tick(pyboy, 30)

    # Select Pokemon
    pyboy.button("a", 10)
    _slow_tick(pyboy, 30)

    # Select trade
    pyboy.button("right", 10)
    _slow_tick(pyboy, 30)
    pyboy.button("a", 10)
    _slow_tick(pyboy, 30)

    # Dialog
    _skip_dialogue(pyboy)

    # trade_completed = [147, 177, 160, 163, 164, 383, 162, 174, 172, 175, 171, 164, 179, 164, 163, 231]
    deadline = time.monotonic() + SERIAL_TEST_TIMEOUT
    while _decode(pyboy.tilemap_window[1:17, 14]) != "Trade completed!":
        if time.monotonic() >= deadline:
            raise AssertionError("Expected to see the 'Trade completed!' message")

        pyboy.button("a", 20)
        _slow_tick(pyboy, 30)

    pyboy.stop(save=False)


@pytest.mark.parametrize("interrupt", [False, True])
def test_serial_trade(pokemon_blue_rom, interrupt):
    if os.environ.get("GITHUB_ACTIONS"):
        pytest.skip("Pokémon trade integration test is too slow on GitHub Actions")

    shared_memory = SerialSharedMemoryBuffer()

    process1 = multiprocessing.Process(
        target=pokemon_trade,
        args=(pokemon_blue_rom, True, interrupt, shared_memory),
        name="PyBoy1",
    )
    process1.start()

    # Wait for first emulator to come online
    while shared_memory.read(0) == 0:
        time.sleep(0.1)

    deadline = time.monotonic() + SERIAL_TEST_TIMEOUT_TOTAL
    try:
        pokemon_trade(pokemon_blue_rom, False, interrupt, shared_memory)
    finally:
        process1.join(max(0, deadline - time.monotonic()))
        if process1.is_alive():
            process1.terminate()
            process1.join()
        shared_memory.close()

    assert process1.exitcode == 0
