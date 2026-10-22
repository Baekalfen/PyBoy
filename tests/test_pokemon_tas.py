"""Pokémon semantic TAS recording and replay used by the PGO pytest workload."""

import hashlib
import io
import json
from collections import deque
from contextlib import ExitStack, contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from pyboy import PyBoy
from pyboy.plugins.game_wrapper_pokemon_gen1_constants import (
    BATTLE_MON_ADDRESS,
    BATTLE_MON_HP_OFFSET,
    BATTLE_MON_MAX_HP_OFFSET,
    BATTLE_MON_MOVES_OFFSET,
    BATTLE_MON_PP_OFFSET,
    MAP_NAMES,
    PARTY_COUNT_ADDRESS,
    PARTY_LENGTH,
    PARTY_MON_HP_OFFSET,
    PARTY_MON_MAX_HP_OFFSET,
    PARTY_MON_MOVES_OFFSET,
    PARTY_MON_PP_OFFSET,
    PARTY_MON_SIZE,
    PARTY_MONS_ADDRESS,
    PLAYER_FACING_DIRECTIONS,
    PLAYER_FACING_DIRECTION_OFFSET,
    PLAYER_SPRITE_STATE_ADDRESS,
)
from pyboy.utils import WindowEvent


DEFAULT_ACTION_FRAME_SKIP = 24
MOVEMENT_FRAMES = 48
WALK_WAYPOINT_TILES = 3
SCENE_STABILITY_FRAMES = 3
DIRECTION_DELTAS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
DELTA_DIRECTIONS = {delta: direction for direction, delta in DIRECTION_DELTAS.items()}
INPUT_EVENTS = (
    (WindowEvent.PRESS_ARROW_UP, WindowEvent.RELEASE_ARROW_UP, "up"),
    (WindowEvent.PRESS_ARROW_DOWN, WindowEvent.RELEASE_ARROW_DOWN, "down"),
    (WindowEvent.PRESS_ARROW_LEFT, WindowEvent.RELEASE_ARROW_LEFT, "left"),
    (WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.RELEASE_ARROW_RIGHT, "right"),
    (WindowEvent.PRESS_BUTTON_A, WindowEvent.RELEASE_BUTTON_A, "a"),
    (WindowEvent.PRESS_BUTTON_B, WindowEvent.RELEASE_BUTTON_B, "b"),
    (WindowEvent.PRESS_BUTTON_START, WindowEvent.RELEASE_BUTTON_START, "start"),
    (WindowEvent.PRESS_BUTTON_SELECT, WindowEvent.RELEASE_BUTTON_SELECT, "select"),
)
BUTTON_ACTIONS = {
    "battle": {"a": "confirm", "b": "cancel", "start": "start", "select": "select"},
    "dialogue": {"a": "advance", "b": "advance", "start": "start", "select": "select"},
    "menu": {"a": "confirm", "b": "back", "start": "close", "select": "select"},
    "overworld": {"a": "interact", "b": "back", "start": "open_menu", "select": "select"},
}


class PokemonBlueState:
    def __init__(self, pyboy):
        self.pyboy = pyboy
        self.waiting = False
        self.generation = 0
        self.completed = 0
        self.tilemap = pyboy.symbol_lookup("wTileMap")[1]
        bank, start = pyboy.symbol_lookup("WaitForTextScrollButtonPress")
        manual_bank, manual = pyboy.symbol_lookup("ManualTextScroll")
        end = manual - 1
        assert bank == manual_bank == 0 and start < end
        assert (pyboy.memory[bank, start], pyboy.memory[bank, manual], pyboy.memory[bank, end]) == (0xF0, 0xFA, 0xC9)
        self.hooks = []
        for address, callback in ((start, self._start_wait), (end, self._end_wait)):
            pyboy.hook_register(bank, address, callback, self)
            self.hooks.append((bank, address))

    @staticmethod
    def _start_wait(context):
        context.waiting = True
        context.generation += 1

    @staticmethod
    def _end_wait(context):
        if context.waiting:
            context.waiting = False
            context.completed = context.generation

    def close(self):
        for bank, address in reversed(self.hooks):
            self.pyboy.hook_deregister(bank, address)
        self.hooks.clear()

    def read(self, symbol):
        return self.pyboy.memory[self.pyboy.symbol_lookup(symbol)[1]]

    def pointer(self, symbol):
        address = self.pyboy.symbol_lookup(symbol)[1]
        return int.from_bytes(self.pyboy.memory[address : address + 2], "little")

    def walkable_tiles(self):
        memory = self.pyboy.memory
        width, height = self.read("wCurMapWidth"), self.read("wCurMapHeight")
        base = self.pyboy.symbol_lookup("wOverworldMap")[1]
        stride = width + 6
        blocks = [
            block
            for y in range(height)
            for block in memory[base + (y + 3) * stride + 3 : base + (y + 3) * stride + 3 + width]
        ]
        bank = self.read("wTilesetBank")
        pointer = self.pointer("wTilesetBlocksPtr")
        tiles = memory[0 if pointer < 0x4000 else bank, pointer : pointer + (max(blocks) + 1) * 16]
        pointer = self.pointer("wTilesetCollisionPtr")
        collision_bank = 0 if pointer < 0x4000 else bank
        passable = set()
        while (tile := memory[collision_bank, pointer]) != 0xFF:
            passable.add(tile)
            pointer += 1
        grass = self.read("wGrassTile")
        if grass != 0xFF:
            passable.add(grass)
        # Each block contains four movement cells, tested at their bottom-left graphics tile.
        return {
            (2 * (index % width) + x, 2 * (index // width) + y)
            for index, block in enumerate(blocks)
            for y in range(2)
            for x in range(2)
            if tiles[block * 16 + 4 + y * 8 + x * 2] in passable
        }

    def occupied_tiles(self):
        occupied = set()
        for index in range(1, self.read("wNumSprites") + 1):
            prefix = f"wSprite{index:02d}StateData"
            if not self.read(prefix + "1PictureID") or self.read(prefix + "1ImageIndex") == 0xFF:
                continue
            # Sprite map coordinates include a four-tile border.
            x, y = self.read(prefix + "2MapX") - 4, self.read(prefix + "2MapY") - 4
            occupied.add((x, y))
            if self.read(prefix + "2WalkAnimationCounter"):
                dx = (self.read(prefix + "1XStepVector") + 128) % 256 - 128
                dy = (self.read(prefix + "1YStepVector") + 128) % 256 - 128
                occupied.add((x - dx, y - dy))
        return occupied

    def snapshot(self):
        pyboy, memory = self.pyboy, self.pyboy.memory
        values = {name: self.read(name) for name in ("wStatusFlags5", "wFontLoaded", "hWY", "hTextID")}
        dialogue_open = bool(values["wFontLoaded"] & 1 and values["hWY"] == 0 and values["hTextID"])
        window_visible = bool(memory[0xFF40] & 0x20 and memory[0xFF4A] < 144 and memory[0xFF4B] < 167)
        dialogue_box = (
            window_visible
            and tuple(memory[self.tilemap + offset] for offset in (240, 259, 340, 359)) == (0x79, 0x7B, 0x7D, 0x7E)
            or dialogue_open
            or self.waiting
        )
        cursor = self.pointer("wMenuCursorLocation")
        offset = cursor - self.tilemap
        menu_cursor = (
            (offset % 20, offset // 20)
            if window_visible
            and 0 <= offset < 360
            and memory[cursor] == 0xED
            # The RAM cursor is written before the window tiles are copied.
            and pyboy.tilemap_window[offset % 20, offset // 20] == 0xED
            else None
        )
        in_battle = bool(memory[0xD057])
        if in_battle:
            scene = "battle"
        elif menu_cursor is not None:
            scene = "menu"
        elif dialogue_box:
            scene = "dialogue"
        else:
            scene = "menu" if window_visible else "overworld"
        return {
            "scripted": bool(values["wStatusFlags5"] & 0x80),
            "dialogue_open": dialogue_open,
            "text_id": values["hTextID"],
            "waiting": self.waiting,
            "generation": self.generation,
            "completed": self.completed,
            "scene": scene,
            "window_visible": window_visible,
            "dialogue_box": dialogue_box,
            "menu_cursor": menu_cursor,
            "map_id": memory[0xD35E],
            "position": (memory[0xD362], memory[0xD361]),
            "facing": PLAYER_FACING_DIRECTIONS.get(
                memory[PLAYER_SPRITE_STATE_ADDRESS + PLAYER_FACING_DIRECTION_OFFSET]
            ),
            "opponent_id": memory[0xD059] if in_battle else None,
        }


class SemanticPokemonRecorder:
    def __init__(self, source_state, output):
        self.output, self.source_state = output, source_state
        self.frame_index = 0
        self.held = {}
        self.pending_buttons = {}
        self.buffer = []
        self.last_release = None
        self.last_dialogue_button = None
        self.press_generations = {}
        self.consumed_generation = None
        self.direction = None
        self.previous_state = source_state.snapshot()
        self.stable_scene = self.previous_state["scene"]
        self.pending_scene = None
        self.pending_scene_frames = 0

    def _fields(self, state):
        map_info = {"id": state["map_id"]}
        if state["map_id"] in MAP_NAMES:
            map_info["name"] = MAP_NAMES[state["map_id"]]
        fields = {"map": map_info, "position": list(state["position"])}
        if state.get("opponent_id") is not None:
            fields["opponent_id"] = state["opponent_id"]
        return fields

    def _write(self, record):
        self.buffer.append(record)
        self._flush()

    def _flush(self):
        if not self.pending_buttons:
            for record in self.buffer:
                self.output.write(json.dumps(record, separators=(",", ":")) + "\n")
            self.output.flush()
            self.buffer.clear()

    def _queue_button(self, button, record):
        if button in self.pending_buttons:
            return
        if self.last_release is not None:
            delay = max(0, self.held.get(button, self.frame_index) - self.last_release)
            if delay:
                record["delay_before_press_frames"] = delay
        self.pending_buttons[button] = record, self.frame_index
        self._write(record)

    def _release_button(self, button):
        pending = self.pending_buttons.pop(button, None)
        if pending is not None:
            record, frame = pending
            record["press_frames"] = max(1, self.frame_index - frame)
        self._flush()

    def _input_scene(self, state, button):
        scene = state["scene"]
        if scene == self.stable_scene:
            return scene
        if button in {"a", "b"} and self.stable_scene == "dialogue" and scene == "overworld":
            return "dialogue"
        if scene == "battle" or (scene == "menu" and state["window_visible"]):
            return scene
        if scene == "dialogue" and state["dialogue_box"]:
            return scene
        print(f"Ignoring {button.upper()} during scene transition from {self.stable_scene} to {scene}.")
        return None

    def _record_advance(self, state, button):
        previous_generation = self.consumed_generation
        self.consumed_generation = state["generation"]
        record = {
            "record": "action",
            "kind": "dialogue",
            "action": "advance",
            **self._fields(state),
            "button": button,
            "ready": state["waiting"],
        }
        if state["dialogue_open"]:
            accepted = state["generation"] > 0 and (
                state["waiting"] or button == "a" and state["completed"] == state["generation"] != previous_generation
            )
            if accepted:
                record.update(ready=True, accepted_wait_generation=state["generation"])
            elif not state["waiting"]:
                record.update(ready=True, press_before_wait=True, press_before_wait_text_id=state["text_id"])
        self._queue_button(button, record)

    def capture_input_events(self, events, before, after):
        reconciled = False
        for event in events:
            for press, release, button in INPUT_EVENTS:
                if event == release:
                    self.held.pop(button, None)
                    self._release_button(button)
                    self.press_generations.pop(button, None)
                    self.last_release = self.frame_index
                    if button == self.last_dialogue_button:
                        self.last_dialogue_button = next((key for key in ("a", "b") if key in self.held), None)
                    break
                if event != press or button in self.held:
                    continue
                self.held[button] = self.frame_index
                state = before.copy()
                scene = self._input_scene(state, button)
                if scene is None:
                    break
                state["scene"] = scene
                if (
                    button in {"a", "b"}
                    and not reconciled
                    and scene == "dialogue"
                    and after["generation"] != state["generation"]
                    and (after["waiting"] or after["completed"] == after["generation"])
                ):
                    state.update(waiting=True, generation=after["generation"])
                    reconciled = True
                if button in {"a", "b"}:
                    self.last_dialogue_button = button
                    self.press_generations[button] = state["generation"]
                if button in DIRECTION_DELTAS:
                    self._start_direction(button, state)
                else:
                    self._finish_direction(after)
                    action = BUTTON_ACTIONS[scene][button]
                    if action == "advance":
                        if state["waiting"] and state["generation"] != self.consumed_generation:
                            self._record_advance(state, button)
                    else:
                        record = {
                            "record": "action",
                            "kind": scene,
                            "action": action,
                            **self._fields(state),
                            "button": button,
                        }
                        if action == "interact" and state["facing"] in DIRECTION_DELTAS:
                            record["facing"] = state["facing"]
                        self._queue_button(button, record)
                break

    def _start_direction(self, button, state, discontinuity=False):
        self._finish_direction(state)
        self.direction = {
            "button": button,
            "scene": state["scene"],
            "map_id": state["map_id"],
            "from": state["position"],
            "to": state["position"],
            "last_direction": None,
            "discontinuity": discontinuity,
            "suppress_face": False,
            "cursors": [state["menu_cursor"]] if state["menu_cursor"] is not None else [],
        }

    def _update_direction(self, state):
        action = self.direction
        if state["map_id"] == action["map_id"] and state["position"] != action["to"]:
            delta = tuple(end - start for start, end in zip(action["to"], state["position"]))
            if action["discontinuity"] and sum(map(abs, delta)) > 1:
                action["from"] = state["position"]
            action["discontinuity"] = False
            action["last_direction"] = DELTA_DIRECTIONS.get(delta, action["last_direction"])
            action["to"] = state["position"]
        cursor = state["menu_cursor"]
        if cursor is not None and (not action["cursors"] or cursor != action["cursors"][-1]):
            action["cursors"].append(cursor)

    def _finish_direction(self, state):
        if self.direction is None:
            return
        self._update_direction(state)
        action, self.direction = self.direction, None
        if action["scene"] != "overworld" and len(action["cursors"]) <= 1:
            return
        record = {
            "record": "action",
            "kind": action["scene"],
            "button": action["last_direction"] or action["button"],
            **self._fields({"map_id": action["map_id"], "position": action["from"]}),
        }
        if action["scene"] == "overworld":
            tiles = sum(abs(end - start) for start, end in zip(action["from"], action["to"]))
            if not tiles and action["suppress_face"]:
                return
            record.update(action="walk" if tiles else "face", tiles=tiles)
            record.update({"from": list(action["from"]), "to": list(action["to"])})
            record.pop("position")
        else:
            record.update(action="navigate", steps=len(action["cursors"]) - 1)
        self._write(record)

    def observe(self, state):
        old_scene = self.stable_scene
        if state["scene"] == self.stable_scene:
            self.pending_scene, self.pending_scene_frames = None, 0
        else:
            self.pending_scene_frames = self.pending_scene_frames + 1 if state["scene"] == self.pending_scene else 1
            self.pending_scene = state["scene"]
            if self.pending_scene_frames >= SCENE_STABILITY_FRAMES:
                self.stable_scene = state["scene"]
                self.pending_scene, self.pending_scene_frames = None, 0
        continuation = None
        if self.direction is not None:
            self._update_direction(state)
            changed = self.stable_scene != self.direction["scene"] or state["map_id"] != self.direction["map_id"]
            waypoint = (
                self.direction["scene"] == "overworld"
                and _distance(self.direction["from"], self.direction["to"]) >= WALK_WAYPOINT_TILES
                and self.source_state.read("wWalkCounter") == 0
            )
            if changed or waypoint:
                if self.direction["button"] in self.held:
                    continuation = self.direction["button"], changed
                self._finish_direction(state)
        if state["map_id"] != self.previous_state["map_id"]:
            self._write(
                {
                    "record": "transition",
                    "kind": "map",
                    "from_map": self.previous_state["map_id"],
                    "to_map": state["map_id"],
                    "position": list(state["position"]),
                }
            )
        if self.stable_scene != old_scene:
            self._write(
                {
                    "record": "transition",
                    "kind": "scene",
                    "from": old_scene,
                    "to": self.stable_scene,
                    **self._fields(state),
                }
            )
        if state["scene"] == "dialogue":
            button = self.last_dialogue_button
            if (
                state["generation"] != self.consumed_generation
                and (state["waiting"] or state["completed"] == state["generation"] != self.previous_state["completed"])
                and button in self.held
                and self.press_generations[button] == state["generation"]
            ):
                self._record_advance(state, button)
        elif self.stable_scene != "dialogue":
            self.consumed_generation = None
        if continuation is not None:
            self._start_direction(continuation[0], state, discontinuity=continuation[1])
            self.direction["suppress_face"] = not continuation[1]
        self.previous_state = state

    def close(self):
        self._finish_direction(self.source_state.snapshot())
        for button in tuple(self.pending_buttons):
            self._release_button(button)


def load_semantic_tas(trace_path, rom_path):
    with Path(trace_path).open(encoding="utf-8") as trace:
        header, *records = [json.loads(line) for line in trace if line.strip()]
    assert (header["format"], header["version"], header["game"]) == ("pyboy.semantic-pokemon-tas", 1, "POKEMON BLUE")
    assert header["rom_sha256"] == hashlib.sha256(Path(rom_path).read_bytes()).hexdigest(), "TAS ROM does not match"
    return header, records


def _distance(start, end):
    return sum(abs(b - a) for a, b in zip(start, end))


def _direction_to_position(start, target):
    dx, dy = target[0] - start[0], target[1] - start[1]
    if dx == 0 and dy:
        direction = "down" if dy > 0 else "up"
    elif dy == 0 and dx:
        direction = "right" if dx > 0 else "left"
    else:
        return None
    return direction


class PlaybackStopped(Exception):
    pass


class SemanticPokemonPlayback:
    def __init__(self, source_state, records, frame_skip):
        self.pyboy, self.records, self.source_state = source_state.pyboy, records, source_state
        self.frame_skip = frame_skip
        self.index = 0
        self.previous_action = None
        self.menu_context = None
        self.battle_completed = False
        self.after_battle = False
        self.wait_offset = None

    def state(self):
        return self.source_state.snapshot()

    def fail(self, message):
        state = self.state()
        raise RuntimeError(
            f"Record {self.index}: {message}; map {state['map_id']} at {state['position']} "
            f"in {state['scene']} (wait={state['generation']}, completed={state['completed']}, "
            f"waiting={state['waiting']})"
        )

    def wait(self, predicate, message, frames=300, interval=1):
        for _ in range(0, frames, interval):
            state = self.state()
            if predicate(state):
                return state
            if not self.pyboy.tick(interval, interval == 1, False):
                raise PlaybackStopped
        state = self.state()
        if not predicate(state):
            self.fail(f"timed out waiting for {message}")
        return state

    def next_transition(self, kind):
        for record in self.records[self.index :]:
            if record["record"] == "action":
                return None
            if record["kind"] == kind:
                return record
        return None

    def route_direction(self, target, blocked):
        current = self.state()["position"]
        walkable = (self.source_state.walkable_tiles() | {target}) - self.source_state.occupied_tiles() - blocked
        visited, pending = {current}, deque([(current, None)])
        while pending:
            point, first = pending.popleft()
            for direction, (dx, dy) in DIRECTION_DELTAS.items():
                neighbor = point[0] + dx, point[1] + dy
                if neighbor in walkable and neighbor not in visited:
                    if neighbor == target:
                        return first or direction
                    visited.add(neighbor)
                    pending.append((neighbor, first or direction))
        return None

    def walk_to(self, record, transition=None):
        map_id, target = record["map"]["id"], tuple(record["to"])
        start = self.state()["position"]
        blocked, leaving = set(), False
        exit_delta = tuple(b - a for a, b in zip(target, transition["position"])) if transition else None
        exit_direction = DELTA_DIRECTIONS.get(exit_delta, record.get("button"))
        for _ in range(10 * _distance(start, target) + 120):
            state = self.state()
            if transition is not None and state["map_id"] == transition["to_map"]:
                return
            if state["map_id"] != map_id:
                self.fail(f"unexpected map transition from {map_id}")
            if state["scene"] == "battle":
                self.battle()
                self.finish_dialogue()
                continue
            if state["scene"] != "overworld":
                return
            position = state["position"]
            if position == target:
                if transition is None:
                    return
                leaving = True
            direction = exit_direction if leaving else self.route_direction(target, blocked)
            if state["scripted"] or direction is None:
                blocked.clear()
                if not self.pyboy.tick(DEFAULT_ACTION_FRAME_SKIP, True, False):
                    raise PlaybackStopped
                continue
            self.pyboy.button(direction, 4)
            if not self.pyboy.tick(MOVEMENT_FRAMES, True, False):
                raise PlaybackStopped
            after = self.state()
            # A ledge jump can carry the player through a waypoint without stopping on it.
            crossed = _direction_to_position(position, after["position"]) == direction and (
                _distance(position, target) + _distance(target, after["position"])
                == _distance(position, after["position"])
            )
            if transition is None and after["map_id"] == map_id and crossed:
                return
            dx, dy = DIRECTION_DELTAS[direction]
            blocked = {(position[0] + dx, position[1] + dy)} if after["position"] == position else set()
        self.fail(f"could not walk from {start} to {target}")

    def refill_battle_resources(self):
        memory = self.pyboy.memory
        count = memory[PARTY_COUNT_ADDRESS]
        assert count <= PARTY_LENGTH, f"Invalid party count: {count}"
        mons = [
            (
                PARTY_MONS_ADDRESS + index * PARTY_MON_SIZE,
                PARTY_MON_HP_OFFSET,
                PARTY_MON_MAX_HP_OFFSET,
                PARTY_MON_MOVES_OFFSET,
                PARTY_MON_PP_OFFSET,
            )
            for index in range(count)
        ]
        # The active battle Pokémon is a separate copy of its party record.
        mons.append(
            (
                BATTLE_MON_ADDRESS,
                BATTLE_MON_HP_OFFSET,
                BATTLE_MON_MAX_HP_OFFSET,
                BATTLE_MON_MOVES_OFFSET,
                BATTLE_MON_PP_OFFSET,
            )
        )
        for address, hp, maximum, moves, pp in mons:
            maximum_hp = memory[address + maximum : address + maximum + 2]
            if any(maximum_hp) and memory[address + hp : address + hp + 2] != maximum_hp:
                memory[address + hp : address + hp + 2] = maximum_hp
            for index in range(4):
                value = 0xFF if memory[address + moves + index] else 0
                if memory[address + pp + index] != value:
                    memory[address + pp + index] = value

    def battle(self):
        for _ in range(6000):
            self.pyboy.button("a")
            for frame in range(10):
                self.refill_battle_resources()
                if not self.pyboy.tick():
                    raise PlaybackStopped
                if frame and self.state()["scene"] != "battle":
                    self.after_battle = True
                    return
        self.fail("battle did not finish")

    def finish_dialogue(self):
        quiet = 0
        for _ in range(1800):
            state = self.state()
            if state["waiting"]:
                quiet = 0
                self.pyboy.button("a")
                running = self.pyboy.tick(DEFAULT_ACTION_FRAME_SKIP)
            elif state["scene"] not in {"battle", "dialogue"} and not state["dialogue_open"]:
                quiet += 1
                if quiet >= 120:
                    return
                running = self.pyboy.tick()
            else:
                quiet = 0
                running = self.pyboy.tick()
            if not running:
                raise PlaybackStopped
        self.fail("dialogue did not settle after 1800 polls")

    def wait_for_text(self, record, generation=None, interval=10):
        def ready(state):
            if generation is not None:
                if state["waiting"] and state["generation"] == generation:
                    return True
                if state["generation"] > generation or state["completed"] == generation:
                    self.fail(f"dialogue wait {generation} already passed")
            elif state["waiting"] or (
                record.get("press_before_wait")
                and state["dialogue_open"]
                and record.get("press_before_wait_text_id", state["text_id"]) == state["text_id"]
            ):
                return True
            if state["scene"] != "dialogue" and not (state["scene"] == "battle" and state["dialogue_box"]):
                self.fail("dialogue closed before its A/B wait")
            return False

        self.wait(ready, f"dialogue A/B wait {generation}", frames=600, interval=interval)

    def advance_dialogue(self, record):
        state = self.state()
        active = state["scene"] == "dialogue" or state["scene"] == "battle" and state["dialogue_box"]
        if self.after_battle:
            if not active:
                self.pyboy.button(record["button"], record["press_frames"])
                if not self.pyboy.tick(max(self.frame_skip, record["press_frames"] + 1)):
                    raise PlaybackStopped
                return False
            record = {"button": record["button"], "press_frames": record["press_frames"], "ready": True}
        generation = record.get("accepted_wait_generation")
        recorded_generation = generation
        if generation is not None:
            if self.wait_offset is None:
                self.wait_offset = max(0, state["generation"] - generation)
            generation += self.wait_offset
            if state["completed"] < state["generation"]:
                generation = state["generation"]
                self.wait_offset = generation - recorded_generation
            if state["completed"] >= generation:
                return False
        pre_wait = None
        if record.get("press_before_wait"):
            for following in self.records[self.index :]:
                if following["record"] == "transition":
                    if following["kind"] == "scene" and following["to"] != "dialogue":
                        break
                else:
                    next_generation = following.get("accepted_wait_generation")
                    if (
                        following.get("action") == "advance"
                        and next_generation is not None
                        and next_generation - state["generation"] == 2
                    ):
                        pre_wait = next_generation - 1
                    break
        delay = record.get("delay_before_press_frames", 0)
        if delay and not self.pyboy.tick(delay, False, False):
            raise PlaybackStopped
        state = self.state()
        if generation is not None:
            if state["completed"] < state["generation"]:
                generation = state["generation"]
            elif generation > state["generation"] + 1:
                generation = state["generation"] + 1
            elif state["completed"] >= generation:
                return False
            self.wait_offset = generation - recorded_generation
        if (
            self.previous_action is not None
            and self.previous_action["action"] == "advance"
            and state["scene"] == "overworld"
            and not state["dialogue_open"]
        ):
            return False
        if state["scene"] != "dialogue" and not (state["scene"] == "battle" and state["dialogue_box"]):
            self.fail("expected dialogue to advance")
        button, press_frames = record["button"], record["press_frames"]
        if record["ready"]:
            next_scene = self.next_transition("scene")
            if (
                generation is not None
                and next_scene is not None
                and next_scene["from"] == "dialogue"
                and next_scene["to"] == "menu"
            ):
                if not (state["waiting"] and state["generation"] == generation):
                    self.pyboy.button_press(button)
                    try:
                        self.wait_for_text(record, generation, interval=1)
                    finally:
                        self.pyboy.button_release(button)
                    if not self.pyboy.tick():
                        raise PlaybackStopped
            self.wait_for_text(record, generation if generation is not None else pre_wait)
        self.pyboy.button(button, press_frames)
        if not self.pyboy.tick(max(self.frame_skip, press_frames + 1)):
            raise PlaybackStopped
        return True

    def resynchronize_map(self, from_map, to_map):
        for index in range(self.index, len(self.records)):
            record = self.records[index]
            if (
                record["record"] == "transition"
                and record["kind"] == "map"
                and (record["from_map"], record["to_map"]) == (from_map, to_map)
            ):
                self.index = index
                self.previous_action = None
                return
        self.fail(f"unexpected map transition from {from_map} to {to_map}")

    def map_transition(self, record):
        state = self.state()
        source, destination = record["from_map"], record["to_map"]
        if state["map_id"] not in (source, destination):
            self.resynchronize_map(source, state["map_id"])
            return
        previous = self.previous_action
        if state["map_id"] == source and previous is not None:
            if previous["action"] == "interact" and state["scene"] == "overworld":
                target = tuple(record["position"])
                direction = _direction_to_position(state["position"], target)
                if direction is not None and 0 < _distance(state["position"], target) <= 3:
                    self.walk_to({"map": {"id": source}, "to": target, "button": direction}, record)
            elif (
                previous["action"] == "walk"
                and previous["map"]["id"] == source
                and state["position"] != tuple(previous["to"])
            ):
                self.walk_to(previous, record)

        def arrived(state):
            if state["map_id"] == destination:
                return True
            if state["map_id"] != source:
                self.fail(f"unexpected map transition from {source}")
            if state["scene"] == "battle":
                self.battle()
                self.finish_dialogue()
            return False

        self.wait(arrived, f"map {destination}")
        if not self.pyboy.tick(DEFAULT_ACTION_FRAME_SKIP, True, False):
            raise PlaybackStopped

    def skip_wild_encounter(self):
        if self.state()["scene"] == "battle":
            self.battle()
            self.finish_dialogue()
        scene = "battle"
        for index in range(self.index, len(self.records)):
            record = self.records[index]
            if record["record"] == "transition":
                if record["kind"] != "scene" or record["from"] != scene:
                    self.index = index
                    break
                scene = record["to"]
                if scene == "overworld":
                    self.index = index + 1
                    break
            elif record["kind"] != scene:
                self.index = index
                break
        else:
            self.index = len(self.records)
        self.battle_completed = False
        self.menu_context = None

    def scene_transition(self, record):
        state = self.state()
        source, destination = record["from"], record["to"]
        next_record = self.records[self.index] if self.index < len(self.records) else {}
        dialogue_active = state["waiting"] or state["scene"] == "dialogue" and state["dialogue_open"]
        if source == "dialogue" and destination == "overworld" and next_record.get("record") == "transition":
            if (
                next_record["kind"] == "scene"
                and (next_record["from"], next_record["to"]) == ("overworld", "dialogue")
                and dialogue_active
            ):
                self.index += 1
                return
        if source == "battle":
            if state["scene"] == "battle":
                self.battle()
            self.battle_completed = self.after_battle = True
            state = self.state()
        if self.battle_completed:
            if destination == "battle" and state["scene"] != "battle":
                return
            if source == "battle" and destination == "dialogue" and state["scene"] not in {"battle", "dialogue"}:
                self.battle_completed = False
                return
        if self.menu_context is not None:
            start_scene, start_cursor, end_scene, end_cursor = self.menu_context
            if (
                start_scene == end_scene == "menu"
                and start_cursor is not None
                and end_cursor is not None
                and start_cursor != end_cursor
            ):
                scene = start_scene
                for index in range(self.index - 1, len(self.records)):
                    transition = self.records[index]
                    if (
                        transition["record"] != "transition"
                        or transition["kind"] != "scene"
                        or transition["map"]["id"] != record["map"]["id"]
                        or transition["from"] != scene
                    ):
                        break
                    scene = transition["to"]
                    if index >= self.index and scene == end_scene:
                        self.index = index + 1
                        return
        if source == "dialogue" and destination == "overworld" and dialogue_active:
            if self.after_battle:
                return
            previous_record = self.records[self.index - 2] if self.index > 1 else {}
            just_opened = (
                previous_record.get("record") == "transition"
                and previous_record.get("kind") == "scene"
                and previous_record.get("from") == "overworld"
                and previous_record.get("to") == "dialogue"
            )
            if (
                self.previous_action
                and self.previous_action["action"] == "advance"
                and next_record.get("action") in {"walk", "interact"}
                and not just_opened
            ):
                self.finish_dialogue()
                state = self.state()
        self.menu_context = None
        stable = int(state["scene"] == destination)
        timeout = 6000 if destination == "battle" else 300
        for elapsed in range(timeout + 1):
            matches = (
                state["dialogue_open"] or state["waiting"]
                if destination == "dialogue"
                else state["scene"] == destination
            )
            if matches and (destination in {"dialogue", "battle"} or stable >= SCENE_STABILITY_FRAMES):
                break
            if state["map_id"] != record["map"]["id"] or (
                state["scene"] == "menu" and destination not in {"menu", "dialogue", "battle"}
            ):
                break
            if elapsed == timeout:
                self.pyboy.button("a")
                if not self.pyboy.tick(60, False, False):
                    raise PlaybackStopped
                state = self.state()
                break
            if not self.pyboy.tick():
                raise PlaybackStopped
            state = self.state()
            stable = stable + 1 if state["scene"] == destination else 0
        if state["map_id"] != record["map"]["id"]:
            self.resynchronize_map(record["map"]["id"], state["map_id"])
        elif state["scene"] != destination and not (state["scene"] == "menu" and destination == "overworld"):
            if destination != "dialogue" or not (state["dialogue_open"] or state["waiting"]):
                self.fail(f"expected scene {destination}")
        if self.battle_completed and source == "battle" and destination != "battle":
            self.battle_completed = False

    def action(self, record):
        state = self.state()
        scene, action = record["kind"], record["action"]
        if scene == "battle" and (self.battle_completed or state["scene"] != "battle"):
            return
        delay = record.get("delay_before_press_frames", 0)
        if scene == "battle" and delay and not self.pyboy.tick(delay, False, False):
            raise PlaybackStopped
        state = self.state()
        map_id = record["map"]["id"]
        if state["map_id"] != map_id:
            self.fail(f"expected map {map_id}")
        if scene == "overworld" and state["scene"] == "battle":
            self.battle()
            self.battle_completed = True
            self.finish_dialogue()
            state = self.state()
        if (
            action == "face"
            and state["scene"] == "dialogue"
            and (self.next_transition("scene") or {}).get("to") == "dialogue"
        ):
            return
        expected = tuple(record.get("from", record.get("position")))
        if (
            action == "interact"
            and self.after_battle
            and state["scene"] == "overworld"
            and state["position"] != expected
        ):
            self.walk_to({"map": record["map"], "to": expected})
            state = self.state()
        start_state = state
        self.menu_context = None
        if (
            action == "interact"
            and state["scene"] == "dialogue"
            and (state["waiting"] or self.after_battle and state["dialogue_open"])
        ):
            record = {**record, "kind": "dialogue", "action": "advance", "ready": True}
            action = "advance"
        elif action == "interact" and state["scene"] == "dialogue" and state["dialogue_open"] and not self.after_battle:
            press = record["press_frames"]
            self.pyboy.button(record["button"], press)
            if not self.pyboy.tick(max(self.frame_skip, press + 1)):
                raise PlaybackStopped
            return
        if action == "advance":
            if not self.advance_dialogue(record):
                return
        elif action in {"walk", "face"}:
            if state["scene"] == "overworld":
                transition = self.next_transition("map")
                if action == "walk":
                    self.walk_to(record, transition)
                elif (
                    self.index < len(self.records)
                    and self.records[self.index].get("action") == "walk"
                    and self.records[self.index]["map"]["id"] == map_id
                    and tuple(self.records[self.index]["from"]) == expected
                ):
                    pass
                elif transition is not None:
                    self.walk_to(record, transition)
                else:
                    self.pyboy.button(record["button"], 3)
                    if not self.pyboy.tick(MOVEMENT_FRAMES, True, False):
                        raise PlaybackStopped
            elif state["scene"] == "menu":
                self.pyboy.button(record["button"])
                if not self.pyboy.tick(self.frame_skip):
                    raise PlaybackStopped
            else:
                self.fail(f"expected overworld {action}")
        elif action == "navigate":
            if state["scene"] != scene and not (scene == "menu" and state["scene"] == "dialogue"):
                self.fail(f"expected {scene} navigation")
            for _ in range(record["steps"]):
                self.pyboy.button(record["button"])
                if not self.pyboy.tick(self.frame_skip):
                    raise PlaybackStopped
        else:
            next_scene = self.next_transition("scene")
            if action == "back" and scene == "menu" and next_scene is not None and next_scene["to"] == "overworld":
                self.pyboy.button_press(record["button"])
                try:

                    def menu_closed(state):
                        if state["scene"] not in {"menu", "dialogue", "overworld"}:
                            self.fail("unexpected scene while closing menu")
                        return state["scene"] == "overworld"

                    self.wait(menu_closed, "menu to close")
                finally:
                    self.pyboy.button_release(record["button"])
                if not self.pyboy.tick():
                    raise PlaybackStopped
            else:
                deferred_back = (
                    action == "back"
                    and scene == "overworld"
                    and state["scene"] == "dialogue"
                    and state["dialogue_open"]
                )
                if (
                    state["scene"] != scene
                    and not (scene == "menu" and state["scene"] == "dialogue")
                    and not deferred_back
                ):
                    self.fail(f"expected {scene} action {action}")
                press = record["press_frames"]
                if scene == "menu" and action in {"back", "cancel"}:
                    press = min(press, 4)
                if action == "interact":
                    press = max(press, 10)
                    facing = record.get("facing")
                    if facing in DIRECTION_DELTAS and state["facing"] != facing:
                        self.pyboy.button(facing, 3)
                        if not self.pyboy.tick(MOVEMENT_FRAMES, True, False):
                            raise PlaybackStopped
                self.pyboy.button(record["button"], press)
                if not self.pyboy.tick(max(self.frame_skip, press + 1)):
                    raise PlaybackStopped
        if self.after_battle and scene == "overworld" and action == "interact":
            self.after_battle = False
        self.previous_action = record
        if scene == "menu" and action == "confirm":
            end_state = self.state()
            self.menu_context = (
                start_state["scene"],
                start_state["menu_cursor"],
                end_state["scene"],
                end_state["menu_cursor"],
            )

    def run(self):
        try:
            if not self.pyboy.tick():
                return False
            while self.index < len(self.records):
                record = self.records[self.index]
                self.index += 1
                if record["record"] == "action":
                    self.action(record)
                elif record["kind"] == "map":
                    self.map_transition(record)
                elif record["kind"] == "scene":
                    if record["from"] == "overworld" and record["to"] == "battle" and record.get("opponent_id") == 0:
                        self.skip_wild_encounter()
                    else:
                        self.scene_transition(record)
                else:
                    self.fail(f"unknown transition {record['kind']}")
            if self.battle_completed:
                self.finish_dialogue()
            return True
        except PlaybackStopped:
            return False


@contextmanager
def pokemon_session(
    rom_path, timer_div, window="null", symbols_path=Path("test_roms/pokered/pokeblue.sym"), no_input=False
):
    with ExitStack() as cleanup:
        pyboy = PyBoy(
            rom_path,
            ram_file=io.BytesIO(bytes(0x8000)),
            window=window,
            sound_volume=0,
            symbols=str(symbols_path),
            no_input=no_input,
        )
        cleanup.callback(pyboy.stop, save=False)
        assert pyboy.cartridge_title == "POKEMON BLUE"
        source = PokemonBlueState(pyboy)
        cleanup.callback(source.close)
        pyboy.set_emulation_speed(0 if window == "null" else 1)
        pyboy.game_wrapper.start_game(timer_div=timer_div)
        yield source


def record_main():
    from pyboy.plugins.window_sdl2 import sdl2_event_pump

    rom_path = Path("ROMs/POKEMON BLUE.gb")
    output_path = Path("pokemon-blue.semantic.jsonl")
    timer_div = 0
    with pokemon_session(rom_path, timer_div, window="SDL2", no_input=True) as source:
        pyboy = source.pyboy
        with output_path.open("x", encoding="utf-8") as output:
            output.write(
                json.dumps(
                    {
                        "record": "session",
                        "format": "pyboy.semantic-pokemon-tas",
                        "version": 1,
                        "game": pyboy.cartridge_title,
                        "rom_sha256": hashlib.sha256(rom_path.read_bytes()).hexdigest(),
                        "startup": {"timer_div": timer_div},
                        "frame_skip": DEFAULT_ACTION_FRAME_SKIP,
                    }
                )
                + "\n"
            )
            recorder = SemanticPokemonRecorder(source, output)
            try:
                while True:
                    events = sdl2_event_pump([])
                    for event in events:
                        pyboy.send_input(event)
                    if not pyboy.tick():
                        break
                    state = source.snapshot()
                    recorder.capture_input_events(events, recorder.previous_state, state)
                    recorder.observe(state)
                    recorder.frame_index += 1
            finally:
                recorder.close()


def play_main(
    trace_path=Path("pokemon-blue.semantic.jsonl"),
    rom_path=Path("ROMs/POKEMON BLUE.gb"),
    window="SDL2",
):
    header, records = load_semantic_tas(trace_path, rom_path)
    with pokemon_session(rom_path, header["startup"]["timer_div"], window=window) as source:
        return SemanticPokemonPlayback(source, records, header["frame_skip"]).run()


def test_pokemon_tas_waypoints():
    state = {"scene": "overworld", "map_id": 0, "position": (5, 6), "menu_cursor": None}
    moving = 1
    source = SimpleNamespace(snapshot=lambda: state, read=lambda _: moving)
    output = io.StringIO()
    recorder = SemanticPokemonRecorder(source, output)
    recorder.capture_input_events([WindowEvent.PRESS_ARROW_RIGHT], state, state)
    for x in (6, 7, 8):
        state = {**state, "position": (x, 6)}
        recorder.observe(state)
        recorder.frame_index += 1
    assert not output.getvalue()
    moving = 0
    recorder.observe(state)
    recorded = output.getvalue()
    waypoint = json.loads(recorded)
    assert (waypoint["action"], waypoint["from"], waypoint["to"]) == ("walk", [5, 6], [8, 6])
    recorder.capture_input_events([WindowEvent.RELEASE_ARROW_RIGHT], state, state)
    recorder.close()
    assert output.getvalue() == recorded


@pytest.mark.benchmark(group="pgo-pokemon-tas")
def test_pgo_pokemon_tas(pokemon_blue_rom, pgo_pokemon_blue_trace, pokemon_blue_symbols, capsys):
    header, records = load_semantic_tas(pgo_pokemon_blue_trace, pokemon_blue_rom)
    with pokemon_session(pokemon_blue_rom, header["startup"]["timer_div"], symbols_path=pokemon_blue_symbols) as source:
        assert SemanticPokemonPlayback(source, records, header["frame_skip"]).run()
        capsys.readouterr()
