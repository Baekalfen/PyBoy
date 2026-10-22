#!/usr/bin/env python3

import argparse
import base64
import binascii
import hashlib
import io
import json
import statistics
import time
import zlib
from pathlib import Path

from pyboy import PyBoy
from pyboy.utils import WindowEvent, cython_compiled

REPLAY_EVENT_FILTER = {
    WindowEvent.PRESS_SPEED_UP,
    WindowEvent.RELEASE_SPEED_UP,
    WindowEvent.SCREEN_RECORDING_TOGGLE,
    WindowEvent.SCREEN_RECORDING_TOGGLE_MP4,
    WindowEvent._INTERNAL_RENDERER_FLUSH,
}


def load_replay(rom_path, replay_path):
    try:
        payload = json.loads(zlib.decompress(Path(replay_path).read_bytes()).decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError, zlib.error) as exc:
        raise ValueError(f"Invalid replay file: {replay_path}") from exc

    if not isinstance(payload, list) or len(payload) != 3:
        raise ValueError(f"Replay must contain input events, ROM hash, and initial state: {replay_path}")

    events, expected_rom_hash, encoded_state = payload
    actual_rom_hash = base64.b64encode(hashlib.sha256(Path(rom_path).read_bytes()).digest()).decode("ascii")
    if actual_rom_hash != expected_rom_hash:
        raise ValueError(f"Replay ROM hash does not match {rom_path}")

    if not isinstance(events, list) or not events:
        raise ValueError(f"Replay contains no input events: {replay_path}")

    last_frame = -1
    for index, event in enumerate(events):
        if not isinstance(event, list) or len(event) < 2:
            raise ValueError(f"Invalid event {index} in replay: {replay_path}")
        frame, inputs = event[:2]
        if not isinstance(frame, int) or isinstance(frame, bool) or frame < 0 or frame < last_frame:
            raise ValueError(f"Invalid or unordered frame in event {index} of replay: {replay_path}")
        if not isinstance(inputs, list) or any(not isinstance(key, int) for key in inputs):
            raise ValueError(f"Invalid input list in event {index} of replay: {replay_path}")
        last_frame = frame

    if encoded_state is None:
        initial_state = None
    else:
        try:
            initial_state = base64.b64decode(encoded_state, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError(f"Invalid initial state in replay: {replay_path}") from exc

    return events, initial_state, last_frame + 1


def discover_replays(rom_dir):
    rom_dir = Path(rom_dir)
    return sorted(replay for replay in rom_dir.rglob("*.replay") if replay.with_suffix("").is_file())


def play_replay(pyboy, events, frame_count, render_every):
    if render_every is not None and render_every < 1:
        raise ValueError("render_every must be positive or None")

    event_index = 0
    frame = 0
    while frame < frame_count:
        while event_index < len(events) and events[event_index][0] == frame:
            for event in events[event_index][1]:
                if event not in REPLAY_EVENT_FILTER:
                    pyboy.send_input(event)
            event_index += 1

        next_event_frame = events[event_index][0] if event_index < len(events) else frame_count
        if render_every is None:
            next_render_frame = frame_count
        else:
            next_render_frame = min(frame_count, (frame // render_every + 1) * render_every)
        next_frame = min(frame_count, next_event_frame, next_render_frame)
        tick_count = next_frame - frame
        render = render_every is not None and (next_frame == frame_count or next_frame % render_every == 0)

        if not pyboy.tick(tick_count, render, False):
            raise RuntimeError(f"PyBoy stopped during replay at frame {frame}")
        frame = next_frame


def benchmark_replay(
    rom_path, events, initial_state, frame_count, runs, iterations, fast_mode, render_every, bootrom=None
):
    samples = []
    state_hashes = []

    for _ in range(runs):
        pyboy = PyBoy(rom_path, window="null", sound_emulated=False, fast_mode=fast_mode, bootrom=bootrom)
        try:
            pyboy.set_emulation_speed(0)
            if initial_state is not None:
                pyboy.load_state(io.BytesIO(initial_state))

            reset_state = io.BytesIO()
            pyboy.save_state(reset_state)
            reset_state = reset_state.getvalue()

            elapsed = 0.0
            for iteration in range(iterations):
                if iteration:
                    pyboy.load_state(io.BytesIO(reset_state))

                started = time.perf_counter()
                play_replay(pyboy, events, frame_count, render_every)
                elapsed += time.perf_counter() - started

                final_state = io.BytesIO()
                pyboy.save_state(final_state)
                state_hashes.append(hashlib.sha256(final_state.getvalue()).hexdigest())

            samples.append(elapsed)
        finally:
            pyboy.stop(save=False)

    median_seconds = statistics.median(samples)
    return {
        "runs": runs,
        "iterations_per_run": iterations,
        "sample_seconds": samples,
        "median_seconds_per_playback": median_seconds / iterations,
        "median_frames_per_second": frame_count * iterations / median_seconds,
        "final_state_sha256": sorted(set(state_hashes)),
        "repeatable_final_state": len(set(state_hashes)) == 1,
        "fast_mode": fast_mode,
        "render": render_every is not None,
        "render_every": render_every,
        "bootrom": None if bootrom is None else str(bootrom),
        "cython_compiled": cython_compiled,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Benchmark deterministic PyBoy input replay traces.")
    parser.add_argument("--rom-dir", type=Path, default=Path("ROMs"), help="Directory to scan for paired .replay files")
    parser.add_argument(
        "--replay",
        type=Path,
        action="append",
        help="Replay file to benchmark; defaults to all replays paired with ROMs under --rom-dir",
    )
    parser.add_argument("--runs", type=int, default=3, help="Independent PyBoy instances to benchmark")
    parser.add_argument(
        "--iterations", type=int, default=10, help="Replays per instance, each from the same saved state"
    )
    parser.add_argument("--fast-mode", action="store_true", help="Enable PyBoy's lower-accuracy fast mode")
    parser.add_argument("--bootrom", type=Path, help="Boot ROM file to use for recorded boot-time inputs")
    parser.add_argument("--render", action="store_true", help="Render every frame while replaying")
    parser.add_argument(
        "--render-every",
        type=int,
        default=0,
        help="Render every N frames (0 disables rendering); --render is equivalent to --render-every 1",
    )
    args = parser.parse_args(argv)

    if args.runs < 1:
        parser.error("--runs must be at least 1")
    if args.iterations < 1:
        parser.error("--iterations must be at least 1")
    if args.render_every < 0:
        parser.error("--render-every must be non-negative")
    if args.render and args.render_every:
        parser.error("Use either --render or --render-every, not both")
    render_every = 1 if args.render else (args.render_every or None)

    replay_paths = args.replay if args.replay is not None else discover_replays(args.rom_dir)
    if not replay_paths:
        parser.error(f"No paired .replay files found under {args.rom_dir}")

    for replay_path in replay_paths:
        rom_path = replay_path.with_suffix("")
        if not rom_path.is_file():
            parser.error(f"Replay has no adjacent ROM file: {replay_path}")
        events, initial_state, frame_count = load_replay(rom_path, replay_path)
        result = benchmark_replay(
            str(rom_path),
            events,
            initial_state,
            frame_count,
            args.runs,
            args.iterations,
            args.fast_mode,
            render_every,
            args.bootrom,
        )
        result.update(
            {
                "rom": str(rom_path),
                "replay": str(replay_path),
                "frames_per_playback": frame_count,
                "input_events": len(events),
            }
        )
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
