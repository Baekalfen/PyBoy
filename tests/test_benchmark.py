#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from threading import Thread

import pytest

from pyboy import PyBoy
from pyboy.utils import cython_compiled
from pyboy.plugins.game_wrapper_pokemon_gen1_constants import TRAINER_SET_COUNTS

VERBOSE = False
SIMULATION_FRAMES = 5 * 60 * 60
ACTION_FRAMES = 10
PANDORA_HORIZONTAL_FRAMES = 20
BENCHMARK_MODES = [(1, True), (ACTION_FRAMES, False)]


def _run_repeating_actions(pyboy, actions, action_frames, render, frame_count=SIMULATION_FRAMES):
    wrapper = pyboy.game_wrapper
    for frame in range(0, frame_count, action_frames):
        pyboy.button(actions[(frame // action_frames) % len(actions)])
        if not pyboy.tick(min(action_frames, frame_count - frame), render, False):
            return
        if wrapper.game_over():
            wrapper.reset_game()


def _run_pandora_strategy(pyboy, action_frames, render, frame_count=SIMULATION_FRAMES):
    wrapper = pyboy.game_wrapper
    elapsed_frames = 0
    direction = "left"

    while elapsed_frames < frame_count:
        while not wrapper.piece_in_motion() and not wrapper.game_over() and elapsed_frames < frame_count:
            if not pyboy.tick(min(action_frames, frame_count - elapsed_frames), render, False):
                return
            elapsed_frames += min(action_frames, frame_count - elapsed_frames)

        if wrapper.game_over():
            wrapper.reset_game(timer_div=0)
            continue

        for _ in range(PANDORA_HORIZONTAL_FRAMES // action_frames):
            if elapsed_frames >= frame_count:
                return
            pyboy.button(direction)
            if not pyboy.tick(action_frames, render, False):
                return
            elapsed_frames += action_frames
            if wrapper.game_over():
                break

        if wrapper.game_over():
            wrapper.reset_game(timer_div=0)
            direction = "right" if direction == "left" else "left"
            continue

        while not wrapper.block_dropped() and not wrapper.game_over() and elapsed_frames < frame_count:
            pyboy.button("down")
            if not pyboy.tick(action_frames, render, False):
                return
            elapsed_frames += action_frames

        if wrapper.game_over():
            wrapper.reset_game(timer_div=0)
            direction = "right" if direction == "left" else "left"
            continue
        direction = "right" if direction == "left" else "left"


@pytest.mark.benchmark(group="2048")
@pytest.mark.parametrize("action_frames, render", BENCHMARK_MODES, ids=["full_render", "batched"])
def test_game_2048_left_down(benchmark, gb2048_file, action_frames, render):
    def run():
        pyboy = PyBoy(gb2048_file, window="GLFW" if VERBOSE else "null", sound_emulated=False)
        try:
            pyboy.set_emulation_speed(1 if VERBOSE else 0)
            pyboy.game_wrapper.start_game()
            _run_repeating_actions(pyboy, ("left", "down"), action_frames, render)
        finally:
            pyboy.stop(save=False)

    benchmark(run)


@pytest.mark.benchmark(group="pandoras_blocks")
@pytest.mark.parametrize("action_frames, render", BENCHMARK_MODES, ids=["full_render", "batched"])
def test_game_pandoras_blocks_left_right(benchmark, pandorasblocks_file, action_frames, render):
    def run():
        pyboy = PyBoy(pandorasblocks_file, window="GLFW" if VERBOSE else "null", sound_emulated=False)
        try:
            pyboy.set_emulation_speed(1 if VERBOSE else 0)
            pyboy.game_wrapper.start_game(timer_div=0)
            _run_pandora_strategy(pyboy, action_frames, render)
        finally:
            pyboy.stop(save=False)

    benchmark(run)


@pytest.mark.benchmark(group="pokemon")
@pytest.mark.parametrize("action_frames, render", BENCHMARK_MODES, ids=["full_render", "batched"])
def test_game_pokemon_trainers(benchmark, pokemon_blue_rom, action_frames, render):
    MAX_TRAINER_BATTLE_STEPS = 10000
    POKEMON_BATTLE_STATE_ADDRESS = 0xD057
    MEWTWO_LEVEL = 100
    MEWTWO_EXP = 1_250_000
    MEWTWO_MAX_HP = 999
    MEWTWO_STATS = {"attack": 999, "defense": 999, "speed": 999, "special": 999}

    def _restore_party_health(wrapper):
        party = wrapper.party
        for pokemon in party:
            pokemon["hp"] = pokemon["max_hp"]
            pokemon["status"] = 0
            pokemon["pp"] = tuple(35 if move else 0 for move in pokemon["moves"])
        wrapper.party = party

    def _run_trainer_battle(pyboy):
        battle_started = False
        battle_frames = 0
        while battle_frames < MAX_TRAINER_BATTLE_STEPS:
            if battle_frames % 2 == 0:
                pyboy.button("a", 1)
            assert pyboy.tick(action_frames, render, False)
            battle_frames += action_frames
            in_battle = pyboy.memory[POKEMON_BATTLE_STATE_ADDRESS] != 0
            if in_battle:
                battle_started = True
            elif battle_started:
                return
        raise AssertionError("Trainer battle did not return to the overworld")

    def run():
        pyboy = PyBoy(pokemon_blue_rom, window="GLFW" if VERBOSE else "null", sound_emulated=False)
        try:
            pyboy.set_emulation_speed(1 if VERBOSE else 0)
            wrapper = pyboy.game_wrapper
            wrapper.start_game()
            for badge in ("boulder", "cascade", "thunder", "rainbow", "soul", "marsh", "volcano", "earth"):
                wrapper.set_badge(badge)
            wrapper.add_pokemon(
                "MEWTWO",
                level=MEWTWO_LEVEL,
                exp=MEWTWO_EXP,
                max_hp=MEWTWO_MAX_HP,
                stats=MEWTWO_STATS,
                moves=("FIRE_PUNCH", "HYDRO_PUMP", "FIRE_BLAST", "HYPER_FANG"),
            )

            # Run every single trainer battle in the game. Even Prof. Oak
            trainer_sets = list(TRAINER_SET_COUNTS.items())
            if benchmark.disabled:
                trainer_sets = trainer_sets[:3]
            for trainer, trainer_set_count in trainer_sets:
                for n in range(trainer_set_count):
                    wrapper.start_trainer_battle(trainer, trainer_set=n + 1)
                    _run_trainer_battle(pyboy)
                    _restore_party_health(wrapper)
        finally:
            pyboy.stop(save=False)

    benchmark(run)


@pytest.mark.benchmark(group="nogil")
def test_threads_baseline(benchmark, default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    benchmark(pyboy.tick, 2000, False)


@pytest.mark.skipif(not cython_compiled, reason="No-GIL is only relevant for Cython")
@pytest.mark.benchmark(group="nogil")
@pytest.mark.parametrize("count", [1, 2, 4])
def test_threads_nogil(benchmark, count, default_rom):
    # Threaded run with no GIL. Should result in roughly same time.
    def thread_run():
        pyboy = PyBoy(default_rom, window="null")
        pyboy.set_emulation_speed(0)
        pyboy.tick(2000, False, False)

    def bench():
        threads = [Thread(target=thread_run) for _ in range(count)]
        for t in threads:
            t.start()

        for t in threads:
            t.join()

    benchmark(bench)
