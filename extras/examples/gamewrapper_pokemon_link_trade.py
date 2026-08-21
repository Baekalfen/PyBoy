#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import glob
import multiprocessing
import os
import shutil
import sys
import time


# Makes us able to import PyBoy from the directory below.
file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, file_path + "/../..")

from pyboy import PyBoy  # noqa: E402
from pyboy.core.serial import SerialSharedMemoryBuffer  # noqa: E402
from pyboy.utils import PyBoyInvalidOperationException, WindowEvent  # noqa: E402


RENDER_SCREEN = "--headless" not in sys.argv
SERIAL_TIMEOUT = 60
try:
    SCREENSHOT_DIR = sys.argv[sys.argv.index("--screenshots") + 1]
except (ValueError, IndexError):
    SCREENSHOT_DIR = None


def _save_screenshot(pyboy, name):
    if SCREENSHOT_DIR is not None:
        pyboy.screen.image.save(os.path.join(SCREENSHOT_DIR, f"PokemonLinkTrade-{name}.png"))


def _copy_recording(pyboy):
    if SCREENSHOT_DIR is None:
        return

    recordings = glob.glob(os.path.join("recordings", f"{pyboy.cartridge_title}-*.gif"))
    if not recordings:
        raise RuntimeError(f"Couldn't find a recording for cartridge {pyboy.cartridge_title!r}")

    recording = max(recordings, key=os.path.getmtime)
    shutil.copy2(recording, os.path.join(SCREENSHOT_DIR, "PokemonLinkTrade.gif"))


def _tick(pyboy, ticks):
    for _ in range(ticks):
        pyboy.tick(1, RENDER_SCREEN, False)


def _prepare_player(rom, shared_memory):
    pyboy = PyBoy(
        rom,
        window="SDL2" if RENDER_SCREEN else "null",
        sound_emulated=False,
        serial_shared_memory=shared_memory,
        serial_interrupt_based=True,
        log_level="DEBUG",
    )
    pyboy.set_emulation_speed(0)
    pokemon = pyboy.game_wrapper

    try:
        pokemon.start_game()
    except PyBoyInvalidOperationException:
        # Serial connections do not support save states, which start_game uses
        pass

    pokemon.add_pokemon("CHARIZARD", level=10, moves=("WATERFALL",))
    pokemon.add_pokemon("MEW", level=10)
    print(pokemon.party)
    pokemon.set_event_flag("got_pokedex")
    pokemon.warp("viridian_pokecenter")
    pyboy.tick(50, RENDER_SCREEN, False)

    # Walk from the Pokécenter entrance to the Cable Club NPC.
    for direction in "uuurrrrrruurru":
        pyboy.button({"u": "up", "r": "right"}[direction], 10)
        pyboy.tick(25, RENDER_SCREEN, False)

    return pyboy, pokemon


def _skip_dialogue(pyboy):
    deadline = time.monotonic() + SERIAL_TIMEOUT
    while pyboy.tilemap_window[18, 16] != 238:
        if time.monotonic() >= deadline:
            raise RuntimeError("Timed out waiting for the Cable Club dialogue")
        _tick(pyboy, 1)
    pyboy.button("a")
    _tick(pyboy, 60)


def _trade(rom, shared_memory, primary):
    pyboy = None
    trade_completed = False
    try:
        pyboy, pokemon = _prepare_player(rom, shared_memory)
        pyboy.set_emulation_speed(0)
        decode = lambda value: pokemon._decode_text(value, skip_invalid=True)

        # Enter the Cable Club and wait until the Trade Center is selected.
        _tick(pyboy, 30)
        for _ in range(2):
            pyboy.button("a", 10)
            _tick(pyboy, 60)

        deadline = time.monotonic() + SERIAL_TIMEOUT
        while decode(pyboy.tilemap_window[7:19, 7]) != "TRADE CENTER":
            if time.monotonic() >= deadline:
                raise RuntimeError("Timed out entering the Trade Center")
            pyboy.button("a", 10)
            _tick(pyboy, 30)

        pyboy.button("a", 10)
        _tick(pyboy, 60 * 8)
        if primary:
            _save_screenshot(pyboy, "connection")

        # The two players occupy different sides of the initial link menu.
        if primary:
            _tick(pyboy, 10)
        pyboy.button("right", 10)
        _tick(pyboy, 30)
        pyboy.button("a", 10)
        _tick(pyboy, 30)

        deadline = time.monotonic() + SERIAL_TIMEOUT
        while decode(pyboy.tilemap_window[4:15, 10]) == "PLEASE WAIT":
            if time.monotonic() >= deadline:
                raise RuntimeError("Timed out waiting for the other player")
            _tick(pyboy, 1)

        blue = pokemon._encode_text("BLUE")
        deadline = time.monotonic() + SERIAL_TIMEOUT
        while pyboy.tilemap_window[5:9, 0] != blue or pyboy.tilemap_window[5:9, 8] != blue:
            if time.monotonic() >= deadline:
                raise RuntimeError("Timed out waiting for the trading menu")
            _tick(pyboy, 1)
        _tick(pyboy, 30)
        if primary:
            _save_screenshot(pyboy, "trading-menu")

        # Select the first Pokémon and confirm the trade.
        if primary:
            pyboy.button("down", 10)
            _tick(pyboy, 30)
        pyboy.button("a", 10)
        _tick(pyboy, 30)
        pyboy.button("right", 10)
        _tick(pyboy, 30)
        pyboy.button("a", 10)
        _tick(pyboy, 30)
        _skip_dialogue(pyboy)

        deadline = time.monotonic() + SERIAL_TIMEOUT
        transfer_ticks = 0
        while decode(pyboy.tilemap_window[1:17, 14]) != "Trade completed!":
            if time.monotonic() >= deadline:
                raise RuntimeError("Timed out waiting for the trade to complete")
            pyboy.button("a", 20)
            _tick(pyboy, 30)
            transfer_ticks += 1

            if primary:
                if transfer_ticks in (10, 85):
                    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)

        trade_completed = True
        print(f"Player {1 if primary else 2}: trade completed")
    finally:
        if pyboy is not None:
            pyboy.stop(save=False)
            if primary and trade_completed:
                _copy_recording(pyboy)


def main():
    roms = []
    skip_argument = False
    for argument in sys.argv[1:]:
        if skip_argument:
            skip_argument = False
        elif argument == "--screenshots":
            skip_argument = True
        elif not argument.startswith("--"):
            roms.append(argument)
    if len(roms) != 1:
        print("Usage: python gamewrapper_pokemon_link_trade.py ROM [--headless] [--screenshots DIR]", file=sys.stderr)
        return 1

    if SCREENSHOT_DIR is not None:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    shared_memory = SerialSharedMemoryBuffer()
    process = multiprocessing.Process(
        target=_trade,
        args=(roms[0], shared_memory, True),
        name="PyBoy-player-1",
    )
    process.start()

    while shared_memory.read(0) == 0:
        time.sleep(0.1)

    try:
        _trade(roms[0], shared_memory, False)
    finally:
        process.join(SERIAL_TIMEOUT)
        if process.is_alive():
            process.terminate()
            process.join()
        shared_memory.close()

    if process.exitcode != 0:
        raise RuntimeError(f"Player 1 exited with status {process.exitcode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
