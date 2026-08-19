#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import PIL
import PIL.Image
from pyboy import PyBoy
from pathlib import Path
import os
from pyboy.plugins.game_wrapper_pokemon_gen1_constants import (
    BAG_ITEM_COUNT_ADDRESS,
    BAG_ITEMS_ADDRESS,
    EVENT_FLAGS,
    EVENT_FLAGS_ADDRESS,
    MAX_MONEY,
    OBTAINED_BADGES_ADDRESS,
    PLAYER_MONEY_ADDRESS,
    POKEMON_TEXT_ENCODING,
)

OVERWRITE_PNGS = False

CURRENT_MAP_ADDRESS = 0xD35E
WARP_DESTINATION_MAP_ADDRESS = 0xFF8B
STATUS_FLAGS3_ADDRESS = 0xD72D
STATUS_FLAGS3_WARP_FROM_CURRENT_SCRIPT = 1 << 3
PARTY_SPECIES_ADDRESS = 0xD164
PARTY_MON_ADDRESS = 0xD16B
PARTY_MON_SIZE = 0x2C
PARTY_MON_HP_OFFSET = 1
PARTY_SPECIES_SENTINEL = 0xFF


def check_image(image, path):
    png_path = Path(f"tests/test_results/pokemon_blue/{path}.png")
    if OVERWRITE_PNGS:
        png_path.parents[0].mkdir(parents=True, exist_ok=True)
        image.save(png_path)
    else:
        assert png_path.exists(), "Test result doesn't exist"
        # Converting to RGB as ImageChops.difference cannot handle Alpha: https://github.com/python-pillow/Pillow/issues/4849
        old_image = PIL.Image.open(png_path).convert("RGB")
        diff = PIL.ImageChops.difference(image.convert("RGB"), old_image)

        if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
            image.show()
            old_image.show()
            diff.show()
        assert not diff.getbbox(), f"Images are different! {path}"


def test_pokemon_basics(pokemon_blue_rom):
    pyboy = PyBoy(pokemon_blue_rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.game_wrapper.start_game()

    # In mom's house
    pyboy.tick()
    check_image(pyboy.screen.image, "house")
    pyboy.button("start")
    pyboy.tick(30, True, False)
    check_image(pyboy.screen.image, "start_menu")
    pyboy.button("start")
    pyboy.tick(30, True, False)
    check_image(pyboy.screen.image, "house")
    pyboy.stop(save=False)


def test_pokemon_warp(pokemon_blue_rom):
    pyboy = PyBoy(pokemon_blue_rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.game_wrapper.start_game()

    pyboy.game_wrapper.warp("viridian_pokecenter")
    assert pyboy.memory[WARP_DESTINATION_MAP_ADDRESS] == 0x29
    assert pyboy.memory[STATUS_FLAGS3_ADDRESS] & STATUS_FLAGS3_WARP_FROM_CURRENT_SCRIPT
    pyboy.tick(120, False, False)
    assert pyboy.memory[CURRENT_MAP_ADDRESS] == 0x29

    pyboy.stop(save=False)


def test_pokemon_event_flag(pokemon_blue_rom):
    pyboy = PyBoy(pokemon_blue_rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.game_wrapper.start_game()

    pyboy.game_wrapper.set_event_flag("got_pokedex")
    event = EVENT_FLAGS["got_pokedex"]
    assert pyboy.memory[EVENT_FLAGS_ADDRESS + event // 8] & (1 << (event % 8))

    # Open start-menu to validate pokedex
    pyboy.button("start", 10)
    pyboy.tick(30, False, False)
    assert pyboy.tilemap_window[12:19, 2] == pyboy.game_wrapper._encode_text("POKéDEX")
    # Close start-menu
    pyboy.button("start", 10)
    pyboy.tick(30, False, False)

    pyboy.game_wrapper.reset_event_flag("got_pokedex")
    assert not pyboy.memory[EVENT_FLAGS_ADDRESS + event // 8] & (1 << (event % 8))

    # Open start-menu to validate pokedex removal
    pyboy.button("start", 10)
    pyboy.tick(30, False, False)
    assert pyboy.tilemap_window[12:19, 2] != pyboy.game_wrapper._encode_text("POKéDEX")

    pyboy.stop(save=False)


def test_pokemon_badges_are_separate_from_event_flags(pokemon_blue_rom):
    pyboy = PyBoy(pokemon_blue_rom, window="null")
    pyboy.set_emulation_speed(0)
    wrapper = pyboy.game_wrapper
    wrapper.start_game()

    wrapper.set_event_flag("beat_brock")
    event = EVENT_FLAGS["beat_brock"]
    assert pyboy.memory[EVENT_FLAGS_ADDRESS + event // 8] & (1 << (event % 8))
    assert pyboy.memory[OBTAINED_BADGES_ADDRESS] == 0

    wrapper.set_badge("boulder")
    assert pyboy.memory[OBTAINED_BADGES_ADDRESS] == 1
    wrapper.set_badge(7)
    assert pyboy.memory[OBTAINED_BADGES_ADDRESS] == 0x81

    wrapper.reset_badge("boulder")
    assert pyboy.memory[OBTAINED_BADGES_ADDRESS] == 0x80

    pyboy.stop(save=False)


def test_pokemon_money_and_inventory(pokemon_blue_rom):
    pyboy = PyBoy(pokemon_blue_rom, window="null")
    wrapper = pyboy.game_wrapper

    wrapper.set_money(MAX_MONEY)
    assert wrapper.money == MAX_MONEY
    assert [pyboy.memory[PLAYER_MONEY_ADDRESS + offset] for offset in range(3)] == [0x99, 0x99, 0x99]

    wrapper.set_inventory({"POTION": 20, "MASTER_BALL": 1})
    assert wrapper.inventory == [{"item": 0x14, "quantity": 20}, {"item": 1, "quantity": 1}]
    assert pyboy.memory[BAG_ITEM_COUNT_ADDRESS] == 2
    assert pyboy.memory[BAG_ITEMS_ADDRESS + 4] == 0xFF

    wrapper.set_item("POTION", 99)
    wrapper.remove_item("MASTER_BALL")
    assert wrapper.inventory == [{"item": 0x14, "quantity": 99}]
    wrapper.set_item("POTION", 0)
    assert wrapper.inventory == []

    wrapper.set_item("POTION", 255, force=True)
    assert wrapper.inventory == [{"item": 0x14, "quantity": 255}]
    wrapper.set_item("MASTER_BALL", 1)
    assert wrapper.inventory == [{"item": 0x14, "quantity": 255}, {"item": 1, "quantity": 1}]
    wrapper.remove_item("POTION", 1)
    assert wrapper.inventory == [{"item": 0x14, "quantity": 254}, {"item": 1, "quantity": 1}]
    wrapper.remove_item("POTION", 254)
    wrapper.remove_item("MASTER_BALL")
    assert wrapper.inventory == []

    pyboy.stop(save=False)


def test_pokemon_text_codec(pokemon_blue_rom):
    pyboy = PyBoy(pokemon_blue_rom, window="null")

    pokedex = [143, 142, 138, 186, 131, 132, 151]
    assert pyboy.game_wrapper._encode_text("POKéDEX") == pokedex
    assert pyboy.game_wrapper._decode_text(pokedex) == "POKéDEX"

    text = "Hello, WORLD! 123 <PKMN>"
    encoded = pyboy.game_wrapper._encode_text(text, terminate=True)
    assert encoded[-1] == POKEMON_TEXT_ENCODING["@"]
    assert pyboy.game_wrapper._decode_text(encoded) == text

    pyboy.stop(save=False)


def test_pokemon_party_controls(pokemon_blue_rom):
    pyboy = PyBoy(pokemon_blue_rom, window="null")
    wrapper = pyboy.game_wrapper

    wrapper.add_pokemon(0xB0, level=50)
    wrapper.add_pokemon("SQUIRTLE", level=45, moves=("TACKLE", "POUND"))
    wrapper.add_pokemon(0xB2, level=40, moves=())
    assert [pokemon["species"] for pokemon in wrapper.party] == [0xB0, 0xB1, 0xB2]
    assert wrapper.party[0]["level"] == 50
    assert wrapper.party[2]["moves"] == (0, 0, 0, 0)
    assert wrapper.party[2]["pp"] == (0, 0, 0, 0)
    assert wrapper.party[1]["nickname"] == tuple(0x80 + ord(character) - ord("A") for character in "SQUIRTLE")
    third_mon = PARTY_MON_ADDRESS + 2 * PARTY_MON_SIZE
    assert pyboy.memory[third_mon + PARTY_MON_HP_OFFSET] == 0
    assert pyboy.memory[third_mon + PARTY_MON_HP_OFFSET + 1] == 90
    assert wrapper.party[0]["nickname"]
    assert pyboy.memory[PARTY_SPECIES_ADDRESS + len(wrapper.party)] == PARTY_SPECIES_SENTINEL

    party = wrapper.party
    party[0]["level"] = 55
    wrapper.party = party
    assert wrapper.party[0]["level"] == 55

    wrapper.remove_pokemon(0)
    assert [pokemon["species"] for pokemon in wrapper.party] == [0xB1, 0xB2]

    pyboy.stop(save=False)
